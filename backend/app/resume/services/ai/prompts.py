"""
All Gemini prompt templates live here, kept separate from service/business
logic so they can be reviewed, versioned, and tuned independently.
"""

RESUME_EXTRACTION_PROMPT = """You are a resume parsing engine. Extract structured information from the resume text below.

Return ONLY a single valid JSON object with this exact shape (no markdown, no commentary):
{{
  "full_name": string or null,
  "email": string or null,
  "phone": string or null,
  "location": string or null,
  "linkedin_url": string or null,
  "github_url": string or null,
  "portfolio_url": string or null,
  "professional_summary": string or null,
  "skills": [string],
  "education": [{{"institution": string, "degree": string, "field": string or null, "start_date": string or null, "end_date": string or null, "gpa": string or null}}],
  "experience": [{{"company": string, "title": string, "start_date": string or null, "end_date": string or null, "location": string or null, "description": [string]}}],
  "projects": [{{"name": string, "description": [string], "technologies": [string], "url": string or null}}],
  "certifications": [{{"name": string, "issuer": string or null, "date": string or null}}],
  "achievements": [string]
}}

If a field cannot be determined, use null (or an empty list for list fields). Do not invent data that is not present in the resume text.

RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"
"""


RESUME_ANALYSIS_PROMPT = """You are an expert technical resume reviewer and ATS (Applicant Tracking System) simulator, evaluating resumes for software engineering / technical roles.

Analyze the resume text below and return ONLY a single valid JSON object with this exact shape (no markdown, no commentary):
{{
  "overall_score": number (0-100),
  "ats_compatibility_score": number (0-100),
  "professional_summary_analysis": string,
  "strengths": [string],
  "weaknesses": [string],
  "missing_skills": [string],
  "missing_keywords": [string],
  "grammar_suggestions": [string],
  "formatting_suggestions": [string],
  "section_scores": [
    {{"section": "summary"|"skills"|"experience"|"projects"|"education"|"certifications"|"achievements", "score": number (0-100), "feedback": string}}
  ],
  "suggestions": [
    {{"type": "grammar"|"formatting"|"content"|"keyword"|"achievement", "section": string or null, "severity": "low"|"medium"|"high", "message": string, "suggested_fix": string or null}}
  ],
  "keywords": [
    {{"keyword": string, "status": "present"|"missing", "relevance": number (0-1)}}
  ]
}}

Scoring guidance:
- Be specific and evidence-based; reference what is actually present or absent in the resume.
- ATS compatibility should reflect formatting/parseability concerns (tables, images, unusual fonts hinted at by text extraction artifacts, missing standard section headers) plus keyword coverage for the candidate's apparent target domain.
- Cover ALL seven sections in section_scores, even if a section is missing from the resume (score it low and say why in feedback).
- Only include section_scores for sections evaluable from the resume; if a section is entirely absent, still include it with a low score noting its absence.

RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"
"""


COMPANY_MATCH_PROMPT = """You are simulating a technical recruiter's resume screen for {company_name}{role_clause}.

Evaluate how well the resume below matches typical technical requirements and hiring bar for {company_name}. This is a compatibility estimate for career-preparation purposes ONLY -- it must NOT be presented as an actual hiring probability or guarantee.

Return ONLY a single valid JSON object with this exact shape (no markdown, no commentary):
{{
  "role_match_score": number (0-100),
  "resume_compatibility_score": number (0-100),
  "required_skills": [string],
  "matched_skills": [string],
  "missing_skills": [string],
  "relevant_keywords": [string],
  "improvement_suggestions": [string]
}}

Base required_skills on what is genuinely representative of {company_name}'s typical technical hiring bar for this kind of role, and matched_skills/missing_skills strictly from what is present or absent in the resume text below.

RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"
"""


def build_resume_extraction_prompt(resume_text: str) -> str:
    return RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text[:15000])


def build_resume_analysis_prompt(resume_text: str) -> str:
    return RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text[:15000])


def build_company_match_prompt(resume_text: str, company_name: str, target_role: str | None) -> str:
    role_clause = f" for a {target_role} role" if target_role else ""
    return COMPANY_MATCH_PROMPT.format(
        resume_text=resume_text[:15000], company_name=company_name, role_clause=role_clause
    )
