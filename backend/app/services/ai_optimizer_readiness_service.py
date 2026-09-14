import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class AIOptimizerReadinessService:
    @classmethod
    def _require_ai(cls) -> None:
        """Raise a clear error when AI is not configured — never silently
        return fabricated optimization/readiness data."""
        if genai is None or not GEMINI_API_KEY:
            raise RuntimeError(
                "AI analysis is temporarily unavailable. Please configure GEMINI_API_KEY and try again."
            )

    @classmethod
    def optimize_resume(cls, resume_text: str, target_role: str, target_company: Optional[str] = None, job_description: Optional[str] = None) -> Dict[str, Any]:
        company_str = target_company or "General"
        jd_str = job_description or "None provided"
        prompt = f"""
You are an expert ATS and Resume Optimization AI engine.
Analyze the following resume for the target role: "{target_role}"
Target Company: {company_str}
Job Description: {jd_str}

Resume Content:
{resume_text}

Provide a comprehensive optimization analysis in valid JSON format matching this exact schema:
{{
    "overall_score": 82.5,
    "ats_score": 85.0,
    "role_match_score": 80.0,
    "summary_optimization": {{
        "original": "...",
        "optimized": "...",
        "reason": "..."
    }},
    "experience_optimizations": [
        {{
            "original": "...",
            "optimized": "...",
            "reason": "..."
        }}
    ],
    "project_optimizations": [
        {{
            "title": "...",
            "original_description": "...",
            "optimized_description": "...",
            "technical_impact": "...",
            "reason": "..."
        }}
    ],
    "skill_optimization": {{
        "existing_skills": ["Python", "FastAPI"],
        "strong_skills": ["Python"],
        "missing_role_relevant_skills": ["Docker", "Kubernetes"],
        "missing_keywords": ["REST APIs", "CI/CD"],
        "recommended_skills_to_learn": ["Docker"]
    }},
    "ats_analysis": {{
        "ats_score": 85.0,
        "keyword_coverage_percentage": 75.0,
        "missing_keywords": ["Docker", "CI/CD"],
        "formatting_warnings": [],
        "section_completeness": {{"summary": True, "experience": True, "education": True}},
        "skill_alignment": 80.0,
        "role_alignment": 82.0
    }},
    "company_match": {{
        "company_name": "{company_str}",
        "resume_compatibility_score": 80.0,
        "role_match_score": 82.0,
        "matching_areas": ["Backend development", "Python experience"],
        "missing_areas": ["Cloud deployment at scale"],
        "recommendations": ["Highlight cloud infrastructure experience"]
    }},
    "improvement_report": {{
        "overall_resume_score": 82.5,
        "ats_compatibility": 85.0,
        "role_match": 80.0,
        "company_job_alignment": 80.0,
        "strong_sections": ["Experience", "Skills"],
        "weak_sections": ["Summary"],
        "missing_keywords": ["Docker"],
        "missing_skills": ["Kubernetes"],
        "grammar_suggestions": ["Fix minor passive voice"],
        "formatting_suggestions": ["Use standard bullet points"],
        "summary_improvements": {{
            "original": "...",
            "optimized": "...",
            "reason": "..."
        }},
        "experience_improvements": [
            {{
                "original": "...",
                "optimized": "...",
                "reason": "..."
            }}
        ],
        "project_improvements": [
            {{
                "title": "...",
                "original_description": "...",
                "optimized_description": "...",
                "technical_impact": "...",
                "reason": "..."
            }}
        ],
        "recommended_actions": ["Add Docker to projects", "Quantify bullet points"]
    }}
}}
Return ONLY valid JSON.
"""
        try:
            cls._require_ai()
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text_resp = response.text.strip()
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:]
            if text_resp.endswith("```"):
                text_resp = text_resp[:-3]
            return json.loads(text_resp.strip())
        except Exception as e:
            logger.error("Gemini resume optimization failed: %s", e)
            raise RuntimeError("AI analysis is temporarily unavailable. Please try again.") from e

    @classmethod
    def analyze_readiness(cls, resume_text: str, target_role: str, target_company: Optional[str] = None, job_description: Optional[str] = None) -> Dict[str, Any]:
        company_str = target_company or "General"
        jd_str = job_description or "None provided"
        prompt = f"""
You are an expert AI Interview Readiness Predictor engine.
Analyze the candidate's preparation for the target role: "{target_role}"
Target Company: {company_str}
Job Description: {jd_str}

Resume / Candidate Context:
{resume_text}

Provide an interview readiness report in valid JSON format matching this exact schema:
{{
    "overall_readiness_score": 78.5,
    "confidence_level": "Moderate",
    "technical_readiness": {{
        "score": 80.0,
        "evaluated_topics": {{"Python": "Strong", "FastAPI": "Moderate", "System Design": "Weak"}},
        "feedback": "Strong backend fundamentals but needs more system design practice."
    }},
    "coding_readiness": {{
        "score": 75.0,
        "problem_solving": "Good algorithmic foundations",
        "algorithmic_thinking": "Proficient in standard data structures",
        "complexity_analysis": "Adequate",
        "status": "Ready with minor revision"
    }},
    "communication_readiness": {{
        "score": 82.0,
        "clarity": "Clear technical explanations",
        "structure": "Well-structured project walkthroughs",
        "technical_explanation": "Concise",
        "status": "Strong"
    }},
    "resume_readiness": {{
        "score": 85.0,
        "ats_compatibility": 85.0,
        "summary": "Resume aligns well with backend roles."
    }},
    "project_readiness": {{
        "score": 78.0,
        "explanation_readiness": "Able to explain core architecture",
        "architecture_clarity": "Moderate"
    }},
    "strong_areas": ["Python", "REST APIs", "SQL"],
    "weak_areas": ["System Design", "Docker"],
    "missing_evidence": ["Kubernetes deployment logs"],
    "knowledge_gaps": {{
        "strong_topics": ["Python", "FastAPI", "SQL"],
        "weak_topics": ["Caching", "Message Queues"],
        "missing_topics": ["System Design", "Kubernetes"]
    }},
    "recommended_topics": ["System Design", "Docker", "Redis"],
    "action_plan": [
        {{
            "priority": 1,
            "topic": "System Design",
            "reason": "Crucial for senior backend roles",
            "suggested_activity": "Practice distributed systems architecture questions",
            "estimated_study_time": "10 hours",
            "difficulty": "Medium"
        }}
    ],
    "company_readiness_scores": [
        {{"company_name": "{company_str}", "readiness_score": 76.0, "notes": "Solid role alignment based on job description."}},
        {{"company_name": "Amazon", "readiness_score": 78.0, "notes": "Good match for technical requirements."}},
        {{"company_name": "Zoho", "readiness_score": 85.0, "notes": "Strong core programming skills match."}}
    ],
    "career_insights": [
        "Strong potential for backend engineering roles.",
        "Focus on system design to unlock senior positions."
    ]
}}
Return ONLY valid JSON.
"""
        try:
            cls._require_ai()
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text_resp = response.text.strip()
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:]
            if text_resp.endswith("```"):
                text_resp = text_resp[:-3]
            return json.loads(text_resp.strip())
        except Exception as e:
            logger.error("Gemini readiness analysis failed: %s", e)
            raise RuntimeError("AI analysis is temporarily unavailable. Please try again.") from e
