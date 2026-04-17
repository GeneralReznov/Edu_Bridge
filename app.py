import os
import json
import re
import sys
import time
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

# Add app root to path so blueprints can import from services/
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "studyabroad-secret-2024")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"Gemini setup error: {e}")

PRIMARY_MODEL   = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
MODEL = PRIMARY_MODEL

def generate(prompt, temperature=0.7):
    if not GEMINI_AVAILABLE:
        raise Exception("Gemini AI not available. Check API key.")

    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    last_error = None

    for model in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=8192
                    )
                )
                return response.text
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_overloaded = "503" in err_str or "unavailable" in err_str or "overload" in err_str or "quota" in err_str or "429" in err_str
                if is_overloaded:
                    wait = (attempt + 1) * 2
                    print(f"[Gemini] {model} overloaded (attempt {attempt+1}). Waiting {wait}s...")
                    time.sleep(wait)
                    continue
                break

    raise Exception(f"All Gemini models unavailable. Last error: {last_error}")

def safe_json_parse(text):
    try:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except Exception:
        return None

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/career-navigator")
def career_navigator():
    return render_template("career_navigator.html")

@app.route("/roi-calculator")
def roi_calculator():
    return render_template("roi_calculator.html")

@app.route("/admission-predictor")
def admission_predictor():
    return render_template("admission_predictor.html")

@app.route("/timeline-generator")
def timeline_generator():
    return render_template("timeline_generator.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/loan-planner")
def loan_planner():
    return render_template("loan_planner.html")

@app.route("/gamification")
def gamification():
    return render_template("gamification.html")

# ── API: AI Career Navigator ──────────────────────────────────────────────────
@app.route("/api/career-navigate", methods=["POST"])
def api_career_navigate():
    data = request.json
    field = data.get("field", "")
    gpa = data.get("gpa", "")
    budget = data.get("budget", "")
    preference = data.get("preference", "")
    work_exp = data.get("work_exp", "0")
    gre_score = data.get("gre_score", "")
    toefl_score = data.get("toefl_score", "")
    research = data.get("research", "none")
    interests = data.get("interests", "")
    career_goal = data.get("career_goal", "")

    prompt = f"""You are an AI Career Navigator for Indian students planning postgraduate education abroad.

Student Profile:
- Field: {field}
- GPA/CGPA: {gpa}
- Budget: {budget} per year
- Country preference: {preference if preference else 'Open to all'}
- Work experience: {work_exp} years
- GRE/GMAT: {gre_score if gre_score else 'Not taken'}
- TOEFL/IELTS: {toefl_score if toefl_score else 'Not taken'}
- Research: {research}
- Specific interests: {interests if interests else 'Not specified'}
- Career goal: {career_goal if career_goal else 'Not specified'}

Provide a comprehensive JSON response (valid JSON only, no markdown, no extra text):
{{
  "overall_profile_score": 78,
  "summary": "One sentence describing the profile strength",
  "profile_tier": "Competitive applicant — strong for top-50 programs",
  "recommended_countries": [
    {{
      "country": "USA",
      "fit_score": 88,
      "reason": "Detailed reason why this country fits the profile",
      "avg_cost_usd": 55000,
      "avg_duration": "2 years",
      "visa_difficulty": "Medium",
      "post_study_work": "OPT: 1-3 years (STEM extension available)",
      "pros": ["Best ROI for CS/engineering", "Huge job market", "OPT/STEM extension"]
    }}
  ],
  "recommended_universities": [
    {{
      "name": "University of Michigan",
      "country": "USA",
      "program": "MS Computer Science",
      "tier": "Target",
      "match_score": 82,
      "tuition_usd": 50000,
      "acceptance_rate": 15,
      "avg_gpa": 3.6,
      "fit_reason": "Strong ML faculty, good acceptance rate for profile",
      "notable_alumni": "Larry Page, founders of major tech companies"
    }}
  ],
  "career_paths": [
    {{
      "role": "Software Engineer",
      "avg_salary_usd": 125000,
      "salary_5yr": 165000,
      "growth_outlook": "Excellent",
      "top_companies": ["Google", "Meta", "Microsoft", "Apple"],
      "required_skills": ["Python", "System Design", "DSA", "Cloud"]
    }}
  ],
  "skill_gaps": [
    {{
      "skill": "Machine Learning",
      "importance": "High",
      "current_level": 45,
      "resources": ["fast.ai", "Coursera DeepLearning.AI", "Kaggle competitions"]
    }}
  ],
  "action_plan": [
    {{
      "period": "Month 1-2",
      "focus": "Test Preparation",
      "tasks": ["Register for GRE", "Start GRE prep with Manhattan Prep", "Take diagnostic test"]
    }},
    {{
      "period": "Month 3-4",
      "focus": "University Research",
      "tasks": ["Shortlist 12 universities", "Email professors of interest", "Review program requirements"]
    }},
    {{
      "period": "Month 5-6",
      "focus": "Application Prep",
      "tasks": ["Draft SOP v1", "Request 3 LORs", "Prepare resume/CV"]
    }}
  ]
}}

Return top 3 countries, top 6 universities (2 Reach, 2 Target, 2 Safe), top 4 career paths, 4-5 skill gaps, and a 6-step action plan. Be specific and realistic for an Indian student."""

    try:
        text = generate(prompt)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response. Please try again."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: ROI Calculator ────────────────────────────────────────────────────────
