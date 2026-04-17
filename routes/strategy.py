from flask import Blueprint, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("strategy", __name__)

@bp.route("/application-strategy")
def application_strategy():
    return render_template("application_strategy.html")

@bp.route("/api/application-strategy", methods=["POST"])
def api_application_strategy():
    from app import generate, safe_json_parse
    from services.application_strategy import build_strategy_prompt

    data = request.json
    prompt = build_strategy_prompt(data)

    try:
        result = generate(prompt, temperature=0.6)
        parsed = safe_json_parse(result)
        if not parsed:
            return jsonify({"success": False, "error": "Could not parse AI response. Please retry."})

        if "profile" not in session:
            session["profile"] = {"xp": 0, "level": 1, "streak": 0, "badges": [], "completed_modules": [], "last_visit": None, "weekly_xp": 0}

        if "application_strategy" not in session["profile"]["completed_modules"]:
            session["profile"]["xp"] = session["profile"].get("xp", 0) + 110
            session["profile"]["level"] = 1 + session["profile"]["xp"] // 500
            session["profile"]["completed_modules"].append("application_strategy")
            if not any(b.get("id") == "application_strategy" for b in session["profile"]["badges"]):
                session["profile"]["badges"].append({"id": "application_strategy", "name": "🎯 Strategist", "desc": "Built a complete application strategy"})
        session.modified = True

        return jsonify({"success": True, "data": parsed, "xp_gained": 110})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@bp.route("/peer-benchmarks")
def peer_benchmarks():
    return render_template("peer_benchmarks.html")

@bp.route("/api/peer-benchmark", methods=["POST"])
def api_peer_benchmark():
    from app import generate, safe_json_parse
    from services.peer_benchmarking import benchmark_profile

    data = request.json

    # Local computation (no AI needed for basic benchmarking)
    bench = benchmark_profile(data)

    # Use AI for enhanced narrative insights
    from app import GEMINI_AVAILABLE
    ai_insights = None
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""You are an expert grad admissions consultant. Give 3 sharp, personalized insights for an Indian student.

Student percentile rank: {bench['overall_percentile']}th (out of {bench['cohort_size']:,} Indian applicants)
Profile tier: {bench['tier'].title()}
Field: {bench['field']}
GPA percentile: {bench['dimensions'][0]['user_pct']}th

Respond with valid JSON only (no markdown):
{{
  "key_insights": [
    "Insight 1 — specific and actionable",
    "Insight 2 — specific and actionable",
    "Insight 3 — specific and actionable"
  ],
  "competitive_summary": "One paragraph about their competitive standing",
  "immediate_actions": ["action1", "action2", "action3"],
  "acceptance_probability": {{
    "top_10": 12,
    "top_25": 35,
    "top_50": 68,
    "top_100": 88
  }}
}}"""
            result = generate(prompt, temperature=0.5)
            ai_insights = safe_json_parse(result)
        except:
            pass

    if "profile" not in session:
        session["profile"] = {"xp": 0, "level": 1, "streak": 0, "badges": [], "completed_modules": [], "last_visit": None, "weekly_xp": 0}
    if "peer_benchmarks" not in session["profile"]["completed_modules"]:
        session["profile"]["xp"] = session["profile"].get("xp", 0) + 75
        session["profile"]["level"] = 1 + session["profile"]["xp"] // 500
        session["profile"]["completed_modules"].append("peer_benchmarks")
        if not any(b.get("id") == "peer_benchmarks" for b in session["profile"]["badges"]):
            session["profile"]["badges"].append({"id": "peer_benchmarks", "name": "📊 Benchmarker", "desc": "Compared profile against 1,247 Indian students"})
    session.modified = True

    return jsonify({
        "success": True,
        "data": {**bench, "ai_insights": ai_insights},
        "xp_gained": 75
    })
