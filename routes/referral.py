from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("referral", __name__)

# ── In-memory referral store ───────────────────────────────────────────────────
_referrals = {}   # code -> {referrer_session, count, joined: [timestamps]}

REWARDS = [
    {"milestone": 1,  "xp": 100,  "badge": None,                   "reward": "100 XP Bonus"},
    {"milestone": 3,  "xp": 300,  "badge": "🤝 Connector",         "reward": "Connector Badge + 300 XP"},
    {"milestone": 5,  "xp": 500,  "badge": "⭐ Ambassador",         "reward": "Ambassador Badge + 500 XP"},
    {"milestone": 10, "xp": 1000, "badge": "👑 EduBridge Champion", "reward": "Champion Badge + 1000 XP + Exclusive features"},
]

def _get_or_create_code():
    """Get or create a referral code for the current session."""
    if "referral_code" not in session:
        sid = session.get("_id", id(session))
        code = hashlib.md5(str(sid).encode()).hexdigest()[:8].upper()
        session["referral_code"] = code
        session.modified = True
    return session["referral_code"]

def _get_stats():
    code = session.get("referral_code","")
    data = _referrals.get(code, {"count": 0, "joined": []})
    count = data["count"]
    next_reward = next((r for r in REWARDS if r["milestone"] > count), None)
    earned_rewards = [r for r in REWARDS if r["milestone"] <= count]
    return {"code": code, "count": count, "joined": data["joined"], "next_reward": next_reward, "earned_rewards": earned_rewards}

@bp.route("/referral")
def referral():
    code = _get_or_create_code()
    return render_template("referral.html", code=code)

@bp.route("/api/referral/stats", methods=["GET"])
def api_referral_stats():
    return jsonify({"success": True, **_get_stats()})

@bp.route("/api/referral/use", methods=["POST"])
def api_use_referral():
    """Called when someone joins using a referral code."""
    code = request.json.get("code","").upper().strip()
    if not code:
        return jsonify({"success": False, "error": "No referral code provided"})
    if code not in _referrals:
        _referrals[code] = {"count": 0, "joined": []}
    _referrals[code]["count"] += 1
    _referrals[code]["joined"].append(datetime.now().strftime("%Y-%m-%d"))

    # Check milestones and award XP to referrer
    count = _referrals[code]["count"]
    milestone = next((r for r in REWARDS if r["milestone"] == count), None)

    return jsonify({"success": True, "count": count, "milestone": milestone})

@bp.route("/api/referral/leaderboard", methods=["GET"])
def api_referral_leaderboard():
    board = [{"code": c, "count": d["count"]} for c, d in _referrals.items()]
    board.sort(key=lambda x: -x["count"])
    # Add current user
    my_code = session.get("referral_code","")
    my_rank = next((i+1 for i, b in enumerate(board) if b["code"]==my_code), "N/A")
    return jsonify({"success": True, "leaderboard": board[:10], "my_rank": my_rank})
