import re
from analyzer.skill_extractor import extract_skills

# Predefined role benchmark skill sets
ROLE_PROFILES = {
    "fullstack": {
        "title": "Full Stack Developer",
        "core_skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "MongoDB", "Git", "REST APIs", "Python", "Docker"]
    },
    "frontend": {
        "title": "Frontend Developer",
        "core_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Tailwind CSS", "Bootstrap", "Git", "Next.js", "REST APIs"]
    },
    "backend": {
        "title": "Backend Developer",
        "core_skills": ["Python", "Java", "Node.js", "SQL", "PostgreSQL", "MongoDB", "Docker", "REST APIs", "Git", "Redis", "Microservices"]
    },
    "datascience": {
        "title": "Data Scientist / AI Engineer",
        "core_skills": ["Python", "Machine Learning", "Data Science", "Pandas", "NumPy", "SQL", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Power BI"]
    },
    "devops": {
        "title": "DevOps & Cloud Engineer",
        "core_skills": ["Linux", "AWS", "Docker", "Kubernetes", "CI/CD", "Git", "Terraform", "Jenkins", "Bash", "Python", "Nginx"]
    },
    "mobile": {
        "title": "Mobile App Developer",
        "core_skills": ["Kotlin", "Swift", "Java", "Git", "REST APIs", "Firebase", "SQLite"]
    },
    "software_engineer": {
        "title": "Software Engineer (General)",
        "core_skills": ["Data Structures", "Algorithms", "Python", "Java", "C++", "Git", "SQL", "OOP", "System Design", "Problem Solving"]
    }
}

ACTION_VERBS = [
    "developed", "built", "engineered", "implemented", "designed", "architected",
    "optimized", "spearheaded", "created", "launched", "deployed", "scaled",
    "improved", "automated", "integrated", "managed", "collaborated", "reduced",
    "increased", "achieved", "delivered", "executed", "configured", "debugged"
]


