from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("learning_path", __name__)

# ── Learning modules library ───────────────────────────────────────────────────
MODULES = {
    "gre_verbal":   {"id":"gre_verbal","title":"GRE Verbal Mastery","icon":"fas fa-book-open","color":"#7c3aed","category":"Test Prep","difficulty":"Hard","hours":40,"xp":200,"topics":["Text Completion (3-blank)","Sentence Equivalence","Reading Comprehension","Vocabulary Building","Critical Reasoning"],"resources":[{"name":"Manhattan Prep GRE Verbal","type":"Course","url":"https://www.manhattanprep.com/gre/"},{"name":"Magoosh GRE","type":"Course","url":"https://magoosh.com/gre/"},{"name":"GRE Big Book","type":"Book","url":"#"},{"name":"GregMat+ YouTube","type":"Video","url":"https://youtube.com/@GregMat"}],"milestones":["Complete 100 vocab flashcards","Score 155+ on 2 practice tests","Complete 5 RCs per day for a week"]},
    "gre_quant":    {"id":"gre_quant","title":"GRE Quantitative Reasoning","icon":"fas fa-calculator","color":"#4f46e5","category":"Test Prep","difficulty":"Medium","hours":30,"xp":180,"topics":["Arithmetic","Algebra","Geometry","Data Analysis","Word Problems","Quantitative Comparison"],"resources":[{"name":"Manhattan 5-lb Book","type":"Book","url":"#"},{"name":"ETS Official Guide","type":"Book","url":"#"},{"name":"Magoosh GRE Math","type":"Course","url":"https://magoosh.com/gre/"},{"name":"Khan Academy","type":"Video","url":"https://khanacademy.org"}],"milestones":["Score 165+ on a practice test","Complete all ETS official tests","Master all quant formulas"]},
    "toefl":        {"id":"toefl","title":"TOEFL iBT Preparation","icon":"fas fa-language","color":"#0891b2","category":"Test Prep","difficulty":"Medium","hours":25,"xp":150,"topics":["Reading (Academic texts)","Listening (Lectures & Conversations)","Speaking (Integrated & Independent)","Writing (Integrated & Independent)"],"resources":[{"name":"ETS Official TOEFL Guide","type":"Book","url":"#"},{"name":"Magoosh TOEFL","type":"Course","url":"https://magoosh.com/toefl/"},{"name":"Notefull YouTube","type":"Video","url":"https://youtube.com/@NoteFull"},{"name":"British Council Resources","type":"Website","url":"https://britishcouncil.org"}],"milestones":["Complete 3 full practice tests","Score 100+ on Reading section","Achieve 22+ on Speaking"]},
    "sop_writing":  {"id":"sop_writing","title":"Statement of Purpose Writing","icon":"fas fa-pen-fancy","color":"#dc2626","category":"Applications","difficulty":"Hard","hours":15,"xp":160,"topics":["Understanding SOP purpose","Opening hook strategies","Academic journey narrative","Research/project descriptions","Why this program + university","Career goals alignment","Common mistakes to avoid","Peer review techniques"],"resources":[{"name":"EduBridge SOP Generator","type":"Tool","url":"/loan-planner"},{"name":"Admit.me SOP guide","type":"Website","url":"#"},{"name":"Accepted.com blog","type":"Blog","url":"#"},{"name":"Reddit r/gradadmissions","type":"Community","url":"https://reddit.com/r/gradadmissions"}],"milestones":["Complete first draft (800 words)","Get feedback from 3 people","Tailor SOP for each university"]},
    "lor_strategy": {"id":"lor_strategy","title":"LOR Strategy & Management","icon":"fas fa-envelope-open-text","color":"#16a34a","category":"Applications","difficulty":"Medium","hours":8,"xp":100,"topics":["Choosing the right recommenders","Academic vs professional LORs","Briefing your recommenders","What to share with them","Timeline & follow-up","Waiving your right to view","LOR templates & guidelines"],"resources":[{"name":"EduBridge Application Strategy","type":"Tool","url":"/application-strategy"},{"name":"PrepScholar LOR guide","type":"Blog","url":"#"},{"name":"Accepted.com","type":"Blog","url":"#"}],"milestones":["Identify 3 recommenders","Prepare briefing documents","Send request 8 weeks before deadline"]},
    "financial":    {"id":"financial","title":"Education Financing Masterclass","icon":"fas fa-coins","color":"#d97706","category":"Finance","difficulty":"Easy","hours":10,"xp":120,"topics":["Understanding Indian education loans","Collateral vs non-collateral loans","CIBIL score improvement","Section 80E tax benefits","Scholarship hunting strategy","Part-time work during MS","Currency hedging basics","EMI planning"],"resources":[{"name":"EduBridge Loan Planner","type":"Tool","url":"/loan-planner"},{"name":"Vidya Lakshmi Portal","type":"Website","url":"https://www.vidyalakshmi.co.in"},{"name":"Buddy4Study scholarships","type":"Website","url":"https://buddy4study.com"}],"milestones":["Check your CIBIL score","Apply to 5 scholarships","Compare 3 loan offers"]},
    "visa_f1":      {"id":"visa_f1","title":"US F-1 Student Visa Guide","icon":"fas fa-passport","color":"#0f766e","category":"Visa","difficulty":"Medium","hours":6,"xp":90,"topics":["F-1 visa requirements","DS-160 form filling","SEVIS fee payment","Visa interview preparation","I-20 document guide","OPT/CPT explained","H-1B pathway overview","Maintaining status"],"resources":[{"name":"USCIS Official Guide","type":"Website","url":"https://uscis.gov"},{"name":"ImmiHelp F-1 Guide","type":"Website","url":"https://immihelp.com"},{"name":"r/f1visa Reddit","type":"Community","url":"https://reddit.com/r/f1visa"}],"milestones":["Complete DS-160","Pay SEVIS fee","Prepare visa interview answers"]},
    "networking":   {"id":"networking","title":"Professional Networking for Indian Students","icon":"fas fa-handshake","color":"#ec4899","category":"Career","difficulty":"Easy","hours":12,"xp":110,"topics":["LinkedIn optimization","Reaching out to professors","Alumni network strategy","Info interviews","Networking at career fairs","Coffee chats","Building Indian professional network","GitHub profile optimization"],"resources":[{"name":"LinkedIn Learning","type":"Course","url":"https://linkedin.com/learning"},{"name":"EduBridge Career Navigator","type":"Tool","url":"/career-navigator"},{"name":"Blind (anonymous forum)","type":"Community","url":"https://teamblind.com"}],"milestones":["Connect with 20 alumni","Complete LinkedIn profile to All-Star","Do 3 coffee chats"]},
    "resume":       {"id":"resume","title":"Graduate School Resume Building","icon":"fas fa-file-alt","color":"#f97316","category":"Applications","difficulty":"Easy","hours":8,"xp":90,"topics":["Education section formatting","Research experience highlighting","Projects & technical skills","Publications & patents","Leadership & activities","ATS optimization","One-page vs two-page debate","LaTeX templates"],"resources":[{"name":"Overleaf Resume Templates","type":"Tool","url":"https://overleaf.com"},{"name":"Resume Worded","type":"Tool","url":"https://resumeworded.com"},{"name":"Novoresume","type":"Tool","url":"https://novoresume.com"}],"milestones":["Create LaTeX resume","Get ATS score above 80","Tailor for each application"]},
    "research":     {"id":"research","title":"Building a Research Profile","icon":"fas fa-flask","color":"#7c3aed","category":"Academics","difficulty":"Hard","hours":20,"xp":150,"topics":["Finding research opportunities in India","Emailing professors abroad","Research abstract writing","Contributing to open source","Writing technical blog posts","IEEE/ACM paper reading","Kaggle competitions","Conference poster presentations"],"resources":[{"name":"IIT research internships","type":"Website","url":"#"},{"name":"SURGE program at IIT Kanpur","type":"Website","url":"#"},{"name":"Google Scholar","type":"Tool","url":"https://scholar.google.com"},{"name":"ArXiv.org","type":"Resource","url":"https://arxiv.org"}],"milestones":["Read 10 research papers in your field","Contribute to 1 open source project","Write 1 technical blog post"]},
}

