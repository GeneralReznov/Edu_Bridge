from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("community", __name__)

# ── In-memory community store ──────────────────────────────────────────────────
_posts = [
    {"id":1,"title":"How do I improve my GRE Quant score from 160 to 165?","body":"I've been stuck at 160 for 2 attempts. My weak areas are probability and data interpretation. Any tips?","author":"Priya S.","avatar":"P","tag":"GRE","ts":"2025-11-12 10:30","upvotes":24,"views":312,"answers":[{"id":1,"body":"Focus on data interpretation specifically — Manhattan 5lb book has great DI sections. Also time yourself strictly (35 min/section). For probability, Magoosh has excellent video explanations. Most importantly, review every mistake carefully.","author":"Rahul M.","ts":"2025-11-12 14:22","upvotes":18,"is_ai":False,"accepted":True},{"id":2,"body":"I went from 159 to 167 in 6 weeks by doing 30 quant problems daily and reviewing ALL errors. Kaplan practice tests are harder than actual GRE which helps.","author":"Arjun T.","ts":"2025-11-13 09:15","upvotes":11,"is_ai":False,"accepted":False}],"answered":True},
    {"id":2,"title":"SBI vs HDFC Credila for $50K loan — which is better for USA?","body":"I have admit from UC San Diego for MS CS. Loan needed: ₹45L. Family income: ₹8L/yr. No collateral. CIBIL: 720. Which lender should I choose?","author":"Vikram P.","avatar":"V","tag":"Loans","ts":"2025-11-10 16:45","upvotes":31,"views":487,"answers":[{"id":3,"body":"For your profile (no collateral, CIBIL 720), HDFC Credila or Avanse are better options since SBI requires collateral above ₹7.5L. HDFC Credila gives faster approval (5-7 days) vs SBI's 3-4 weeks. Rate will be around 11-11.5%. Use EduBridge Loan Planner for a full comparison!","author":"EduBridge AI","ts":"2025-11-10 17:00","upvotes":28,"is_ai":True,"accepted":True}],"answered":True},
    {"id":3,"title":"Is a GPA of 7.8/10 (CGPA) competitive for Georgia Tech MS CS?","body":"My CGPA is 7.8 from a top NIT. GRE: 317 (V158, Q159). Work exp: 1.5 years at TCS. No research. Should I apply?","author":"Deepa R.","avatar":"D","tag":"Universities","ts":"2025-11-08 11:20","upvotes":19,"views":265,"answers":[{"id":4,"body":"Yes, you should apply! Georgia Tech's average GPA is around 3.5 (roughly 7.5-8/10 for Indian grading). Your profile is competitive for Georgia Tech, especially with work experience. Your GRE could be stronger — 320+ would help — but 317 is not a dealbreaker for GT. Apply and also target UIUC, UT Austin, and UCSD as targets.","author":"EduBridge AI","ts":"2025-11-08 11:45","upvotes":16,"is_ai":True,"accepted":True}],"answered":True},
    {"id":4,"title":"Canada PR through Express Entry — realistic after MS from UofT?","body":"I'm planning MS CS at UofT specifically for PR pathway. Is this a realistic plan? What's the timeline typically?","author":"Ananya K.","avatar":"A","tag":"Visa","ts":"2025-11-05 09:00","upvotes":45,"views":623,"answers":[{"id":5,"body":"Very realistic! Canadian Experience Class (CEC) under Express Entry is the primary pathway. After your 2-year MS + 1 year work experience in Canada, you'll likely qualify. Current CRS scores for CEC are around 470-490. CS graduates with Canadian work experience typically get PR in 6-12 months after becoming eligible. PGWP for 2-year programs gives you 3 years to gain work experience.","author":"Ananya K.","ts":"2025-11-05 10:30","upvotes":38,"is_ai":False,"accepted":True}],"answered":True},
    {"id":5,"title":"Is Prodigy Finance a good option without a co-applicant?","body":"My parents don't have stable income and I can't arrange a co-applicant. Prodigy Finance seems like the only option for my Cornell admit. Experiences?","author":"Karthik N.","avatar":"K","tag":"Loans","ts":"2025-11-03 14:00","upvotes":22,"views":334,"answers":[],"answered":False},
    {"id":6,"title":"F-1 visa denial — got 214b rejection. What next?","body":"I got a 214b rejection for my F-1 visa for USC. My I-20 is valid, SEVIS paid, strong ties. Can I reapply immediately?","author":"Sneha V.","avatar":"S","tag":"Visa","ts":"2025-10-29 08:00","upvotes":28,"views":445,"answers":[{"id":6,"body":"214b means the officer wasn't convinced of non-immigrant intent (ties to home country). You can reapply immediately — there's no waiting period. For reapplication: 1) Strengthen home ties evidence (property, family, job offer after study) 2) Be more specific about your career plans in India 3) Show strong financial documents 4) A bank statement showing 2x program cost helps. 60-70% of 214b applicants succeed on second attempt.","author":"EduBridge AI","ts":"2025-10-29 09:00","upvotes":24,"is_ai":True,"accepted":True}],"answered":True},
]

