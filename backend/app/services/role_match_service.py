"""
Evidence-based matching between an uploaded resume and a selected
company's job role.

Design:
- The deterministic scorer is the source of truth for what the resume can
  prove (evidence search over the resume's raw text + extracted skills) and
  computes the match percentage from weighted requirement coverage.
- When GEMINI_API_KEY is configured, Gemini enriches the evidence with
  semantic matching (e.g. "built REST services with Express" counts for
  "Node.js"). AI output can only UPGRADE/EXPLAIN; it can never invent a
  requirement the role doesn't have.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.exceptions import NotFoundException, ValidationException
from app.core.logging import get_logger
from app.models.company import (
    Company,
    JobRole,
    MatchStatus,
    RequirementCategory,
    RoleMatchResult,
    RoleRequirement,
)
from app.resume.models.resume import Resume
from app.resume.repositories.resume_repository import ResumeRepository

logger = get_logger(__name__)

# Normalization map: variants found in a resume -> canonical requirement name.
_SKILL_ALIASES: dict[str, list[str]] = {
    "python": ["python", "python3"],
    "java": ["java", "java8", "java11", "java17", "core java"],
    "javascript": ["javascript", "js", "es6", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net", "dotnet"],
    "sql": ["sql", "mysql", "postgres", "postgresql", "sqlite", "t-sql", "pl/sql"],
    "postgresql": ["postgres", "postgresql"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node", "node.js", "nodejs"],
    "rest apis": ["rest", "rest api", "rest apis", "restful", "api development", "web services"],
    "ci/cd": ["ci/cd", "cicd", "jenkins", "github actions", "gitlab ci", "continuous integration"],
    "git": ["git", "github", "gitlab", "bitbucket"],
    "linux": ["linux", "unix", "bash", "shell scripting"],
    "spring boot": ["spring", "spring boot", "springboot"],
    "machine learning": ["machine learning", "ml", "ml models", "predictive modeling"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "keras"],
    "redis": ["redis", "caching layer"],
    "kafka": ["kafka", "message queue", "event streaming"],
    "microservices": ["microservices", "microservice architecture", "service oriented"],
    "system design": ["system design", "architecture design", "scalable architecture", "distributed systems"],
    "data structures": ["data structures", "dsa"],
    "algorithms": ["algorithms", "problem solving"],
    "html5": ["html", "html5"],
    "css3": ["css", "css3", "tailwind"],
    "docker compose": ["docker-compose"],
}


def _canonical(requirement: str) -> str:
    return requirement.strip().lower()


def _aliases_for(requirement: str) -> list[str]:
    req = _canonical(requirement)
    aliases = _SKILL_ALIASES.get(req, [])
    # Always include the requirement itself and its lowercase form.
    return list({req, requirement.strip(), *aliases})


def _find_evidence(requirement: str, resume: Resume) -> tuple[str | None, float]:
    """Search the actual resume content for evidence supporting a requirement.

    Returns (evidence_snippet_or_None, confidence 0..1).
    """
    aliases = _aliases_for(requirement)
    raw = (resume.raw_text or "")
    raw_lower = raw.lower()

    # 1) Structured skills parsed from the resume.
    skill_names = {s.name.strip().lower(): s for s in (resume.skills or [])}
    for alias in aliases:
        if alias in skill_names:
            return f"Listed in resume skills as '{skill_names[alias].name}'", 0.9

    # 2) Projects / experience / education sections mention the requirement.
    for section in (resume.sections or []):
        if not section.content_json:
            continue
        if isinstance(section.content_json, list):
            blob = " ".join(
                str(item) for item in section.content_json
            ).lower()
        else:
            blob = str(section.content_json).lower()
        for alias in aliases:
            if re.search(rf"(?<!\w){re.escape(alias.lower())}(?!\w)", blob):
                label = section.section_type.value.replace("_", " ").title()
                snippet = blob[:160].strip()
                return f"Mentioned in the {label} section: \"{snippet}...\"", 0.8

    # 3) Raw text search (word-boundary, case-insensitive).
    for alias in aliases:
        pattern = rf"(?<!\w){re.escape(alias.lower())}(?!\w)"
        match = re.search(pattern, raw_lower)
        if match:
            start = max(0, match.start() - 70)
            end = min(len(raw), match.end() + 70)
            snippet = " ".join(raw[start:end].split())
            return f"Found in resume text: \"...{snippet}...\"", 0.7

    return None, 0.0


def _score_status(confidence: float) -> MatchStatus:
    if confidence >= 0.85:
        return MatchStatus.STRONG
    if confidence >= 0.7:
        return MatchStatus.MODERATE
    if confidence > 0.0:
        return MatchStatus.WEAK
    return MatchStatus.MISSING


def _weak_reason(requirement: str, company: str, role_title: str, status: MatchStatus) -> str:
    base = f"'{requirement}' is required for the {role_title} role at {company}"
    if status == MatchStatus.MISSING:
        return (
            f"{base}, but there is no supporting experience or project in your uploaded resume."
        )
    return (
        f"{base}, and your resume only shows limited/partial exposure to it. "
        "Strengthen the evidence (project or work bullet) to raise this match."
    )


def _ai_enrich(resume_text: str, role: JobRole, company: Company, requirements: list[RoleRequirement]) -> dict | None:
    """Optional Gemini pass for semantic evidence matching. Returns None when
    unavailable. The result may upgrade statuses/confidence but never adds
    requirements that don't exist in the role."""
    from app.core.config import settings

    if not settings.GEMINI_API_KEY:
        return None
    try:
        from app.resume.services.ai.gemini_client import generate_structured_json

        req_list = ", ".join(r.requirement for r in requirements)
        raw = generate_structured_json(
            f"""You are matching a resume against a job's requirements.

ROLE: {role.title} at {company.name}
REQUIREMENTS: {req_list}

RESUME:
\"\"\"
{resume_text[:12000]}
\"\"\"

For EACH requirement, decide whether the resume contains real evidence (project, work experience, skill listing) supporting it. Semantic equivalents count (e.g. 'built APIs with Express' supports 'Node.js'). Return ONLY JSON:
{{
  "matches": [
    {{"requirement": "<exact requirement string>",
      "status": "strong" | "moderate" | "weak" | "missing",
      "confidence": <0-1 float>,
      "evidence": "<short quote or paraphrase from the resume, or null>",
      "reason": "<one sentence explaining the status>"}}
  ]
}}
Use the EXACT requirement strings from the list. Never add requirements that are not in the list.""",
            temperature=0.2,
        )
        if isinstance(raw, dict) and isinstance(raw.get("matches"), list):
            return raw
    except Exception as exc:  # noqa: BLE001
        logger.warning("AI enrichment for role match failed: %s", exc)
    return None