PATHS = {
    "cs_fresher":     {"name":"CS Fresher → Top MS","modules":["gre_verbal","gre_quant","toefl","research","sop_writing","lor_strategy","networking","resume","financial","visa_f1"],"target":"Top 20 CS programs in USA/Canada"},
    "mba_professional":{"name":"MBA Aspirant","modules":["toefl","sop_writing","lor_strategy","financial","networking","resume","visa_f1"],"target":"Top MBA programs globally"},
    "finance_track":  {"name":"Finance/Quant Track","modules":["gre_quant","toefl","sop_writing","lor_strategy","financial","networking","resume"],"target":"MS Finance / Financial Engineering"},
    "germany_track":  {"name":"Germany Free Education Track","modules":["toefl","research","sop_writing","lor_strategy","financial","networking","resume"],"target":"TUM / RWTH Aachen / Free German universities"},
    "uk_track":       {"name":"UK 1-Year Masters","modules":["toefl","sop_writing","lor_strategy","financial","networking","resume","visa_f1"],"target":"UCL / Imperial / Edinburgh"},
}

def _recommend_path(profile: dict) -> str:
    field = profile.get("field","").lower()
    budget = profile.get("budget_lakhs", 40)
    countries = profile.get("countries","USA").lower()
    if "germany" in countries: return "germany_track"
    if "uk" in countries and "usa" not in countries: return "uk_track"
    if "mba" in field or "business" in field: return "mba_professional"
    if "finance" in field: return "finance_track"
    return "cs_fresher"