@app.route("/api/roi-calculate", methods=["POST"])
def api_roi_calculate():
    data = request.json
    program = data.get("program", "")
    university = data.get("university", "")
    country = data.get("country", "USA")
    tuition = float(data.get("tuition", 0))
    living = float(data.get("living", 15000))
    duration = float(data.get("duration", 2))
    current_salary = float(data.get("current_salary", 0))
    scholarship = float(data.get("scholarship", 0))
    specialization = data.get("specialization", "")

    total_cost = (tuition + living) * duration - scholarship
    total_cost_inr = int(total_cost * 84)

    prompt = f"""You are a financial advisor for Indian students studying abroad.

Program: {program} at {university}, {country}
Tuition: ${tuition:,.0f}/year for {duration} years
Living costs: ${living:,.0f}/year
Scholarship/funding: ${scholarship:,.0f} total
Total estimated investment: ${total_cost:,.0f} (₹{total_cost_inr:,})
Current salary in India: ₹{current_salary:,.0f}/year
Specialization: {specialization if specialization else 'General'}

Provide a complete financial ROI analysis JSON (valid JSON only, no markdown, no extra text):
{{
  "roi_analysis": {{
    "total_investment_usd": {int(total_cost)},
    "total_investment_inr": {total_cost_inr},
    "expected_starting_salary_usd": 105000,
    "expected_starting_salary_inr": 8820000,
    "payback_period_years": 3.2,
    "10yr_earnings_gain_usd": 480000,
    "roi_percentage": 320,
    "wealth_at_20yr": 850000
  }},
  "salary_trajectory": [
    {{"year": 1, "salary_usd": 105000}},
    {{"year": 2, "salary_usd": 112000}},
    {{"year": 3, "salary_usd": 122000}},
    {{"year": 4, "salary_usd": 133000}},
    {{"year": 5, "salary_usd": 145000}},
    {{"year": 6, "salary_usd": 155000}},
    {{"year": 7, "salary_usd": 163000}},
    {{"year": 8, "salary_usd": 172000}},
    {{"year": 9, "salary_usd": 181000}},
    {{"year": 10, "salary_usd": 192000}}
  ],
  "comparison_without_degree": [
    {{"year": 1, "salary_usd": 18000}},
    {{"year": 2, "salary_usd": 20000}},
    {{"year": 3, "salary_usd": 22000}},
    {{"year": 4, "salary_usd": 24000}},
    {{"year": 5, "salary_usd": 27000}},
    {{"year": 6, "salary_usd": 29000}},
    {{"year": 7, "salary_usd": 32000}},
    {{"year": 8, "salary_usd": 35000}},
    {{"year": 9, "salary_usd": 38000}},
    {{"year": 10, "salary_usd": 42000}}
  ],
  "scenarios": [
    {{
      "name": "Conservative",
      "salary_growth": "3%/yr",
      "total_gain_10yr": 280000,
      "note": "Slower career trajectory, non-FAANG companies"
    }},
    {{
      "name": "Base Case",
      "salary_growth": "8%/yr",
      "total_gain_10yr": 480000,
      "note": "Industry average growth, mid-tier tech companies"
    }},
    {{
      "name": "Optimistic",
      "salary_growth": "15%/yr",
      "total_gain_10yr": 720000,
      "note": "FAANG or top startup, fast promotion track"
    }}
  ],
  "key_insights": [
    "Payback period of ~3 years is excellent for this field",
    "20-year wealth advantage of $850K makes this a strong investment",
    "With OPT/H1B, US-based salary is 6-8x higher than India equivalent"
  ],
  "recommendation": "Highly recommended. The ROI for this program is exceptional."
}}

Use real salary data for {program} graduates in {country}. Be specific and data-driven."""

    try:
        text = generate(prompt)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: Admission Predictor ───────────────────────────────────────────────────
