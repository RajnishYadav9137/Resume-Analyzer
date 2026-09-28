import re

# Structured Skills Catalog categorized by technical domain
SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", 
        "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Dart", 
        "SQL", "Shell", "Bash", "Scala", "R"
    ],
    "Web & Frameworks": [
        "React", "React.js", "Next.js", "Angular", "Vue.js", "Node.js", 
        "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", 
        "ASP.NET", "Laravel", "HTML", "HTML5", "CSS", "CSS3", 
        "Tailwind CSS", "Bootstrap", "jQuery", "GraphQL", "REST APIs"
    ],
    "Databases & Storage": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", 
        "Firebase", "Cassandra", "DynamoDB", "MariaDB", "Elasticsearch"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", 
        "Git", "GitHub", "GitLab", "CI/CD", "Jenkins", "Linux", 
        "Terraform", "Ansible", "Nginx", "Apache"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", 
        "Natural Language Processing", "NLP", "Computer Vision", 
        "Data Science", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", 
        "PyTorch", "Keras", "OpenCV", "Power BI", "Tableau", "Excel", 
        "Matplotlib", "Seaborn"
    ],
    "Engineering, CAD & Tools": [
        "AutoCAD", "MATLAB", "SolidWorks", "Revit", "Quantity Estimation",
        "Site Execution", "Quality Assurance", "QA/QC", "Technical Documentation",
        "Project Management", "MS Office", "Jira", "Figma"
    ],
    "Core CS & Methodologies": [
        "Data Structures", "Algorithms", "Object-Oriented Programming", "OOP", 
        "System Design", "Microservices", "Agile", "Scrum", "Unit Testing", 
        "Problem Solving", "Communication", "Leadership", "Teamwork", 
        "Team Coordination", "Critical Thinking"
    ]
}

# Pre-compile regex patterns for precise skill matching to prevent false positives
# (e.g. preventing 'c' from matching every word with 'c', or 'Java' inside 'JavaScript')
def _compile_skill_pattern(skill):
    if skill == "C":
        return re.compile(r"\b[cC]\b(?!\s*[\+#])")
    elif skill == "C++":
        return re.compile(r"\b[cC]\+\+", re.IGNORECASE)
    elif skill == "C#":
        return re.compile(r"\b[cC]#", re.IGNORECASE)
    elif skill == "R":
        return re.compile(r"\b[rR]\b(?=\s*(?:programming|language|scripting|studio))", re.IGNORECASE)
    elif skill == ".NET" or skill == "ASP.NET":
        return re.compile(r"(?:\.net|asp\.net)", re.IGNORECASE)
    elif skill == "CI/CD":
        return re.compile(r"\bci\s*/\s*cd\b", re.IGNORECASE)
    elif skill in ["Node.js", "React.js", "Vue.js", "Next.js", "Express.js"]:
        base = skill.split(".")[0]
        return re.compile(rf"\b{re.escape(base)}(?:\.js)?\b", re.IGNORECASE)
    elif skill == "Java":
        return re.compile(r"\bjava\b(?!script)", re.IGNORECASE)
    elif skill == "Git":
        return re.compile(r"\bgit\b(?!hub|lab)", re.IGNORECASE)
    elif skill == "HTML" or skill == "HTML5":
        return re.compile(r"\bhtml(?:5)?\b", re.IGNORECASE)
    elif skill == "CSS" or skill == "CSS3":
        return re.compile(r"\bcss(?:3)?\b", re.IGNORECASE)
    else:
        # Standard word boundary match
        return re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)

COMPILED_SKILLS = {}
for category, skills in SKILL_CATEGORIES.items():
    COMPILED_SKILLS[category] = [(skill, _compile_skill_pattern(skill)) for skill in skills]


