import io
import unittest
from analyzer.resume_parser import extract_text, clean_text
from analyzer.skill_extractor import (
    extract_skills,
    extract_categorized_skills,
    extract_email,
    extract_phone,
    extract_name,
    extract_education,
    extract_experience,
    extract_links,
    detect_sections
)
from analyzer.resume_scorer import calculate_scores
from app import app


SAMPLE_RESUME_TEXT = """
Alex Morgan
alex.morgan@email.com | +1 (555) 234-5678 | linkedin.com/in/alexmorgan | github.com/alexmorgan

PROFESSIONAL SUMMARY
Results-driven Full Stack Software Engineer with 3+ years of experience designing, developing, and deploying scalable web applications. Spearheaded backend optimization reducing API response latency by 45%.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
Frameworks: React, Node.js, Express, Flask, Tailwind CSS
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS, Git, CI/CD
Methodologies: Agile, Scrum, REST APIs, Microservices

WORK EXPERIENCE
Senior Software Engineer | TechNova Solutions | 2021 - Present
- Architected and built high-throughput microservices handling 250,000+ daily active users.
- Optimized PostgreSQL database queries, improving performance by 35%.
- Implemented CI/CD deployment pipelines using GitHub Actions and Docker on AWS.

EDUCATION
Bachelor of Technology in Computer Science | Apex Institute of Technology | 2017 - 2021
CGPA: 8.9 / 10

PROJECTS
CloudTask Manager | React, Node.js, MongoDB, Docker
- Built a real-time collaborative task platform with 5,000+ registered users.
- Integrated WebSocket notifications and secure OAuth2 authentication.
- Repository: github.com/alexmorgan/cloudtask

CERTIFICATIONS
- AWS Certified Solutions Architect Associate (2023)
"""


class TestResumeAnalyzer(unittest.TestCase):

    def test_clean_text(self):
        dirty = "Hello\u00a0world\r\nTest\x00String"
        cleaned = clean_text(dirty)
        self.assertNotIn("\x00", cleaned)
        self.assertIn("Hello world", cleaned)

    def test_skill_extractor_no_false_positives(self):
        # Text with lots of 'c', 'java' inside javascript, etc.
        tricky_text = "I studied cat communication and computer science."
        skills = extract_skills(tricky_text)
        # 'C' should NOT be extracted just from 'cat' or 'computer' or 'communication'
        self.assertNotIn("C", skills)
        self.assertNotIn("R", skills)

    def test_skill_extractor_positive_matches(self):
        skills = extract_skills(SAMPLE_RESUME_TEXT)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("Node.js", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("Docker", skills)
        self.assertIn("AWS", skills)
        self.assertIn("Git", skills)

    def test_categorized_skills(self):
        categorized = extract_categorized_skills(SAMPLE_RESUME_TEXT)
        self.assertIn("Programming Languages", categorized)
        self.assertIn("Python", categorized["Programming Languages"])
        self.assertIn("Cloud & DevOps", categorized)
        self.assertIn("AWS", categorized["Cloud & DevOps"])

    def test_contact_extraction(self):
        email = extract_email(SAMPLE_RESUME_TEXT)
        self.assertEqual(email, "alex.morgan@email.com")

        phone = extract_phone(SAMPLE_RESUME_TEXT)
        self.assertIn("555", phone)

        name = extract_name(SAMPLE_RESUME_TEXT)
        self.assertEqual(name, "Alex Morgan")

        links = extract_links(SAMPLE_RESUME_TEXT)
        self.assertIn("linkedin", links)
        self.assertIn("github", links)

    def test_sections_detection(self):
        sections = detect_sections(SAMPLE_RESUME_TEXT)
        self.assertTrue(sections["Contact Information"])
        self.assertTrue(sections["Professional Summary / Objective"])
        self.assertTrue(sections["Education Section"])
        self.assertTrue(sections["Experience / Internships"])
        self.assertTrue(sections["Projects Section"])
        self.assertTrue(sections["Technical Skills"])

    def test_scores_calculation(self):
        skills = extract_skills(SAMPLE_RESUME_TEXT)
        education = extract_education(SAMPLE_RESUME_TEXT)
        experience = extract_experience(SAMPLE_RESUME_TEXT)
        sections = detect_sections(SAMPLE_RESUME_TEXT)
        links = extract_links(SAMPLE_RESUME_TEXT)

        analysis = calculate_scores(
            text=SAMPLE_RESUME_TEXT,
            skills=skills,
            education=education,
            experience=experience,
            sections=sections,
            links=links,
            target_role="fullstack"
        )

        scores = analysis["scores"]
        self.assertGreaterEqual(scores["ats"], 70)
        self.assertGreaterEqual(scores["strength"], 70)
        self.assertGreaterEqual(scores["technical"], 60)
        self.assertGreaterEqual(scores["project"], 70)
        self.assertGreaterEqual(scores["job_match"], 60)
        self.assertGreater(len(analysis["matched_skills"]), 3)

    def test_flask_routes(self):
        client = app.test_client()
        # Test Home Route
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Next-Gen Resume Analyzer", resp.data)
        # Ensure no broken markdown backticks exist in rendered HTML
        self.assertNotIn(b"```", resp.data)

        # Test Analyze Route with a real docx document
        from docx import Document
        doc = Document()
        for line in SAMPLE_RESUME_TEXT.strip().splitlines():
            if line.strip():
                doc.add_paragraph(line.strip())
        docx_bytes = io.BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)

        data = {
            "resume": (docx_bytes, "test_resume.docx"),
            "target_role": "fullstack"
        }
        resp = client.post("/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Alex Morgan", resp.data)
        self.assertIn(b"ATS Compatibility", resp.data)
        self.assertIn(b"competencyRadar", resp.data)

    def test_error_cases(self):
        client = app.test_client()

        # 1. No file submitted
        resp = client.post("/analyze", data={}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"No file was uploaded", resp.data)

        # 2. Unsupported extension (e.g. .txt or .png)
        bad_file = (io.BytesIO(b"Hello world"), "test.txt")
        resp = client.post("/analyze", data={"resume": bad_file}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Unsupported file format", resp.data)

        # 3. Empty filename
        empty_file = (io.BytesIO(b""), "")
        resp = client.post("/analyze", data={"resume": empty_file}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Please select a resume file", resp.data)


if __name__ == "__main__":
    unittest.main()