def calculate_scores(text, skills, education, experience, sections, links, target_role="software_engineer", job_description=""):
    """
    Computes rigorous, multi-dimensional scores and actionable recommendations.
    """
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)

    # 1. ATS COMPATIBILITY SCORE (0-100)
    ats_score = 0

    # Section completeness (up to 40 pts)
    section_points = {
        "Contact Information": 10,
        "Education Section": 8,
        "Experience / Internships": 8,
        "Projects Section": 8,
        "Technical Skills": 6
    }
    for sec_name, pts in section_points.items():
        if sections.get(sec_name, False):
            ats_score += pts

    # Professional profiles / links (up to 10 pts)
    if links.get("linkedin") or links.get("github"):
        ats_score += 10
    elif "github" in text_lower or "linkedin" in text_lower:
        ats_score += 5

    # Word count / Ideal resume length (up to 20 pts)
    if 400 <= word_count <= 1100:
        ats_score += 20
    elif 250 <= word_count < 400 or 1100 < word_count <= 1600:
        ats_score += 14
    elif word_count > 1600:
        ats_score += 8
    else:
        ats_score += 5

    # Action verbs presence (up to 15 pts)
    found_verbs = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", text_lower)]
    ats_score += min(len(found_verbs) * 3, 15)

    # Skill density (up to 15 pts)
    if len(skills) >= 8:
        ats_score += 15
    elif len(skills) >= 4:
        ats_score += 10
    elif len(skills) >= 1:
        ats_score += 5

    ats_score = min(max(ats_score, 10), 100)


    # 2. RESUME STRENGTH SCORE (0-100)
    strength_score = 0

    # Action verbs strength (up to 25 pts)
    strength_score += min(len(found_verbs) * 4, 25)

    # Quantifiable results and metrics (% numbers, $, improvements) (up to 25 pts)
    metric_matches = re.findall(r"\b\d+(?:\.\d+)?%|\b\$\d+(?:,\d+)?|\b\d{1,3}\+?\s*(?:users|clients|requests|ms|seconds|records|downloads|stars)\b", text, re.IGNORECASE)
    if len(metric_matches) >= 4:
        strength_score += 25
    elif len(metric_matches) >= 2:
        strength_score += 18
    elif len(metric_matches) >= 1:
        strength_score += 10

    # Project and experience depth (up to 20 pts)
    if sections.get("Projects Section", False):
        strength_score += 10
    if experience != "Not detected" and experience != "Fresher / Not explicitly stated":
        strength_score += 10
    elif sections.get("Experience / Internships", False):
        strength_score += 8

    # Professional presence (LinkedIn & GitHub links) (up to 15 pts)
    if links.get("github") and links.get("linkedin"):
        strength_score += 15
    elif links.get("github") or links.get("linkedin"):
        strength_score += 10
    elif "github" in text_lower or "linkedin" in text_lower:
        strength_score += 5

    # Certifications & achievements (up to 15 pts)
    if sections.get("Certifications / Achievements", False):
        strength_score += 15
    elif "certified" in text_lower or "course" in text_lower:
        strength_score += 8

    strength_score = min(max(strength_score, 15), 100)


    # 3. TECHNICAL SKILLS SCORE (0-100)
    tech_score = 0
    num_skills = len(skills)

    if num_skills >= 15:
        tech_score = 95
    elif num_skills >= 12:
        tech_score = 88
    elif num_skills >= 9:
        tech_score = 78
    elif num_skills >= 6:
        tech_score = 65
    elif num_skills >= 3:
        tech_score = 50
    elif num_skills >= 1:
        tech_score = 35
    else:
        tech_score = 15

    # Bonus for diversified skill coverage (e.g. languages + frameworks + databases)
    tech_score = min(tech_score, 100)


    # 4. PROJECT SCORE (0-100)
    project_score = 0
    if sections.get("Projects Section", False):
        project_score += 35
    else:
        if "project" in text_lower:
            project_score += 20

    # Tech stack integration in projects
    project_action_verbs = [v for v in ["developed", "built", "implemented", "created", "designed", "architected"] if v in text_lower]
    project_score += min(len(project_action_verbs) * 7, 25)

    # GitHub links / demo links for projects
    if links.get("github"):
        project_score += 20
    elif "github.com" in text_lower or "gitlab.com" in text_lower:
        project_score += 12

    # Technical skills count applied
    if num_skills >= 6:
        project_score += 20
    elif num_skills >= 3:
        project_score += 12
    else:
        project_score += 5

    project_score = min(max(project_score, 10), 100)


    # 5. JOB MATCH & TARGET ROLE COMPATIBILITY
    matched_skills = []
    missing_skills = []
    role_title = "General Software Engineering"

    if job_description.strip():
        # Custom Job Description matching
        role_title = "Custom Job Description"
        jd_skills = extract_skills(job_description)
        if not jd_skills:
            # Fallback if no specific skills in JD, match against tech keywords
            jd_skills = ROLE_PROFILES.get(target_role, ROLE_PROFILES["software_engineer"])["core_skills"]
            role_title = ROLE_PROFILES.get(target_role, ROLE_PROFILES["software_engineer"])["title"]

        for req in jd_skills:
            if req.lower() in [s.lower() for s in skills]:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        match_ratio = len(matched_skills) / max(len(jd_skills), 1)
        job_match_score = int(match_ratio * 100)
    else:
        role_data = ROLE_PROFILES.get(target_role, ROLE_PROFILES["software_engineer"])
        role_title = role_data["title"]
        core_reqs = role_data["core_skills"]

        for req in core_reqs:
            if any(req.lower() == s.lower() for s in skills):
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        match_ratio = len(matched_skills) / len(core_reqs)
        # Base score on skills match + general strength
        job_match_score = int((match_ratio * 0.75 + (strength_score / 100) * 0.25) * 100)

    job_match_score = min(max(job_match_score, 10), 100)


    # 6. ACTIONABLE RECOMMENDATIONS & INSIGHTS
    strengths = []
    improvements = []

    if ats_score >= 75:
        strengths.append("High ATS compliance with well-defined resume structure and clear sections.")
    else:
        improvements.append("Ensure standard section headers are used (e.g. 'Work Experience', 'Education', 'Projects', 'Technical Skills').")

    if len(skills) >= 8:
        strengths.append(f"Strong technical skill coverage with {len(skills)} verified industry technologies detected.")
    else:
        improvements.append("Expand your technical skills list to include modern tools, databases, and frameworks relevant to your target role.")

    if links.get("github") and links.get("linkedin"):
        strengths.append("Professional presence: Both GitHub and LinkedIn profiles are clearly linked.")
    elif not links.get("github") and not links.get("linkedin"):
        improvements.append("Add clickable links to your LinkedIn and GitHub profiles at the top of your resume.")

    if len(metric_matches) >= 2:
        strengths.append("Effective use of quantifiable results and performance metrics in project descriptions.")
    else:
        improvements.append("Add quantifiable metrics to bullet points (e.g., 'Improved query performance by 35%', 'Served 1000+ daily active users').")

    if not sections.get("Professional Summary / Objective", False):
        improvements.append("Include a concise 2-3 sentence Professional Summary at the top highlighting your core value.")

    if missing_skills:
        top_missing = ", ".join(missing_skills[:4])
        improvements.append(f"Target role ({role_title}) recommends adding skills like: {top_missing}.")

    if word_count < 350:
        improvements.append(f"Resume is relatively brief ({word_count} words). Aim for 450 - 800 words to provide adequate depth.")
    elif word_count > 1200:
        improvements.append(f"Resume is on the longer side ({word_count} words). Consider condensing to 1-2 focused pages.")

    return {
        "scores": {
            "ats": ats_score,
            "strength": strength_score,
            "technical": tech_score,
            "project": project_score,
            "job_match": job_match_score
        },
        "target_role": role_title,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "improvements": improvements,
        "metrics_found": len(metric_matches),
        "action_verbs_found": len(found_verbs),
        "word_count": word_count
    }