TAGS = ["GRE","TOEFL","Universities","Loans","Visa","SOP","Career","Scholarships","Germany","Canada","UK","MBA","Internships","Research","Interview"]
_next_id = len(_posts) + 1

def _get_username():
    return session.get("forum_username", "Anonymous")

def _get_post_by_id(post_id):
    return next((p for p in _posts if p["id"] == post_id), None)

@bp.route("/community")
def community():
    return render_template("community.html")

@bp.route("/api/community/posts", methods=["GET"])
def api_posts():
    tag = request.args.get("tag","")
    q   = request.args.get("q","").lower()
    sort = request.args.get("sort","trending")

    posts = list(_posts)
    if tag: posts = [p for p in posts if p["tag"] == tag]
    if q:   posts = [p for p in posts if q in p["title"].lower() or q in p["body"].lower()]
    if sort == "trending": posts.sort(key=lambda x: -(x["upvotes"]*2 + x["views"]))
    elif sort == "newest": posts.sort(key=lambda x: x["ts"], reverse=True)
    elif sort == "unanswered": posts = [p for p in posts if not p["answered"]]

    # Strip full body for list view
    result = [{**p, "body": p["body"][:150]+"...", "answer_count": len(p["answers"])} for p in posts]
    return jsonify({"success": True, "posts": result, "total": len(result), "tags": TAGS})

@bp.route("/api/community/post/<int:post_id>", methods=["GET"])
def api_get_post(post_id):
    post = _get_post_by_id(post_id)
    if not post: return jsonify({"success": False, "error": "Post not found"})
    post["views"] = post.get("views",0) + 1
    return jsonify({"success": True, "post": post})

@bp.route("/api/community/post/create", methods=["POST"])
def api_create_post():
    global _next_id
    data = request.json
    if not data.get("title") or len(data["title"]) < 10:
        return jsonify({"success": False, "error": "Title must be at least 10 characters"})
    post = {
        "id": _next_id,
        "title": data["title"][:200],
        "body": data.get("body","")[:2000],
        "author": _get_username(),
        "avatar": _get_username()[0].upper(),
        "tag": data.get("tag","General"),
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "upvotes": 0,
        "views": 1,
        "answers": [],
        "answered": False,
    }
    _posts.append(post)
    _next_id += 1

    # Award XP
    if "profile" not in session:
        session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
    session["profile"]["xp"] = session["profile"].get("xp",0) + 20
    if not any(b.get("id")=="community" for b in session["profile"]["badges"]):
        session["profile"]["badges"].append({"id":"community","name":"🗣️ Community Member","desc":"Posted in the EduBridge community forum"})
    session.modified = True
    return jsonify({"success": True, "post": post, "xp_gained": 20})

@bp.route("/api/community/answer", methods=["POST"])
def api_answer():
    from app import generate, GEMINI_AVAILABLE
    data = request.json
    post_id = data.get("post_id")
    body = data.get("body","")
    use_ai = data.get("use_ai", False)
    post = _get_post_by_id(post_id)
    if not post: return jsonify({"success": False, "error": "Post not found"})

    if use_ai and GEMINI_AVAILABLE:
        prompt = f"""You are an expert advisor for Indian students applying to graduate programs abroad. Answer this forum question concisely and helpfully (2-3 paragraphs max):

Question: {post['title']}
Details: {post['body']}

Provide specific, actionable advice relevant to Indian students."""
        try:
            body = generate(prompt, temperature=0.5)
            is_ai = True
        except:
            is_ai = False
    else:
        is_ai = False

    answer = {
        "id": sum(len(p["answers"]) for p in _posts) + 1,
        "body": body[:2000],
        "author": "EduBridge AI" if is_ai else _get_username(),
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "upvotes": 0,
        "is_ai": is_ai,
        "accepted": False,
    }
    post["answers"].append(answer)
    post["answered"] = True

    if not is_ai:
        if "profile" not in session:
            session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
        session["profile"]["xp"] = session["profile"].get("xp",0) + 25
        session.modified = True
    return jsonify({"success": True, "answer": answer, "xp_gained": 25 if not is_ai else 0})

@bp.route("/api/community/upvote", methods=["POST"])
def api_upvote():
    data = request.json
    post_id = data.get("post_id")
    answer_id = data.get("answer_id")
    post = _get_post_by_id(post_id)
    if not post: return jsonify({"success": False})
    if answer_id:
        for a in post["answers"]:
            if a["id"] == answer_id:
                a["upvotes"] += 1
                return jsonify({"success": True, "upvotes": a["upvotes"]})
    else:
        post["upvotes"] += 1
        return jsonify({"success": True, "upvotes": post["upvotes"]})
    return jsonify({"success": False})

@bp.route("/api/community/set-username", methods=["POST"])
def api_set_username():
    name = request.json.get("username","").strip()
    if not name: return jsonify({"success": False, "error": "Username required"})
    session["forum_username"] = name[:30]
    session.modified = True
    return jsonify({"success": True})