@app.route("/api/predict-admission", methods=["POST"])
def api_predict_admission():
    data = request.json
    gpa = float(data.get("gpa", 3.0))
    gre = int(data.get("gre", 310))
    gre_verbal = int(data.get("gre_verbal", 155))
    gre_quant = int(data.get("gre_quant", 155))
    gre_awa = float(data.get("gre_awa", 3.5))
    toefl = int(data.get("toefl", 95))
    work_exp = int(data.get("work_exp", 0))
    research = data.get("research", "none")
    publications = int(data.get("publications", 0))
    internships = int(data.get("internships", 0))
    sop_quality = data.get("sop_quality", "basic")
    lor_quality = data.get("lor_quality", "good")
    extracurriculars = data.get("extracurriculars", "none")
    university = data.get("university", "")
    program = data.get("program", "")

    prompt = f"""You are an admission expert for top global universities with 15+ years experience.

Applicant Profile:
- GPA: {gpa}/4.0
- GRE Total: {gre}/340 (V:{gre_verbal}, Q:{gre_quant}, AWA:{gre_awa})
- TOEFL: {toefl}/120
- Work Experience: {work_exp} years
- Research: {research}
- Publications: {publications}
- Internships: {internships}
- SOP Quality: {sop_quality}
- LOR Quality: {lor_quality}
- Extracurriculars: {extracurriculars}
- Target University: {university if university else 'General assessment'}
- Program: {program if program else 'Graduate program'}

Provide a detailed JSON admission analysis (valid JSON only, no markdown, no extra text):
{{
  "overall_admission_probability": 72,
  "strength_score": 78,
  "competitiveness_rank": "Top 25th percentile",
  "recommended_unis_count": 10,
  "verdict": "2-sentence overall verdict about the profile",
  "profile_breakdown": {{
    "academic": {{
      "score": 82,
      "comment": "GPA is competitive for top-50 programs",
      "benchmark": "Top programs avg: 3.7 GPA"
    }},
    "test_scores": {{
      "score": 75,
      "comment": "GRE score is at the median for target schools",
      "benchmark": "Competitive range: 320-330 for top programs"
    }},
    "experience": {{
      "score": 65,
      "comment": "Work experience adds professional perspective",
      "benchmark": "Target programs avg: 1-2 years preferred"
    }},
    "research": {{
      "score": 70,
      "comment": "Research background shows academic curiosity",
      "benchmark": "PhD programs require strong research; MS programs value it"
    }},
    "application_materials": {{
      "score": 68,
      "comment": "SOP and LOR are critical differentiators",
      "benchmark": "Strong LORs from professors can boost chances by 15-20%"
    }}
  }},
  "university_tiers": [
    {{
      "tier": "Reach",
      "examples": ["MIT CSAIL", "Stanford CS", "CMU SCS"],
      "probability": 12
    }},
    {{
      "tier": "Target",
      "examples": ["UMass Amherst", "Purdue", "UT Dallas", "NCSU"],
      "probability": 65
    }},
    {{
      "tier": "Safe",
      "examples": ["ASU", "Stevens Tech", "UTA", "Northeastern"],
      "probability": 92
    }}
  ],
  "specific_university_prediction": {{
    "university": "{university if university else ''}",
    "probability": 58,
    "positive_factors": ["Strong GPA meets cutoff", "Research aligns with faculty interests"],
    "negative_factors": ["GRE slightly below median", "Limited publications"],
    "advice": "Apply Early Action if available. Email specific professors before applying."
  }},
  "improvement_areas": [
    {{
      "area": "GRE Score",
      "current": "{gre}",
      "target": "325+",
      "impact": "Could boost probability by 10-15%",
      "how_to": "Take GRE again after 4 weeks of targeted prep. Focus on Quant (165+)"
    }},
    {{
      "area": "Research Experience",
      "current": "{research}",
      "target": "1 published paper or conference proceedings",
      "impact": "Significantly differentiates from other applicants",
      "how_to": "Reach out to professors for research assistant positions"
    }}
  ],
  "sos_tips": [
    "Open with a specific research problem or professional challenge you faced — avoid 'since childhood' openers",
    "Mention specific professors at each university whose research aligns with your interests",
    "Quantify your achievements — 'Improved system performance by 40%' beats 'improved system performance'",
    "Keep SOP under 1000 words unless specified otherwise — admissions officers read hundreds per day",
    "End with a clear connection between this program and your specific 5-year career goal"
  ]
}}

{"Include specific_university_prediction with detailed analysis for " + university if university else "Set specific_university_prediction fields to empty strings/zeroes since no specific university was given."}
Be realistic and honest about the admission chances."""

    try:
        text = generate(prompt)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: Application Timeline Generator ───────────────────────────────────────
