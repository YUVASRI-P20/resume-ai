"""
Roadmap and knowledge graph services.

Knowledge graph mastery is computed from REAL interview evaluations and coding
submissions per topic — never seeded with fake values. The roadmap is a
PERSONALIZED 15-DAY plan generated from:
  1. the candidate's actual resume skills,
  2. the target job's real requirements the resume does not show evidence for,
  3. knowledge gaps recorded during interviews,
  4. coding test results,
prioritizing weak areas first. With GEMINI_API_KEY set, Gemini drafts the day
plan from this real data; without it, a deterministic plan is built from the
same real weaknesses. Every roadmap is stored in PostgreSQL.
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.roadmap import (
    KnowledgeNode,
    KnowledgeEdge,
    LearningRoadmap,
    RoadmapWeek,
    RoadmapTask,
    LearningProgress,
    NodeStatus,
    TaskPriority,
)
from app.models.feedback import KnowledgeGap

logger = logging.getLogger(__name__)

ROADMAP_DAYS = 15


class RoadmapService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _call_gemini(self, prompt: str) -> Optional[dict]:
        if not settings.GEMINI_API_KEY:
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception as e:  # noqa: BLE001
            logger.error("Gemini roadmap error: %s", e)
            return None

    # ------------------------------------------------------------------ #
    # Knowledge graph — computed from REAL user performance
    # ------------------------------------------------------------------ #
    async def get_knowledge_graph(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Build the graph from the user's actual interview evaluations and
        coding submissions. Topics with no real data are simply absent —
        no placeholder nodes are invented."""
        from collections import defaultdict

        from app.models.interview import (
            Interview,
            InterviewQuestion,
            InterviewAnswer,
            InterviewEvaluation,
        )
        from app.models.coding import CodingQuestion, CodingSubmission, CodeExecution

        topic_scores: Dict[str, List[float]] = defaultdict(list)

        rows = await self.db.execute(
            select(InterviewQuestion, InterviewEvaluation)
            .join(InterviewAnswer, InterviewQuestion.id == InterviewAnswer.question_id)
            .join(InterviewEvaluation, InterviewAnswer.id == InterviewEvaluation.answer_id)
            .join(Interview, InterviewQuestion.interview_id == Interview.id)
            .filter(Interview.user_id == user_id)
        )
        for q, e in rows.all():
            # Attribute the score to the topic actually asked about: the
            # question's role-domain plus key resume-skill terms in the text.
            topics = set()
            if q.question_type:
                topics.add(q.question_type.title())
            for term in (q.expected_key_points or "").split(","):
                term = term.strip()
                if term and len(term) < 60:
                    topics.add(term)
            if not topics:
                topics.add(q.domain or "General")
            for t in topics:
                topic_scores[t].append(e.score)

        coding_rows = await self.db.execute(
            select(CodingQuestion, CodeExecution)
            .join(CodingSubmission, CodeExecution.submission_id == CodingSubmission.id)
            .join(CodingQuestion, CodingSubmission.question_id == CodingQuestion.id)
            .filter(CodingSubmission.user_id == user_id)
        )
        for question, execution in coding_rows.all():
            domain = question.domain or "Algorithms"
            if execution.total_tests > 0:
                topic_scores[domain].append(execution.passed_tests / execution.total_tests * 100.0)

        nodes_res = await self.db.execute(select(KnowledgeNode).filter(KnowledgeNode.user_id == user_id))
        existing = {n.topic_name: n for n in nodes_res.scalars().all()}

        # Upsert nodes from real data.
        for topic, scores in topic_scores.items():
            mastery = round(sum(scores) / len(scores), 1)
            if mastery >= 75:
                status, is_strength, is_weakness = NodeStatus.MASTERED, True, False
            elif mastery >= 50:
                status, is_strength, is_weakness = NodeStatus.IN_PROGRESS, False, False
            else:
                status, is_strength, is_weakness = NodeStatus.WEAK, False, True

            node = existing.get(topic)
            if node is None:
                node = KnowledgeNode(user_id=user_id, topic_name=topic, category="Performance")
                self.db.add(node)
                existing[topic] = node
            node.mastery_score = mastery
            node.status = status
            node.is_strength = is_strength
            node.is_weakness = is_weakness
        await self.db.commit()

        nodes = list(existing.values())
        # Edges: a deterministic topic-similarity link within the same category.
        edges_res = await self.db.execute(select(KnowledgeEdge).filter(KnowledgeEdge.user_id == user_id))
        edge_pairs = {(e.parent_node_id, e.child_node_id) for e in edges_res.scalars().all()}
        by_id = {n.id: n for n in nodes}
        for a in nodes:
            for b in nodes:
                if a.id != b.id and a.category == b.category and (a.id, b.id) not in edge_pairs:
                    self.db.add(KnowledgeEdge(user_id=user_id, parent_node_id=a.id, child_node_id=b.id))
                    edge_pairs.add((a.id, b.id))
        await self.db.commit()

        edges_res = await self.db.execute(select(KnowledgeEdge).filter(KnowledgeEdge.user_id == user_id))
        edges = edges_res.scalars().all()

        return {
            "nodes": [
                {
                    "id": str(n.id),
                    "topic_name": n.topic_name,
                    "category": n.category,
                    "mastery_score": n.mastery_score,
                    "status": n.status.value,
                    "is_strength": n.is_strength,
                    "is_weakness": n.is_weakness,
                }
                for n in nodes
            ],
            "edges": [
                {
                    "id": str(e.id),
                    "parent_node_id": str(e.parent_node_id),
                    "child_node_id": str(e.child_node_id),
                }
                for e in edges
            ],
        }

    # ------------------------------------------------------------------ #
    # Personalized 15-day roadmap
    # ------------------------------------------------------------------ #
    async def _collect_user_context(self, user_id: uuid.UUID) -> dict[str, Any]:
        """Gather the user's real data that drives the roadmap."""
        from app.models.interview import (
            Interview,
            InterviewQuestion,
            InterviewAnswer,
            InterviewEvaluation,
        )
        from app.models.coding import CodingQuestion, CodingSubmission, CodeExecution
        from app.resume.models.resume import Resume
        from app.models.company import RoleMatchResult

        # Resume skills (actual extraction)
        resume_row = (
            await self.db.execute(
                select(Resume)
                .where(Resume.user_id == user_id, Resume.is_active.is_(True))
                .order_by(Resume.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        resume_skills: List[str] = []
        resume_id = None
        target_company = target_role = None
        missing_requirements: List[str] = []
        if resume_row:
            resume_id = resume_row.id
            resume_skills = [s.name for s in (resume_row.skills or [])]

        # Latest role match gaps (real job requirements with weak/missing status)
        match = (
            await self.db.execute(
                select(RoleMatchResult)
                .where(RoleMatchResult.user_id == user_id)
                .order_by(RoleMatchResult.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if match:
            from app.models.company import Company, JobRole

            company = await self.db.get(Company, match.company_id)
            role = await self.db.get(JobRole, match.job_role_id)
            if isinstance(company, Company):
                target_company = company.name
            if isinstance(role, JobRole):
                target_role = role.title
            missing_requirements = list(match.requirements_missing or [])

        # Weak topics from actual interview evaluations
        weak_rows = await self.db.execute(
            select(InterviewQuestion, InterviewEvaluation)
            .join(InterviewAnswer, InterviewQuestion.id == InterviewAnswer.question_id)
            .join(InterviewEvaluation, InterviewAnswer.id == InterviewEvaluation.answer_id)
            .join(Interview, InterviewQuestion.interview_id == Interview.id)
            .filter(Interview.user_id == user_id, InterviewEvaluation.score < 70)
            .order_by(InterviewEvaluation.score.asc())
        )
        weak_topics: List[dict[str, Any]] = []
        for q, e in weak_rows.all():
            weak_topics.append(
                {"topic": (e.knowledge_gap or q.question_text[:80]), "score": e.score, "feedback": e.feedback}
            )

        # Knowledge gaps recorded during feedback generation
        gaps = (
            await self.db.execute(
                select(KnowledgeGap).filter(KnowledgeGap.user_id == user_id).order_by(KnowledgeGap.created_at.desc())
            )
        ).scalars().all()
        gap_topics = [{"topic": g.topic, "description": g.description, "severity": g.severity.value} for g in gaps]

        # Coding mistakes (real submission outcomes)
        coding_rows = await self.db.execute(
            select(CodingQuestion, CodeExecution)
            .join(CodingSubmission, CodeExecution.submission_id == CodingSubmission.id)
            .join(CodingQuestion, CodingSubmission.question_id == CodingQuestion.id)
            .filter(CodingSubmission.user_id == user_id)
            .order_by(CodeExecution.created_at.desc())
            .limit(10)
        )
        coding_results = [
            {
                "domain": q.domain,
                "title": q.title,
                "passed": f"{e.passed_tests}/{e.total_tests}",
                "status": e.execution_status,
                "error": (e.error_message or "")[:200],
            }
            for q, e in coding_rows.all()
        ]

        return {
            "resume_skills": resume_skills,
            "target_company": target_company,
            "target_role": target_role,
            "missing_job_requirements": missing_requirements,
            "weak_interview_topics": weak_topics,
            "knowledge_gaps": gap_topics,
            "coding_results": coding_results,
        }

    async def generate_roadmap(self, user_id: uuid.UUID, interview_id: Optional[uuid.UUID] = None) -> LearningRoadmap:
        """Generate (or return the existing) personalized 15-day roadmap."""
        existing_res = await self.db.execute(select(LearningRoadmap).filter(LearningRoadmap.user_id == user_id))
        existing = existing_res.scalars().first()
        if existing:
            return existing

        context = await self._collect_user_context(user_id)

        weak_names = [w["topic"] for w in context["weak_interview_topics"]]
        gap_names = [g["topic"] for g in context["knowledge_gaps"]]
        missing_reqs = context["missing_job_requirements"]

        priority_list = (weak_names + gap_names + missing_reqs)[:10]

        prompt = f"""Create a PERSONALIZED 15-day interview improvement roadmap.
Base every day strictly on the candidate data below — no generic filler days.

CANDIDATE DATA:
- Resume skills (actually extracted): {json.dumps(context["resume_skills"])}
- Target: {context["target_role"] or "not selected"} at {context["target_company"] or "not selected"}
- Job requirements with weak/missing resume evidence: {json.dumps(missing_reqs)}
- Interview topics scored below 70: {json.dumps(weak_names)}
- Recorded knowledge gaps: {json.dumps(gap_names)}
- Coding test results: {json.dumps(context["coding_results"])}

Return a JSON object:
{{
  "title": "string",
  "summary": "string explaining why these topics were chosen",
  "days": [
    {{
      "day_number": 1,
      "topic": "string",
      "what_to_study": "string",
      "why_important": "string",
      "practice_task": "string",
      "interview_questions_to_practice": ["string", "string"],
      "priority": "Low|Medium|High|Critical",
      "difficulty": "Easy|Medium|Hard",
      "resources": ["string"]
    }}
  ]  // exactly 15 items, day_number 1..15
}}
Prioritize the weakest/most-missing topics early; end with a full mock interview + coding assessment on day 15."""

        ai_data = await self._call_gemini(prompt)
        days: List[dict[str, Any]]
        if ai_data and isinstance(ai_data.get("days"), list) and ai_data["days"]:
            days = ai_data["days"][:ROADMAP_DAYS]
        else:
            days = self._deterministic_days(context, priority_list)

        roadmap = LearningRoadmap(
            user_id=user_id,
            title=str(ai_data.get("title", "15-Day Personalized Improvement Plan")) if ai_data else "15-Day Personalized Improvement Plan",
            summary=str(ai_data.get("summary", "Built from your interview results, coding outcomes and job-fit gaps.")) if ai_data else "Built from your interview results, coding outcomes and job-fit gaps.",
            total_weeks=3,  # 15 days = ~3 weeks of study
            completion_percentage=0.0,
        )
        self.db.add(roadmap)
        await self.db.commit()
        await self.db.refresh(roadmap)

        # Persist as weeks of 7 days (schema constraint), keeping day numbers 1..15.
        total_tasks_count = 0
        for week_index in range(0, (len(days) + 6) // 7):
            week_days = days[week_index * 7 : (week_index + 1) * 7]
            if not week_days:
                continue
            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=week_index + 1,
                theme=f"Days {week_index * 7 + 1}\u2013{min((week_index + 1) * 7, len(days))}",
                objectives=", ".join(d.get("topic", "Practice") for d in week_days[:3]),
            )
            self.db.add(week)
            await self.db.commit()
            await self.db.refresh(week)

            for d in week_days:
                total_tasks_count += 1
                try:
                    priority = TaskPriority(d.get("priority", "Medium"))
                except ValueError:
                    priority = TaskPriority.MEDIUM
                self.db.add(
                    RoadmapTask(
                        week_id=week.id,
                        day_number=int(d.get("day_number", total_tasks_count)),
                        task_title=str(d.get("topic", f"Day {total_tasks_count}"))[:200],
                        description="\n".join(
                            filter(
                                None,
                                [
                                    f"What to study: {d.get('what_to_study', '')}",
                                    f"Why it matters: {d.get('why_important', '')}",
                                    f"Practice task: {d.get('practice_task', '')}",
                                    "Interview questions to practice:",
                                    *[f"- {q}" for q in (d.get("interview_questions_to_practice") or [])[:3]],
                                ],
                            )
                        ),
                        study_time_hours=2.0,
                        priority=priority,
                        difficulty=str(d.get("difficulty", "Medium")),
                        resources=list(d.get("resources", []) or []),
                        is_completed=False,
                    )
                )

        # Init learning progress
        progress_res = await self.db.execute(select(LearningProgress).filter(LearningProgress.user_id == user_id))
        progress = progress_res.scalars().first()
        if progress is None:
            progress = LearningProgress(user_id=user_id)
            self.db.add(progress)
        progress.total_tasks = total_tasks_count
        progress.completed_tasks = 0
        await self.db.commit()

        return roadmap

    def _deterministic_days(self, context: dict[str, Any], priority_list: List[str]) -> List[dict[str, Any]]:
        """Build the 15-day plan directly from the user's real weaknesses."""
        days: List[dict[str, Any]] = []
        pool = [p for p in priority_list if p]
        skills = context["resume_skills"] or []

        # Days 1..10: rotate through the user's actual weak topics.
        for i in range(10):
            topic = pool[i % len(pool)] if pool else (skills[i % len(skills)] if skills else "Core problem solving")
            focus = (
                context["weak_interview_topics"][i]["feedback"][:150]
                if i < len(context["weak_interview_topics"])
                else "Structured revision and hands-on practice."
            )
            days.append(
                {
                    "day_number": i + 1,
                    "topic": f"{topic} \u2014 focused revision",
                    "what_to_study": f"Core concepts of {topic}; review the exact points missed in your interview ({focus}).",
                    "why_important": f"This topic appeared in your interview results or job requirements with weak evidence.",
                    "practice_task": f"Complete 2 practice exercises on {topic} and write a short summary of key takeaways.",
                    "interview_questions_to_practice": [
                        f"Explain how you used {topic} in a project.",
                        f"What are the most common pitfalls when working with {topic}?",
                    ],
                    "priority": "Critical" if i < 3 else "High" if i < 7 else "Medium",
                    "difficulty": "Medium",
                    "resources": [],
                }
            )

        # Days 11..12: coding, grounded in the user's real coding outcomes.
        coding_domains = sorted({c["domain"] for c in context["coding_results"] if c.get("domain")}) or ["Python"]
        for j, i in enumerate((11, 12)):
            domain = coding_domains[j % len(coding_domains)]
            days.append(
                {
                    "day_number": i,
                    "topic": f"{domain} coding practice",
                    "what_to_study": ("Timed " + domain + " problems; review your failed submissions: "
                    + "; ".join(f"{c['title']} ({c['status']})" for c in context["coding_results"][:3]))
                    or f"Timed {domain} problems.",
                    "why_important": "Your coding test outcomes feed directly into your overall readiness.",
                    "practice_task": f"Solve 3 timed {domain} problems focusing on correctness first, then optimize.",
                    "interview_questions_to_practice": ["Walk through your solution's time and space complexity."],
                    "priority": "High",
                    "difficulty": "Hard",
                    "resources": [],
                }
            )

        # Days 13..14: missing job requirements (real gaps).
        missing = context["missing_job_requirements"]
        for k, i in enumerate((13, 14)):
            req = missing[k] if k < len(missing) else (missing[0] if missing else f"{skills[0] if skills else 'System design'} deep dive")
            days.append(
                {
                    "day_number": i,
                    "topic": f"{req} \u2014 closing the job gap",
                    "what_to_study": f"Build working knowledge of {req}, which is required by your target role but not evidenced in your resume.",
                    "why_important": "Your resume shows no evidence for this job requirement yet.",
                    "practice_task": f"Complete a small hands-on project or exercise using {req} and document what you built.",
                    "interview_questions_to_practice": [f"Describe a scenario where you would apply {req}."],
                    "priority": "High",
                    "difficulty": "Medium",
                    "resources": [],
                }
            )

        # Day 15: full mock.
        days.append(
            {
                "day_number": 15,
                "topic": "Full mock interview + coding assessment",
                "what_to_study": "Run a complete InterviewIQ AI interview plus a timed coding test covering your previously weak topics.",
                "why_important": "Verifies the improvement across all previously identified weaknesses.",
                "practice_task": "Complete a full mock session on InterviewIQ and compare your scores with your baseline.",
                "interview_questions_to_practice": [f"Any question from days 1\u201314 on {p}" for p in pool[:3]],
                "priority": "Critical",
                "difficulty": "Hard",
                "resources": [],
            }
        )
        return days

    async def update_task_completion(self, task_id: uuid.UUID, user_id: uuid.UUID, is_completed: bool) -> RoadmapTask:
        task = await self.db.get(RoadmapTask, task_id)
        if not task:
            raise AppException(status_code=404, detail="Task not found.")

        # Ensure the task belongs to this user's roadmap.
        week = await self.db.get(RoadmapWeek, task.week_id)
        roadmap = await self.db.get(LearningRoadmap, week.roadmap_id) if week else None
        if roadmap is None or roadmap.user_id != user_id:
            raise AppException(status_code=404, detail="Task not found.")

        task.is_completed = is_completed
        await self.db.commit()
        await self.db.refresh(task)

        # Update progress summary
        progress_res = await self.db.execute(select(LearningProgress).filter(LearningProgress.user_id == user_id))
        progress = progress_res.scalars().first()
        if progress:
            all_tasks_res = await self.db.execute(
                select(RoadmapTask).join(RoadmapWeek, RoadmapTask.week_id == RoadmapWeek.id).filter(RoadmapWeek.roadmap_id == roadmap.id)
            )
            all_tasks = all_tasks_res.scalars().all()
            completed = sum(1 for t in all_tasks if t.is_completed)
            progress.completed_tasks = completed
            progress.total_tasks = len(all_tasks)
            roadmap.completion_percentage = (completed / len(all_tasks) * 100.0) if all_tasks else 0.0
            await self.db.commit()

        return task

    async def regenerate_roadmap(self, user_id: uuid.UUID) -> LearningRoadmap:
        # Delete existing roadmap and rebuild from the latest performance data.
        existing_res = await self.db.execute(select(LearningRoadmap).filter(LearningRoadmap.user_id == user_id))
        existing = existing_res.scalars().first()
        if existing:
            await self.db.delete(existing)
            await self.db.commit()

        return await self.generate_roadmap(user_id)