@bp.route("/learning-path")
def learning_path():
    return render_template("learning_path.html")

@bp.route("/api/learning-path/generate", methods=["POST"])
def api_generate_path():
    data = request.json
    path_key = _recommend_path(data)
    path = PATHS.get(path_key, PATHS["cs_fresher"])
    modules = [MODULES[m] for m in path["modules"] if m in MODULES]

    # Get progress from session
    progress = session.get("learning_progress", {})
    for m in modules:
        m["completed"] = m["id"] in progress.get("completed", [])
        m["current"] = m["id"] == progress.get("current")

    total_hours = sum(m["hours"] for m in modules)
    total_xp = sum(m["xp"] for m in modules)
    completed_count = sum(1 for m in modules if m["completed"])

    return jsonify({
        "success": True,
        "path": path,
        "modules": modules,
        "stats": {
            "total_modules": len(modules),
            "completed": completed_count,
            "total_hours": total_hours,
            "total_xp": total_xp,
            "progress_pct": round(completed_count / len(modules) * 100) if modules else 0,
        }
    })

@bp.route("/api/learning-path/complete-module", methods=["POST"])
def api_complete_module():
    module_id = request.json.get("module_id")
    progress = session.get("learning_progress", {"completed": [], "current": None})
    if module_id not in progress["completed"]:
        progress["completed"].append(module_id)
    session["learning_progress"] = progress
    session.modified = True

    # Award XP
    module = MODULES.get(module_id, {})
    xp_reward = module.get("xp", 50)
    if "profile" not in session:
        session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
    session["profile"]["xp"] = session["profile"].get("xp",0) + xp_reward
    if "learning_path" not in session["profile"].get("completed_modules",[]):
        session["profile"]["completed_modules"].append("learning_path")
    session.modified = True

    return jsonify({"success": True, "xp_gained": xp_reward, "completed": progress["completed"]})

@bp.route("/api/learning-path/all-modules", methods=["GET"])
def api_all_modules():
    progress = session.get("learning_progress", {"completed": []})
    modules = []
    for m in MODULES.values():
        m_copy = dict(m)
        m_copy["completed"] = m["id"] in progress["completed"]
        modules.append(m_copy)
    return jsonify({"success": True, "modules": modules})