def compute_role_match(
    db: Session,
    resume_id: uuid.UUID,
    user_id: uuid.UUID,
    company_id: uuid.UUID,
    job_role_id: uuid.UUID,
) -> RoleMatchResult:
    """Run an evidence-based match and persist the result. Raises if the
    resume isn't parsed, or the company/role don't exist."""
    resume_repo = ResumeRepository(db)
    resume = resume_repo.get_with_details(resume_id)
    if resume is None or resume.user_id != user_id or not resume.is_active:
        raise NotFoundException("Resume not found.")
    if resume.status.value != "parsed" or not resume.raw_text:
        raise ValidationException("Resume must be successfully parsed before matching.")

    company = db.get(Company, company_id)
    role = db.get(JobRole, job_role_id)
    if company is None or not company.is_active:
        raise NotFoundException("Company not found.")
    if role is None or role.company_id != company.id or not role.is_active:
        raise NotFoundException("Job role not found for this company.")

    requirements = list(
        db.execute(
            select(RoleRequirement)
            .where(RoleRequirement.job_role_id == role.id)
            .order_by(RoleRequirement.importance.desc())
        ).scalars().all()
    )
    if not requirements:
        raise ValidationException("This job role has no requirements configured.")

    evidence_items: list[dict[str, Any]] = []
    for req in requirements:
        evidence, confidence = _find_evidence(req.requirement, resume)
        status = _score_status(confidence)
        evidence_items.append(
            {
                "requirement": req.requirement,
                "category": req.category.value,
                "importance": req.importance,
                "evidence": evidence,
                "status": status.value,
                "confidence": round(confidence, 2),
                "reason": (
                    f"Resume evidence: {evidence}"
                    if evidence
                    else _weak_reason(req.requirement, company.name, role.title, status)
                ),
            }
        )

    # Optional AI enrichment: only upgrade/annotate existing requirements.
    ai_result = _ai_enrich(resume.raw_text, role, company, requirements)
    if ai_result:
        by_req = {_canonical(m.get("requirement", "")): m for m in ai_result["matches"]}
        for item in evidence_items:
            ai_item = by_req.get(_canonical(item["requirement"]))
            if not ai_item:
                continue
            try:
                ai_status = MatchStatus(str(ai_item.get("status", "")).lower())
            except ValueError:
                ai_status = None
            ai_conf = ai_item.get("confidence")
            if ai_status is not None and ai_conf is not None:
                try:
                    ai_conf = max(0.0, min(1.0, float(ai_conf)))
                except (TypeError, ValueError):
                    ai_conf = None
            # Only allow upgrades (never downgrade deterministic evidence).
            if ai_status and ai_conf is not None and ai_conf > item["confidence"]:
                item["status"] = ai_status.value
                item["confidence"] = round(ai_conf, 2)
            if ai_item.get("evidence") and not item["evidence"]:
                item["evidence"] = str(ai_item["evidence"])
            if ai_item.get("reason"):
                item["reason"] = str(ai_item["reason"])

    # Weighted match percentage from importance * confidence.
    total_weight = sum(r.importance for r in requirements)
    earned = 0.0
    for item, req in zip(evidence_items, requirements):
        earned += req.importance * float(item["confidence"])
    match_percentage = round(earned / total_weight * 100.0, 1) if total_weight else 0.0

    strong = [i["requirement"] for i in evidence_items if i["status"] in ("strong", "moderate")]
    weak = [i["requirement"] for i in evidence_items if i["status"] in ("weak", "missing")]
    matched = [i["requirement"] for i in evidence_items if i["status"] in ("strong", "moderate")]
    missing = [i["requirement"] for i in evidence_items if i["status"] in ("weak", "missing")]

    result = RoleMatchResult(
        resume_id=resume_id,
        user_id=user_id,
        company_id=company.id,
        job_role_id=role.id,
        match_percentage=match_percentage,
        strong_areas=strong,
        weak_areas=weak,
        requirements_matched=matched,
        requirements_missing=missing,
        evidence=evidence_items,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def seed_if_empty(db: Session) -> None:
    """Idempotent seed of companies/roles/requirements for sqlite dev boots
    (Postgres deployments get the same data from migration 0005)."""
    exists = db.execute(select(Company).limit(1)).scalar_one_or_none()
    if exists is not None:
        return

    from app.services.seed_data import build_seed_rows

    for c in build_seed_rows():
        company = Company(name=c["company"], description=c.get("description"), industry=c.get("industry"))
        db.add(company)
        db.flush()
        for r in c["roles"]:
            role = JobRole(
                company_id=company.id,
                title=r["title"],
                description=r.get("description"),
                domain=r.get("domain"),
                seniority=r.get("seniority"),
                job_description=(
                    f"{r['title']} at {c['company']} — {r['description']} "
                    f"Key requirements: {', '.join(req for req, _c, _i in r['requirements'])}."
                ),
            )
            db.add(role)
            db.flush()
            for req, cat, imp in r["requirements"]:
                db.add(
                    RoleRequirement(
                        job_role_id=role.id,
                        requirement=req,
                        category=RequirementCategory(cat),
                        importance=imp,
                    )
                )
    db.commit()
    logger.info("Seeded companies/job roles for local development.")
