from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("analytics", __name__)

@bp.route("/analytics")
def analytics_dashboard():
    return render_template("analytics_dashboard.html")

@bp.route("/api/analytics/data", methods=["GET"])
def api_analytics_data():
    from services.adaptive_learning import get_adaptive_recommendations
    profile = session.get("profile", {
        "xp": 0, "level": 1, "streak": 0,
        "badges": [], "completed_modules": [],
        "last_visit": None, "weekly_xp": 0,
        "activity_log": []
    })

    completed = profile.get("completed_modules", [])
    xp = profile.get("xp", 0)
    badges = profile.get("badges", [])
    streak = profile.get("streak", 0)
    weekly_xp = profile.get("weekly_xp", 0)
    level = profile.get("level", 1)

    # Tool definitions
    all_tools = [
        {"id": "career_navigator",     "name": "Career Navigator",     "xp": 100, "icon": "fa-compass",          "color": "#4f46e5"},
        {"id": "roi_calculator",       "name": "ROI Calculator",       "xp": 80,  "icon": "fa-chart-line",       "color": "#16a34a"},
        {"id": "admission_predictor",  "name": "Admission Predictor",  "xp": 90,  "icon": "fa-brain",            "color": "#7c3aed"},
        {"id": "timeline_generator",   "name": "Timeline Generator",   "xp": 70,  "icon": "fa-calendar-alt",    "color": "#f97316"},
        {"id": "loan_planner",         "name": "Loan Planner",         "xp": 120, "icon": "fa-piggy-bank",       "color": "#0891b2"},
        {"id": "chatbot",              "name": "EduMentor AI",         "xp": 50,  "icon": "fa-robot",            "color": "#ec4899"},
        {"id": "application_strategy", "name": "App Strategy",         "xp": 110, "icon": "fa-bullseye",         "color": "#dc2626"},
        {"id": "university_comparison","name": "Uni Comparison",       "xp": 85,  "icon": "fa-balance-scale",    "color": "#d97706"},
        {"id": "peer_benchmarks",      "name": "Peer Benchmarks",      "xp": 75,  "icon": "fa-users",            "color": "#0f766e"},
    ]

    # Compute completion
    tools_with_status = []
    total_xp_possible = 0
    for t in all_tools:
        done = t["id"] in completed
        tools_with_status.append({**t, "done": done})
        total_xp_possible += t["xp"]

    completion_pct = round(len(completed) / len(all_tools) * 100) if all_tools else 0

    # XP progress to next level
    xp_for_next_level = (level) * 500
    xp_in_current_level = xp - (level - 1) * 500
    level_progress_pct = min(100, round(xp_in_current_level / 500 * 100))

    # Engagement score (composite)
    engagement = min(100, round(
        (completion_pct * 0.4) +
        (min(100, streak * 10) * 0.3) +
        (min(100, xp / 10) * 0.2) +
        (len(badges) / 9 * 100 * 0.1)
    ))

    # Journey stage
    if completion_pct >= 80:
        stage = {"name": "Loan Ready", "icon": "💰", "next": "Apply for education financing", "pct": completion_pct}
    elif completion_pct >= 60:
        stage = {"name": "Strategizing", "icon": "🎯", "next": "Build your application strategy", "pct": completion_pct}
    elif completion_pct >= 40:
        stage = {"name": "Planning", "icon": "📋", "next": "Generate your application timeline", "pct": completion_pct}
    elif completion_pct >= 20:
        stage = {"name": "Exploring", "icon": "🔭", "next": "Calculate ROI for your programs", "pct": completion_pct}
    else:
        stage = {"name": "Getting Started", "icon": "🚀", "next": "Start with AI Career Navigator", "pct": completion_pct}

    # Weekly XP chart (simulated for 7 days)
    today = datetime.now()
    weekly_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_xp = 0
        if i == 0:  # today
            day_xp = weekly_xp
        elif i <= len(completed):
            day_xp = all_tools[len(completed) - i]["xp"] if len(completed) > i else 0
        weekly_data.append({
            "day": day.strftime("%a"),
            "date": day.strftime("%b %d"),
            "xp": day_xp
        })

    # Adaptive recommendations
    recs = get_adaptive_recommendations(profile)

    return jsonify({
        "success": True,
        "stats": {
            "xp": xp,
            "level": level,
            "streak": streak,
            "badges_count": len(badges),
            "tools_completed": len(completed),
            "total_tools": len(all_tools),
            "completion_pct": completion_pct,
            "weekly_xp": weekly_xp,
            "engagement_score": engagement,
            "xp_for_next_level": xp_for_next_level,
            "level_progress_pct": level_progress_pct,
            "xp_remaining": max(0, xp_for_next_level - xp),
        },
        "tools": tools_with_status,
        "badges": badges,
        "stage": stage,
        "weekly_xp_data": weekly_data,
        "recommendations": recs["recommendations"],
        "nudge": recs["nudge"],
    })


@bp.route("/api/analytics/log-activity", methods=["POST"])
def log_activity():
    """Log a user activity event for analytics tracking."""
    data = request.json
    if "profile" not in session:
        return jsonify({"success": False})

    log = session["profile"].get("activity_log", [])
    log.append({
        "action": data.get("action"),
        "page": data.get("page"),
        "ts": datetime.now().isoformat(),
    })
    # Keep last 100 events
    session["profile"]["activity_log"] = log[-100:]
    session.modified = True
    return jsonify({"success": True})
