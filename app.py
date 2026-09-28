import os
import time
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from analyzer.resume_parser import extract_text
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

app = Flask(__name__)
app.secret_key = "resume-analyzer-super-secret-key"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        flash("No file was uploaded. Please select a resume file.", "error")
        return redirect(url_for("home"))

    file = request.files["resume"]

    if file.filename == "":
        flash("Please select a resume file before clicking analyze.", "error")
        return redirect(url_for("home"))

    if not allowed_file(file.filename):
        flash("Unsupported file format! Please upload a PDF (.pdf) or Word document (.docx).", "error")
        return redirect(url_for("home"))

    original_filename = secure_filename(file.filename) or "resume.pdf"
    unique_prefix = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    saved_filename = f"{unique_prefix}_{original_filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)

    try:
        file.save(file_path)
    except Exception as e:
        flash(f"Could not save uploaded file: {str(e)}", "error")
        return redirect(url_for("home"))

    # Extract text from document
    try:
        text = extract_text(file_path)
    except Exception as e:
        flash(f"Failed to read file contents: {str(e)}", "error")
        return redirect(url_for("home"))

    if not text or not text.strip():
        flash("Could not extract any readable text from this file. Ensure the resume is not scanned as an image or password-protected.", "error")
        return redirect(url_for("home"))

    target_role = request.form.get("target_role", "software_engineer").strip()
    job_description = request.form.get("job_description", "").strip()

    # Extract profile attributes
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    categorized_skills = extract_categorized_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    links = extract_links(text)
    sections = detect_sections(text)

    # Calculate multi-dimensional analytics
    analysis = calculate_scores(
        text=text,
        skills=skills,
        education=education,
        experience=experience,
        sections=sections,
        links=links,
        target_role=target_role,
        job_description=job_description
    )

    scores = analysis["scores"]
    reading_time = max(1, round(analysis["word_count"] / 200))

    return render_template(
        "result.html",
        filename=original_filename,
        name=name,
        email=email,
        phone=phone,
        links=links,
        skills=skills,
        categorized_skills=categorized_skills,
        education=education,
        experience=experience,
        sections=sections,
        ats_score=scores["ats"],
        strength_score=scores["strength"],
        technical_score=scores["technical"],
        project_score=scores["project"],
        job_match_score=scores["job_match"],
        target_role=analysis["target_role"],
        matched_skills=analysis["matched_skills"],
        missing_skills=analysis["missing_skills"],
        strengths=analysis["strengths"],
        improvements=analysis["improvements"],
        word_count=analysis["word_count"],
        reading_time=reading_time,
        metrics_found=analysis["metrics_found"],
        action_verbs_found=analysis["action_verbs_found"]
    )


@app.errorhandler(413)
def request_entity_too_large(error):
    flash("The uploaded file is too large! Maximum allowed file size is 16MB.", "error")
    return redirect(url_for("home")), 413


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)