def extract_skills_from_section(text):
    """
    Finds custom skills listed directly under a Skills/Technical Skills heading.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    skills_found = []
    in_skills_section = False

    section_headers = [
        "skills", "technical skills", "core skills", "key skills", 
        "professional skills", "core competencies", "technologies", 
        "tools & technologies", "technical proficiencies", "civil engineering skills"
    ]
    other_headers = [
        "experience", "work experience", "professional experience", "education", 
        "educational qualifications", "projects", "certifications", 
        "achievements", "languages", "personal details", "summary", 
        "profile", "objective", "declaration", "interests"
    ]

    for line in lines:
        line_clean = line.strip("•- \t|*#:")
        line_lower = line_clean.lower()

        if any(h in line_lower for h in section_headers) and len(line_clean.split()) <= 5:
            in_skills_section = True
            continue

        if in_skills_section and any(h in line_lower for h in other_headers) and len(line_clean.split()) <= 5:
            in_skills_section = False
            break

        if in_skills_section:
            item_text = re.sub(r"^[•\-\*\u2022\ufffd\d+\.]\s*", "", line).strip()
            if not item_text or len(item_text) > 80:
                continue

            if "," in item_text or "|" in item_text:
                parts = re.split(r"[,|]", item_text)
                for part in parts:
                    clean_p = part.strip()
                    if 2 <= len(clean_p) <= 35 and len(clean_p.split()) <= 4:
                        skills_found.append(clean_p.title())
            else:
                if 2 <= len(item_text) <= 35 and len(item_text.split()) <= 4:
                    skills_found.append(item_text.title())

    return skills_found


def extract_skills(text):
    """
    Extracts skills accurately without false positives.
    Returns a deduplicated list of found skills.
    """
    found_skills = []
    seen = set()

    for category, skill_list in COMPILED_SKILLS.items():
        for skill_name, pattern in skill_list:
            if pattern.search(text):
                clean_name = skill_name
                # Normalize variations
                if clean_name in ["HTML5"]: clean_name = "HTML"
                if clean_name in ["CSS3"]: clean_name = "CSS"
                if clean_name in ["React.js"]: clean_name = "React"
                if clean_name in ["Node.js"]: clean_name = "Node.js"
                if clean_name in ["Express.js"]: clean_name = "Express"
                if clean_name in ["Vue.js"]: clean_name = "Vue"
                
                if clean_name.lower() not in seen:
                    seen.add(clean_name.lower())
                    found_skills.append(clean_name)

    # Merge dynamic section skills
    section_skills = extract_skills_from_section(text)
    for s in section_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            found_skills.append(s)

    return found_skills


def extract_categorized_skills(text):
    """
    Returns skills grouped by their technical category.
    """
    categorized = {}
    seen = set()

    for category, skill_list in COMPILED_SKILLS.items():
        matched = []
        for skill_name, pattern in skill_list:
            if pattern.search(text):
                clean_name = skill_name
                if clean_name in ["HTML5"]: clean_name = "HTML"
                if clean_name in ["CSS3"]: clean_name = "CSS"
                if clean_name in ["React.js"]: clean_name = "React"
                if clean_name in ["Vue.js"]: clean_name = "Vue"
                if clean_name in ["Express.js"]: clean_name = "Express"
                
                if clean_name.lower() not in seen:
                    seen.add(clean_name.lower())
                    matched.append(clean_name)
        if matched:
            categorized[category] = matched

    # Add dynamically detected skills under Domain-Specific / Custom Skills
    section_skills = extract_skills_from_section(text)
    custom_skills = []
    for s in section_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            custom_skills.append(s)
    if custom_skills:
        categorized["Domain & Specialized Skills"] = custom_skills

    return categorized


def extract_email(text):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    matches = re.findall(pattern, text)
    if matches:
        # Return clean lowercase email
        return matches[0].strip().lower()
    return "Not detected"


def extract_phone(text):
    # Matches international and standard phone formats (+91, +1, +44, with dashes, dots, spaces or parens)
    patterns = [
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        r"(?:\+91[\s-]?)?[6-9]\d{9}\b",
        r"\b\d{10}\b"
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            phone_candidate = match.group(0).strip()
            # Verify it contains at least 10 digits
            digits = re.sub(r"\D", "", phone_candidate)
            if 10 <= len(digits) <= 15:
                return phone_candidate
    return "Not detected"


def extract_links(text):
    """
    Extracts LinkedIn, GitHub, and Portfolio URLs from resume text.
    """
    links = {}
    
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        url = linkedin_match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        links["linkedin"] = url

    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        url = github_match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        links["github"] = url

    return links


def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Common words/headers to skip when finding the candidate's name
    skip_keywords = [
        "resume", "curriculum vitae", "cv", "profile", "summary", 
        "contact", "education", "experience", "skills", "projects",
        "email", "phone", "page 1", "page 2", "personal details", 
        "objective", "work experience", "about me", "http", "www"
    ]

    for line in lines[:8]:
        line_clean = line.strip("•- \t|")
        line_lower = line_clean.lower()
        
        # Skip if contains skip keywords or emails or urls or phone digits
        if any(skip in line_lower for skip in skip_keywords):
            continue
        if "@" in line_clean or "/" in line_clean or "\\" in line_clean:
            continue
        # Skip if line has many numbers
        if sum(c.isdigit() for c in line_clean) > 2:
            continue
        # Check if length and word count match a realistic name (2 to 4 words)
        words = line_clean.split()
        if 1 <= len(words) <= 4 and len(line_clean) <= 40:
            # Check that words look like name tokens (capitalized or alpha)
            if all(re.match(r"^[A-Za-z\.'-]+$", w) for w in words):
                return line_clean.title()

    # Fallback to first line if reasonably short
    if lines and len(lines[0]) <= 35 and not any(k in lines[0].lower() for k in ["resume", "cv", "@"]):
        return lines[0].title()

    return "Candidate"


def extract_education(text):
    lines = [
        line.strip("•- \t|*")
        for line in text.splitlines()
        if line.strip()
    ]

    education_lines = []

    education_keywords = [
        "b.tech", "btech", "m.tech", "mtech", "bca", "mca", "b.sc", "bsc", 
        "m.sc", "msc", "bachelor of technology", "bachelor of science", 
        "bachelor of engineering", "master of technology", "master of science", 
        "bachelor", "master", "ph.d", "phd", "degree", "diploma", 
        "senior secondary", "intermediate", "class xii", "class 12", 
        "class x", "class 10", "12th", "10th", "university", "college", 
        "institute", "school", "cgpa", "percentage", "gpa"
    ]

    ignore_keywords = [
        "participated", "actively", "activity", "activities", "motivated", 
        "detail-oriented", "detail oriented", "interest in", "software development", 
        "developed", "responsible", "worked", "working", "technical skills", 
        "github", "linkedin", "http"
    ]

    for line in lines:
        line_lower = line.lower()
        if len(line.split()) > 16:
            continue
        if any(word in line_lower for word in ignore_keywords):
            continue
        if any(keyword in line_lower for keyword in education_keywords):
            if 4 <= len(line) <= 130:
                if line not in education_lines:
                    education_lines.append(line)

    return education_lines[:6]


def extract_experience(text):
    # Check for direct duration strings (e.g., "3 years", "2.5 yrs", "18 months")
    pattern_duration = r"\b\d+(?:\.\d+)?\+?\s*(?:years?|yrs?|months?)\s*(?:of\s+experience)?\b"
    matches = re.findall(pattern_duration, text, flags=re.IGNORECASE)

    # Check for date ranges (e.g. 2021 - 2024, Jan 2020 - Present)
    date_range_pattern = r"\b(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|present|current)\b"
    range_matches = re.findall(date_range_pattern, text, flags=re.IGNORECASE)

    # Check for fresher keywords
    if re.search(r"\b(?:fresher|recent graduate|entry[- ]level)\b", text, re.IGNORECASE):
        if not matches and not range_matches:
            return "Fresher / Entry Level"

    if matches:
        unique_matches = list(dict.fromkeys([m.strip() for m in matches]))
        return ", ".join(unique_matches[:2])
    elif range_matches:
        return f"{len(range_matches)} roles detected ({', '.join(range_matches[:2])})"
    elif re.search(r"\b(?:intern|internship|software engineer|developer|analyst)\b", text, re.IGNORECASE):
        return "Experience detected (Intern / Professional roles found)"

    return "Fresher / Not explicitly stated"


def detect_sections(text):
    """
    Checks the presence of essential resume sections for ATS verification.
    """
    text_lower = text.lower()
    
    sections = {
        "Contact Information": bool(re.search(r"@[A-Za-z0-9.-]+", text) or re.search(r"\d{10}", text)),
        "Professional Summary / Objective": bool(re.search(r"\b(summary|objective|about me|profile overview)\b", text_lower)),
        "Education Section": bool(re.search(r"\b(education|academic|qualifications|degree|btech|b\.tech|bachelor)\b", text_lower)),
        "Experience / Internships": bool(re.search(r"\b(experience|employment|work history|internship|internships|worked as)\b", text_lower)),
        "Projects Section": bool(re.search(r"\b(projects?|portfolio|personal projects|academic projects)\b", text_lower)),
        "Technical Skills": bool(re.search(r"\b(skills|technical skills|technologies|tech stack|tools)\b", text_lower)),
        "Certifications / Achievements": bool(re.search(r"\b(certificat(?:e|ion|ions)|achievements?|awards?|hackathon)\b", text_lower)),
        "Online Profiles (GitHub/LinkedIn)": bool(re.search(r"\b(github|linkedin|portfolio)\b", text_lower))
    }
    return sections
