from flask import Blueprint, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("gamification_enhanced", __name__)

@bp.route("/api/leaderboard", methods=["GET"])
def api_leaderboard():
    """Return simulated leaderboard data."""
    import random
    names = ["Priya S.", "Rahul M.", "Ananya K.", "Vikram P.", "Deepa R.",
             "Arjun T.", "Sneha V.", "Karthik N.", "Pooja A.", "Ravi K."]
    boards = []
    for i, name in enumerate(names):
        boards.append({
            "rank": i + 1,
            "name": name,
            "xp": max(50, 850 - i * 80 + random.randint(-20, 20)),
            "level": max(1, 3 - i // 3),
            "tools": min(9, 9 - i),
            "badge": "🏆" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "⭐"))
        })

    user_profile = session.get("profile", {"xp": 0, "level": 1, "completed_modules": []})
    user_entry = {
        "rank": "You",
        "name": "You",
        "xp": user_profile.get("xp", 0),
        "level": user_profile.get("level", 1),
        "tools": len(user_profile.get("completed_modules", [])),
        "badge": "👤"
    }

    return jsonify({"success": True, "leaderboard": boards, "user": user_entry})
