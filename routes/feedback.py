from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("feedback", __name__)

# ── In-memory feedback store ───────────────────────────────────────────────────
_feedback_store = []
_ratings_store  = []

CATEGORIES = ["AI Response Quality","University Data Accuracy","Feature Request","Bug Report","UI/UX Feedback","General Feedback"]
TOOLS = ["Career Navigator","ROI Calculator","Admission Predictor","Timeline Generator","Loan Planner","University Comparison","Application Strategy","Peer Benchmarking","Analytics Dashboard","EduMentor Chatbot","General"]

@bp.route("/feedback")
def feedback_page():
    return render_template("feedback.html")

@bp.route("/api/feedback/submit", methods=["POST"])
def api_submit_feedback():
    data = request.json
    fb = {
        "id": len(_feedback_store) + 1,
        "category": data.get("category","General Feedback"),
        "tool": data.get("tool","General"),
        "rating": int(data.get("rating", 3)),
        "message": data.get("message",""),
        "email": data.get("email",""),
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "received",
        "helpful": 0,
    }
    _feedback_store.append(fb)

    # Award XP for feedback
    if "profile" not in session:
        session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
    xp = session["profile"].get("xp",0) + 15
    session["profile"]["xp"] = xp
    if not any(b.get("id")=="feedback" for b in session["profile"]["badges"]):
        session["profile"]["badges"].append({"id":"feedback","name":"💬 Contributor","desc":"Submitted platform feedback"})
    session.modified = True

    return jsonify({"success": True, "id": fb["id"], "xp_gained": 15})

@bp.route("/api/feedback/rate-tool", methods=["POST"])
def api_rate_tool():
    data = request.json
    rating = {
        "tool": data.get("tool",""),
        "score": int(data.get("score",5)),
        "comment": data.get("comment",""),
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _ratings_store.append(rating)
    return jsonify({"success": True})

@bp.route("/api/feedback/stats", methods=["GET"])
def api_feedback_stats():
    total = len(_feedback_store)
    avg_rating = round(sum(f["rating"] for f in _feedback_store) / total, 1) if total else 4.8
    by_category = {}
    for f in _feedback_store:
        by_category[f["category"]] = by_category.get(f["category"], 0) + 1

    tool_ratings = {}
    for r in _ratings_store:
        if r["tool"] not in tool_ratings:
            tool_ratings[r["tool"]] = []
        tool_ratings[r["tool"]].append(r["score"])
    tool_avg = {t: round(sum(v)/len(v),1) for t,v in tool_ratings.items()}

    # Sample recent feedback (last 5, anonymized)
    recent = []
    for f in reversed(_feedback_store[-5:]):
        recent.append({"category":f["category"],"tool":f["tool"],"rating":f["rating"],"message":f["message"][:100],"ts":f["ts"]})

    return jsonify({
        "success": True,
        "total_feedback": total,
        "avg_rating": avg_rating,
        "by_category": by_category,
        "tool_ratings": tool_avg,
        "recent": recent,
    })
