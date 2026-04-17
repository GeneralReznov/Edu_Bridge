from flask import Blueprint, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("university_comparison", __name__)

@bp.route("/university-comparison")
def university_comparison():
    return render_template("university_comparison.html")

@bp.route("/api/compare-universities", methods=["POST"])
def api_compare_universities():
    from app import generate, safe_json_parse
    data = request.json
    universities = data.get("universities", [])
    field = data.get("field", "Computer Science")
    profile = data.get("profile", {})

    if not universities or len(universities) < 2:
        return jsonify({"success": False, "error": "Please provide at least 2 universities to compare"})

    uni_list = "\n".join([f"- {u}" for u in universities])

    prompt = f"""You are an expert graduate admissions counselor. Compare these universities for an Indian student applying for {field}.

Universities to compare:
{uni_list}

Student Profile:
- GPA: {profile.get('gpa', 'Not specified')}
- GRE/GMAT: {profile.get('gre', 'Not specified')}
- Work Experience: {profile.get('work_exp', '0')} years
- Budget: {profile.get('budget', '₹30-40L')}/year
- Career Goal: {profile.get('career_goal', 'Industry job')}

Provide a comprehensive comparison (valid JSON only, no markdown):
{{
  "universities": [
    {{
      "name": "University Name",
      "country": "USA",
      "ranking_qs": 12,
      "ranking_us_news": 8,
      "program": "MS Computer Science",
      "tuition_usd_yr": 45000,
      "living_cost_usd_yr": 18000,
      "total_cost_inr_lakhs": 52,
      "acceptance_rate": "12%",
      "avg_gre": "325",
      "avg_gpa": "3.7",
      "program_duration": "2 years",
      "specializations": ["AI/ML", "Systems", "HCI"],
      "research_strength": 95,
      "industry_connections": 90,
      "career_support": 88,
      "campus_life": 82,
      "diversity_score": 85,
      "placement_rate": "95%",
      "median_salary_usd": 125000,
      "scholarship_availability": "Limited",
      "scholarship_details": "Merit awards $5K-$20K",
      "faculty_highlights": "Prof. X (AI research), Prof. Y (Systems)",
      "notable_alumni": ["Sundar Pichai (Google CEO)", "Alumni 2"],
      "visa_support": "Excellent CPT/OPT support",
      "location_pros": ["Tech hub", "Good job market"],
      "location_cons": ["Expensive", "Cold winters"],
      "application_deadline": "December 15",
      "required_docs": ["SOP", "3 LORs", "CV", "Transcripts"],
      "unique_strengths": ["Strongest CS faculty in systems", "Best industry connections"],
      "weaknesses": ["Very competitive", "Limited funding for MS"],
      "fit_score": 82,
      "fit_reason": "Strong match for your AI/ML interests and GPA"
    }}
  ],
  "comparison_matrix": {{
    "best_roi": "University Name",
    "best_ranking": "University Name",
    "best_for_research": "University Name",
    "best_for_jobs": "University Name",
    "most_affordable": "University Name",
    "highest_salary": "University Name",
    "best_fit_for_profile": "University Name"
  }},
  "head_to_head": [
    {{
      "dimension": "Research Quality",
      "winner": "University A",
      "scores": {{"University A": 92, "University B": 78}},
      "insight": "University A has more NSF-funded research in AI"
    }}
  ],
  "overall_recommendation": {{
    "top_choice": "University Name",
    "reason": "Best combination of ranking, salary, and fit for your profile",
    "apply_to_all": true,
    "strategy": "Apply to all — they serve as Reach, Target, and Safe schools"
  }},
  "cost_comparison": {{
    "cheapest": "University Name",
    "best_value": "University Name",
    "payback_years": {{"University A": 2.5, "University B": 3.1}}
  }}
}}"""

    try:
        result = generate(prompt, temperature=0.5)
        parsed = safe_json_parse(result)
        if not parsed:
            return jsonify({"success": False, "error": "Could not parse AI response. Please try again."})

        # Award XP
        if "profile" not in session:
            session["profile"] = {"xp": 0, "level": 1, "streak": 0, "badges": [], "completed_modules": [], "last_visit": None, "weekly_xp": 0}
        if "university_comparison" not in session["profile"]["completed_modules"]:
            session["profile"]["xp"] = session["profile"].get("xp", 0) + 85
            session["profile"]["completed_modules"].append("university_comparison")
            session.modified = True

        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