@app.route("/api/generate-timeline", methods=["POST"])
def api_generate_timeline():
    data = request.json
    intake = data.get("intake", "Fall 2026")
    program = data.get("program", "MS Computer Science")
    country = data.get("country", "USA")
    current_status = data.get("current_status", "Just starting")
    num_apps = int(data.get("num_apps", 10))
    deadline_type = data.get("deadline_type", "regular")
    has_gre = data.get("has_gre", False)
    has_toefl = data.get("has_toefl", False)
    sop_done = data.get("sop_done", False)
    lors_done = data.get("lors_done", False)

    prompt = f"""You are an expert admission consultant creating a detailed application timeline.

Student Goal:
- Target Intake: {intake}
- Program: {program}
- Country: {country}
- Current Status: {current_status}
- Number of universities: {num_apps}
- Deadline type: {deadline_type}
- GRE/GMAT taken: {has_gre}
- TOEFL/IELTS taken: {has_toefl}
- SOP drafted: {sop_done}
- LORs arranged: {lors_done}
- Today's date: {datetime.now().strftime("%B %Y")}

Create a comprehensive timeline JSON (valid JSON only, no markdown, no extra text):
{{
  "total_months": 10,
  "success_probability": 82,
  "key_advice": "Personalized 2-sentence strategic advice for this student.",
  "phases": [
    {{"name": "Preparation", "months": "Month 1-2"}},
    {{"name": "Test Prep", "months": "Month 2-4"}},
    {{"name": "Research", "months": "Month 3-5"}},
    {{"name": "Application", "months": "Month 5-8"}},
    {{"name": "Visa", "months": "Month 9-10"}}
  ],
  "critical_deadlines": [
    {{
      "date": "September 2025",
      "deadline": "GRE exam date",
      "consequence": "Applications won't be competitive without a strong GRE score"
    }},
    {{
      "date": "November 2025",
      "deadline": "Early Action deadline for top programs",
      "consequence": "Missing EA means competing in larger Regular pool"
    }}
  ],
  "timeline": [
    {{
      "month": "May 2025",
      "phase": "Preparation",
      "milestone": "Study plan finalized",
      "tasks": [
        {{
          "task": "Register for GRE exam",
          "priority": "High",
          "duration": "1 day",
          "tips": "Book 3+ months in advance for preferred dates"
        }},
        {{
          "task": "Create university research spreadsheet",
          "priority": "High",
          "duration": "3 days",
          "tips": "Track: name, deadline, GRE req, tuition, acceptance rate"
        }},
        {{
          "task": "Request official transcripts",
          "priority": "Medium",
          "duration": "1-2 weeks",
          "tips": "Some universities take weeks — start early"
        }}
      ]
    }}
  ]
}}

Create a realistic 8-12 month timeline with 3-5 tasks per month. Adjust based on what's already done ({{"GRE: " + ("done" if has_gre else "needed")}}, {{"TOEFL: " + ("done" if has_toefl else "needed")}}, {{"SOP: " + ("started" if sop_done else "not started")}}, {{"LORs: " + ("arranged" if lors_done else "not arranged")}}). Use phases: Preparation, Test Prep, Research, Application, Visa, Enrollment."""

    try:
        text = generate(prompt)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: AI Chatbot ────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    message = data.get("message", "")
    history = data.get("history", [])
    context = data.get("context", "")

    system_prompt = f"""You are EduMentor, an expert AI advisor for Indian students planning postgraduate education abroad. You are warm, knowledgeable, and deeply practical.

You help with:
- University selection and shortlisting for MS, MBA, PhD programs
- Application essays and SOPs (Statement of Purpose)
- Visa guidance (F-1, UK Student visa, Canada study permit, German student visa, Australia 500)
- Education loans (SBI, HDFC Credila, Avanse, Prodigy Finance, Auxilo, Incred)
- Scholarships (Fulbright, Commonwealth, DAAD, Chevening, Erasmus Mundus, Inlaks, AAUW)
- GRE/TOEFL/GMAT/IELTS strategies and preparation resources
- Career advice post-MS/MBA: OPT/CPT, H1B lottery, PGWP, PR pathways
- Financial planning: budgeting, on-campus jobs, scholarships, tax savings

{f"Student Profile: {context}" if context else ""}

Formatting rules:
- Use **bold** for key terms and numbers
- Use bullet points (- item) for lists
- Use numbered lists for steps
- Be specific with numbers, dates, and deadlines
- Keep responses focused and under 350 words unless the question demands depth
- Be encouraging but honest about challenges"""

    try:
        contents = []
        # Add system context to first message
        sys_content = types.Content(role="user", parts=[types.Part(text=f"[System] {system_prompt}\n\nPlease acknowledge you understand your role.")])
        model_ack = types.Content(role="model", parts=[types.Part(text="Understood! I'm EduMentor AI, ready to help Indian students navigate their study abroad journey with expert guidance on universities, applications, visas, loans, and careers.")])
        
        if not history:
            contents = [sys_content, model_ack]
        else:
            contents = [sys_content, model_ack]
            for msg in history[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.75, max_output_tokens=1200)
        )
        
        return jsonify({
            "success": True,
            "data": {
                "response": response.text.strip()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: Loan Eligibility Estimator ───────────────────────────────────────────
@app.route("/api/loan-eligibility", methods=["POST"])
def api_loan_eligibility():
    data = request.json
    program = data.get("program", "")
    total_cost = float(data.get("total_cost", 0))
    loan_amount = float(data.get("loan_amount", total_cost * 0.8))
    family_income = float(data.get("family_income", 0))
    co_income = float(data.get("co_income", 0))
    employment = data.get("employment", "Salaried")
    collateral = data.get("collateral", "none")
    collateral_value = float(data.get("collateral_value", 0))
    cibil = data.get("cibil", "700-749")
    existing_emi = float(data.get("existing_emi", 0))
    academics = data.get("academics", "")

    combined_income = family_income + co_income
    loan_cr = loan_amount / 100000

    prompt = f"""You are a senior loan advisor for Indian education loans with expertise across all major lenders.

Student Loan Application:
- Program: {program}
- Total Program Cost: ₹{total_cost:,.0f}
- Loan Required: ₹{loan_amount:,.0f} ({loan_cr:.1f} Lakhs)
- Family Annual Income: ₹{family_income:,.0f}
- Co-applicant Income: ₹{co_income:,.0f}
- Combined Income: ₹{combined_income:,.0f}
- Employment Type: {employment}
- Collateral: {collateral} (Value: ₹{collateral_value:,.0f})
- CIBIL Score: {cibil}
- Existing EMI Obligations: ₹{existing_emi:,.0f}/month
- Academic Achievements: {academics if academics else 'Not specified'}

Provide a comprehensive loan eligibility analysis (valid JSON only, no markdown, no extra text):
{{
  "overall_eligibility": {{
    "score": 78,
    "status": "Highly Eligible",
    "summary": "Strong profile with good income and CIBIL score. Multiple lenders will compete for your business.",
    "max_eligible_amount": 4500000
  }},
  "lenders": [
    {{
      "name": "SBI Global Ed-Vantage",
      "type": "PSU Bank",
      "interest_rate": "10.15",
      "max_amount": 15000000,
      "max_tenure": "15 years",
      "collateral_required": "Above ₹7.5L",
      "approval_time": "3-4 weeks",
      "best_for": "Lowest rate, government-backed security",
      "recommended": true
    }},
    {{
      "name": "HDFC Credila",
      "type": "NBFC",
      "interest_rate": "11.5",
      "max_amount": 15000000,
      "max_tenure": "15 years",
      "collateral_required": "None (for top universities)",
      "approval_time": "5-7 days",
      "best_for": "Fast processing, flexible for top US/UK universities",
      "recommended": false
    }},
    {{
      "name": "Axis Bank Education Loan",
      "type": "Private Bank",
      "interest_rate": "13.7",
      "max_amount": 7500000,
      "max_tenure": "15 years",
      "collateral_required": "Above ₹4L",
      "approval_time": "1-2 weeks",
      "best_for": "Good for students with limited collateral",
      "recommended": false
    }},
    {{
      "name": "Avanse Financial Services",
      "type": "NBFC",
      "interest_rate": "11.0",
      "max_amount": 10000000,
      "max_tenure": "15 years",
      "collateral_required": "None for top 200 global universities",
      "approval_time": "5-7 days",
      "best_for": "Pre-admission loans, faster processing than banks",
      "recommended": false
    }},
    {{
      "name": "Prodigy Finance",
      "type": "International NBFC",
      "interest_rate": "11.9",
      "max_amount": 10000000,
      "max_tenure": "10 years",
      "collateral_required": "None",
      "approval_time": "2-3 days",
      "best_for": "No co-applicant required, ideal for top global programs",
      "recommended": false
    }},
    {{
      "name": "ICICI Bank Education Loan",
      "type": "Private Bank",
      "interest_rate": "10.5",
      "max_amount": 10000000,
      "max_tenure": "15 years",
      "collateral_required": "Above ₹7.5L",
      "approval_time": "1-2 weeks",
      "best_for": "Competitive rate with wide branch network",
      "recommended": false
    }},
    {{
      "name": "Auxilo Finserve",
      "type": "NBFC",
      "interest_rate": "12.5",
      "max_amount": 7500000,
      "max_tenure": "14 years",
      "collateral_required": "None for eligible profiles",
      "approval_time": "3-5 days",
      "best_for": "Good for profiles with limited credit history",
      "recommended": false
    }}
  ],
  "recommended_lender": {{
    "name": "SBI Global Ed-Vantage",
    "reason": "Lowest interest rate among all lenders, government backing, and covers full program cost. Best for profiles with collateral.",
    "interest_rate": "10.15",
    "monthly_emi": 42500,
    "total_repayment": 5100000,
    "tax_savings": 480000,
    "steps": [
      "Visit nearest SBI branch with all documents",
      "Submit loan application form with academic documents",
      "Bank sends representative for collateral valuation",
      "Loan sanction within 3-4 weeks of complete application"
    ]
  }},
  "documents_required": [
    "Admission letter / I-20 / CAS from university",
    "Fee structure / cost estimate from university",
    "Last 3 years ITR of co-applicant",
    "Last 6 months bank statements (all accounts)",
    "Co-applicant salary slips (last 3 months)",
    "Property documents for collateral (if applicable)",
    "KYC: Aadhaar + PAN of student and co-applicant",
    "Academic documents: 10th, 12th, graduation marksheets",
    "GRE/TOEFL score cards",
    "Passport copy"
  ],
  "approval_tips": [
    "Apply to 2-3 lenders simultaneously — parallel applications increase approval speed",
    "Keep CIBIL score above 750 — avoid new credit applications 3 months before loan",
    "Prepare a strong admission letter mentioning scholarship if any — it improves approval odds",
    "SBI offers 0.5% concession for female students under PM Vidyalakshmi scheme",
    "Tax savings under Section 80E have no cap — save the full interest paid each year on ITR"
  ]
}}

Adjust interest rates and approval odds based on CIBIL score {cibil} and collateral {collateral}. Make the recommendation specific to this profile."""

    try:
        text = generate(prompt)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: EMI Calculator ────────────────────────────────────────────────────────
@app.route("/api/emi-calculate", methods=["POST"])
def api_emi_calculate():
    data = request.json
    principal = float(data.get("principal", 0))
    rate = float(data.get("rate", 10)) / 12 / 100
    tenure_months = int(data.get("tenure_years", 10)) * 12
    moratorium_months = int(data.get("moratorium_months", 24))

    if rate == 0 or tenure_months == 0:
        return jsonify({"success": False, "error": "Invalid inputs"}), 400

    interest_during_moratorium = principal * (data.get("rate", 10) / 100 / 12) * moratorium_months
    total_principal = principal + interest_during_moratorium

    emi = (total_principal * rate * (1 + rate) ** tenure_months) / ((1 + rate) ** tenure_months - 1)
    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    schedule = []
    balance = total_principal
    for month in range(1, min(tenure_months + 1, 13)):
        interest_comp = balance * rate
        principal_comp = emi - interest_comp
        balance -= principal_comp
        schedule.append({
            "month": month,
            "emi": round(emi, 2),
            "principal": round(principal_comp, 2),
            "interest": round(interest_comp, 2),
            "balance": round(max(balance, 0), 2)
        })

    return jsonify({
        "success": True,
        "data": {
            "emi": round(emi, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "interest_during_moratorium": round(interest_during_moratorium, 2),
            "effective_principal": round(total_principal, 2),
            "schedule": schedule
        }
    })


# ── API: Generate SOP Outline + Draft ─────────────────────────────────────────
@app.route("/api/sop-outline", methods=["POST"])
def api_sop_outline():
    data = request.json
    program = data.get("program", "")
    background = data.get("background", "")
    experience = data.get("experience", "")
    research = data.get("research", "")
    why_program = data.get("why_program", "")
    goal_short = data.get("goal_short", "")
    goal_long = data.get("goal_long", "")
    length = int(data.get("length", 800))
    tone = data.get("tone", "passionate")

    prompt = f"""You are an expert SOP writer who has helped 1000+ Indian students get into top programs worldwide.

Student Info:
- Program: {program}
- Academic Background: {background}
- Work/Internship Experience: {experience if experience else 'Not specified'}
- Research/Projects: {research if research else 'Not specified'}
- Why This Program: {why_program}
- Short-term Goal: {goal_short if goal_short else 'Not specified'}
- Long-term Goal: {goal_long if goal_long else 'Not specified'}
- Target Length: {length} words
- Tone: {tone}

Generate a complete SOP package (valid JSON only, no markdown, no extra text):
{{
  "quality_score": 82,
  "quality_assessment": "Strong narrative with specific motivations. Research and goals are well-aligned with the program.",
  "structure": [
    {{
      "section": "Opening Hook",
      "content": "Start with a defining moment or specific problem that drove you to this field",
      "word_count": 100,
      "key_points": ["Be specific, not generic", "Create immediate interest", "Connect to your journey"]
    }},
    {{
      "section": "Academic Foundation",
      "content": "Describe your academic journey, key courses, GPA, and how they prepared you",
      "word_count": 150,
      "key_points": ["Highlight relevant coursework", "Mention GPA if strong", "Connect to program requirements"]
    }},
    {{
      "section": "Professional Experience",
      "content": "Detail internships, work experience, and key professional achievements with numbers",
      "word_count": 150,
      "key_points": ["Use quantified achievements", "Show progression", "Connect to graduate study"]
    }},
    {{
      "section": "Research & Projects",
      "content": "Highlight research work, publications, or significant projects",
      "word_count": 100,
      "key_points": ["Be technically specific", "Show intellectual curiosity", "Mention methodologies used"]
    }},
    {{
      "section": "Why This Program",
      "content": "Specific reasons for choosing this exact program and university",
      "word_count": 150,
      "key_points": ["Name specific faculty/labs", "Mention unique courses", "Show you've done research"]
    }},
    {{
      "section": "Goals & Vision",
      "content": "Clear short and long-term career goals and how this degree enables them",
      "word_count": 100,
      "key_points": ["Be specific about roles", "Connect degree to goals", "Show ambition and realism"]
    }}
  ],
  "draft": "Write a complete {length}-word SOP draft in {tone} tone here. This should be a full, ready-to-submit draft that incorporates all the student's information. Start with a compelling hook. Each paragraph should flow naturally into the next. End with a forward-looking conclusion.",
  "common_mistakes": [
    "Starting with 'Since childhood, I have been fascinated by...' — too clichéd",
    "Being too generic — every statement should be unique to you",
    "Not mentioning specific professors or labs at the university",
    "Exceeding the word limit — admissions officers read hundreds of SOPs",
    "Repeating what's already in your CV — SOP should add context, not repeat",
    "Using passive voice excessively — active voice is more compelling"
  ],
  "power_phrases": [
    "quantifiable impact",
    "bridging the gap between",
    "interdisciplinary approach",
    "scalable solution",
    "research-driven perspective",
    "industry-academic synergy"
  ]
}}

IMPORTANT: The "draft" field must contain the actual complete SOP text (not placeholder text), written specifically for this student's background. Make it compelling and personal."""

    try:
        text = generate(prompt, temperature=0.9)
        result = safe_json_parse(text)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": "Could not parse AI response."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── API: User Profile / Gamification ──────────────────────────────────────────
@app.route("/api/profile/update", methods=["POST"])
def api_profile_update():
    data = request.json
    if "profile" not in session:
        session["profile"] = {
            "xp": 0, "level": 1, "streak": 0,
            "badges": [], "completed_modules": [], "last_visit": None,
            "weekly_xp": 0, "weekly_reset": datetime.now().strftime("%Y-W%U"),
            "challenges": {}
        }

    profile = session["profile"]
    action = data.get("action", "")
    xp_rewards = {
        "career_navigator": 100,
        "roi_calculator": 80,
        "admission_predictor": 90,
        "timeline_generator": 70,
        "chatbot": 20,
        "chat": 20,
        "loan_planner": 120,
        "sop_outline": 85
    }

    xp_gained = xp_rewards.get(action, 10)
    if action not in profile["completed_modules"]:
        profile["xp"] += xp_gained
        profile["level"] = 1 + profile["xp"] // 500
        profile["completed_modules"].append(action)
    else:
        xp_gained = 5  # Repeat usage bonus

    # Weekly XP tracking
    current_week = datetime.now().strftime("%Y-W%U")
    if profile.get("weekly_reset") != current_week:
        profile["weekly_xp"] = 0
        profile["weekly_reset"] = current_week
    profile["weekly_xp"] = profile.get("weekly_xp", 0) + xp_gained

    badge_rules = {
        "career_navigator": ("🧭 Navigator", "Explored AI Career Navigator"),
        "roi_calculator": ("📈 ROI Pro", "Calculated Education ROI"),
        "admission_predictor": ("🎯 Predictor", "Used Admission Predictor"),
        "loan_planner": ("💰 Finance Wizard", "Planned Education Loan"),
        "timeline_generator": ("📅 Planner", "Generated Application Timeline"),
        "sop_outline": ("✍️ SOP Master", "Generated AI SOP Draft"),
        "chatbot": ("🤖 AI User", "Chatted with EduMentor"),
    }
    if action in badge_rules:
        badge = {"id": action, "name": badge_rules[action][0], "desc": badge_rules[action][1]}
        if not any(b.get("id") == action for b in profile["badges"]):
            profile["badges"].append(badge)

    # Special achievement badges
    if len(profile["completed_modules"]) >= 5 and not any(b.get("id") == "all_rounder" for b in profile["badges"]):
        profile["badges"].append({"id": "all_rounder", "name": "🌟 All-Rounder", "desc": "Used all 5 major tools"})
    if profile["xp"] >= 500 and not any(b.get("id") == "level2" for b in profile["badges"]):
        profile["badges"].append({"id": "level2", "name": "⚡ Level 2 Scholar", "desc": "Reached 500 XP"})

    today = datetime.now().strftime("%Y-%m-%d")
    if profile["last_visit"] != today:
        profile["streak"] = profile.get("streak", 0) + 1
        profile["last_visit"] = today

    session["profile"] = profile
    session.modified = True

    return jsonify({"success": True, "profile": profile, "xp_gained": xp_gained})


@app.route("/api/profile/get", methods=["GET"])
def api_profile_get():
    profile = session.get("profile", {
        "xp": 0, "level": 1, "streak": 0,
        "badges": [], "completed_modules": [], "last_visit": None,
        "weekly_xp": 0
    })
    return jsonify({"success": True, "profile": profile})


# ── Register Blueprints ───────────────────────────────────────────────────────
from routes.university_comparison import bp as university_comparison_bp
from routes.loan import bp as loan_bp
from routes.analytics import bp as analytics_bp
from routes.gamification import bp as gamification_bp
from routes.strategy import bp as strategy_bp
from routes.university_data import bp as university_data_bp
from routes.feedback import bp as feedback_bp
from routes.learning_path import bp as learning_path_bp
from routes.documents import bp as documents_bp
from routes.referral import bp as referral_bp
from routes.community import bp as community_bp
from routes.admission_tracking import bp as admission_tracking_bp
from routes.interview_prep import bp as interview_prep_bp

app.register_blueprint(university_comparison_bp)
app.register_blueprint(loan_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(gamification_bp)
app.register_blueprint(strategy_bp)
app.register_blueprint(university_data_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(learning_path_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(referral_bp)
app.register_blueprint(community_bp)
app.register_blueprint(admission_tracking_bp)
app.register_blueprint(interview_prep_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
