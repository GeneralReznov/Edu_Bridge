from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("admission_tracking", __name__)

STATUSES = ["Planning","Applied","Documents Submitted","Under Review","Interview Scheduled","Interview Done","Waitlisted","Admitted","Rejected","Deferred","Withdrawn"]
STATUS_COLORS = {"Planning":"#64748b","Applied":"#4f46e5","Documents Submitted":"#0891b2","Under Review":"#d97706","Interview Scheduled":"#7c3aed","Interview Done":"#7c3aed","Waitlisted":"#f97316","Admitted":"#16a34a","Rejected":"#dc2626","Deferred":"#d97706","Withdrawn":"#94a3b8"}

def get_apps():
    return session.get("application_tracker", [])

def save_apps(apps):
    session["application_tracker"] = apps
    session.modified = True

def _deadline_status(deadline_str):
    if not deadline_str: return "none"
    try:
        dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        today = date.today()
        diff = (dl - today).days
        if diff < 0: return "overdue"
        if diff <= 7: return "urgent"
        if diff <= 30: return "upcoming"
        return "future"
    except:
        return "none"

@bp.route("/admission-tracker")
def admission_tracker():
    return render_template("admission_tracker.html")

@bp.route("/api/tracker/list", methods=["GET"])
def api_tracker_list():
    apps = get_apps()
    for a in apps:
        a["deadline_status"] = _deadline_status(a.get("deadline"))
        a["status_color"] = STATUS_COLORS.get(a["status"], "#64748b")
    stats = {
        "total": len(apps),
        "admitted": sum(1 for a in apps if a["status"] == "Admitted"),
        "rejected": sum(1 for a in apps if a["status"] == "Rejected"),
        "pending": sum(1 for a in apps if a["status"] not in ["Admitted","Rejected","Withdrawn"]),
        "waitlisted": sum(1 for a in apps if a["status"] == "Waitlisted"),
        "interviews": sum(1 for a in apps if "Interview" in a["status"]),
    }
    upcoming = sorted([a for a in apps if _deadline_status(a.get("deadline")) in ["urgent","upcoming"]], key=lambda x: x.get("deadline","9999"))
    return jsonify({"success": True, "applications": apps, "stats": stats, "upcoming_deadlines": upcoming[:3]})

@bp.route("/api/tracker/add", methods=["POST"])
def api_tracker_add():
    data = request.json
    apps = get_apps()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    app_entry = {
        "id": int(datetime.now().timestamp() * 1000),
        "university": data.get("university",""),
        "program": data.get("program",""),
        "country": data.get("country",""),
        "degree": data.get("degree","MS"),
        "intake": data.get("intake","Fall 2026"),
        "status": data.get("status","Planning"),
        "deadline": data.get("deadline",""),
        "tuition_usd": data.get("tuition_usd",0),
        "scholarship": data.get("scholarship",""),
        "portal_link": data.get("portal_link",""),
        "notes": data.get("notes",""),
        "priority": data.get("priority","Medium"),
        "gre_required": data.get("gre_required",True),
        "toefl_required": data.get("toefl_required",True),
        "lor_count": data.get("lor_count",3),
        "tasks": [
            {"task":"Finalize SOP","done":False},
            {"task":"Request LORs","done":False},
            {"task":"Prepare transcripts","done":False},
            {"task":"Submit application","done":False},
            {"task":"Pay application fee","done":False},
        ],
        "created_at": now,
        "updated_at": now,
        "tier": data.get("tier","Target"),
    }
    apps.append(app_entry)
    save_apps(apps)

    if "profile" not in session:
        session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
    session["profile"]["xp"] = session["profile"].get("xp",0) + 10
    if "admission_tracking" not in session["profile"].get("completed_modules",[]):
        session["profile"]["completed_modules"].append("admission_tracking")
        if not any(b.get("id")=="tracker" for b in session["profile"]["badges"]):
            session["profile"]["badges"].append({"id":"tracker","name":"📋 Tracker","desc":"Started tracking applications"})
    session.modified = True
    return jsonify({"success": True, "application": app_entry, "xp_gained": 10})

@bp.route("/api/tracker/update", methods=["POST"])
def api_tracker_update():
    data = request.json
    app_id = data.get("id")
    apps = get_apps()
    for app_entry in apps:
        if app_entry["id"] == app_id:
            for field in ["status","notes","scholarship","portal_link","deadline","priority","tasks"]:
                if field in data:
                    app_entry[field] = data[field]
            app_entry["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            app_entry["status_color"] = STATUS_COLORS.get(app_entry["status"],"#64748b")
            if data.get("status") == "Admitted" and not any(b.get("id")=="admitted" for b in session.get("profile",{}).get("badges",[])):
                if "profile" in session:
                    session["profile"]["badges"].append({"id":"admitted","name":"🎓 Admitted!","desc":"Got admitted to a university"})
                    session["profile"]["xp"] = session["profile"].get("xp",0) + 500
                    session.modified = True
            save_apps(apps)
            return jsonify({"success": True, "application": app_entry})
    return jsonify({"success": False, "error": "Application not found"})

@bp.route("/api/tracker/delete", methods=["POST"])
def api_tracker_delete():
    app_id = request.json.get("id")
    apps = [a for a in get_apps() if a["id"] != app_id]
    save_apps(apps)
    return jsonify({"success": True})

@bp.route("/api/tracker/statuses", methods=["GET"])
def api_statuses():
    return jsonify({"success": True, "statuses": STATUSES, "colors": STATUS_COLORS})
