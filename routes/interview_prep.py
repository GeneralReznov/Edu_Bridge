from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("interview_prep", __name__)

# ── Question Bank ──────────────────────────────────────────────────────────────
QUESTIONS = {
    "behavioral": [
        {"id":"b1","q":"Tell me about yourself.","tip":"Use Present-Past-Future structure: current role → how you got here → why this program","category":"behavioral","difficulty":"Easy","time":90},
        {"id":"b2","q":"Why do you want to pursue a graduate degree?","tip":"Be specific about skills you want to develop and how this program uniquely offers them","category":"behavioral","difficulty":"Easy","time":90},
        {"id":"b3","q":"Describe a challenging project and how you overcame obstacles.","tip":"Use STAR method: Situation, Task, Action, Result. Quantify the result.","category":"behavioral","difficulty":"Medium","time":120},
        {"id":"b4","q":"What is your biggest weakness, and how are you addressing it?","tip":"Choose a real weakness but one not critical to this field. Show self-awareness and improvement steps.","category":"behavioral","difficulty":"Medium","time":90},
        {"id":"b5","q":"Where do you see yourself in 5 years?","tip":"Connect your goal to the program — show this is a deliberate step, not a fallback plan.","category":"behavioral","difficulty":"Easy","time":90},
        {"id":"b6","q":"Why this university over others?","tip":"Research specific professors, labs, courses, and industry connections. Be specific, not generic.","category":"behavioral","difficulty":"Medium","time":90},
        {"id":"b7","q":"Describe a time you failed and what you learned.","tip":"Don't deflect. Describe a real failure, own your role, and show concrete lessons learned.","category":"behavioral","difficulty":"Hard","time":120},
        {"id":"b8","q":"How do you handle working in teams with conflict?","tip":"Show empathy, communication skills, and focus on team outcomes over personal ego.","category":"behavioral","difficulty":"Medium","time":90},
        {"id":"b9","q":"What motivates you most in your work?","tip":"Align your motivation with the nature of graduate study (research, problem-solving, impact).","category":"behavioral","difficulty":"Easy","time":60},
        {"id":"b10","q":"Do you have any questions for us?","tip":"Always ask 2-3 thoughtful questions. Ask about research directions, student life, or career outcomes.","category":"behavioral","difficulty":"Easy","time":60},
    ],
    "technical_cs": [
        {"id":"t1","q":"Explain the difference between machine learning and deep learning.","tip":"Start with ML as learning from data with features, then explain deep learning as representation learning with neural networks.","category":"technical","difficulty":"Medium","time":120},
        {"id":"t2","q":"What is your experience with data structures and algorithms?","tip":"Give specific examples: sorted problems you solved, competitive programming, or DSA used in projects.","category":"technical","difficulty":"Medium","time":120},
        {"id":"t3","q":"Explain a research paper or project you are most proud of.","tip":"Structure: problem statement, your approach, key results, impact. Be ready to go deep on methodology.","category":"technical","difficulty":"Hard","time":180},
        {"id":"t4","q":"What are the differences between SQL and NoSQL databases?","tip":"Cover: structure (schema vs schemaless), scaling (vertical vs horizontal), use cases, ACID vs BASE.","category":"technical","difficulty":"Medium","time":90},
        {"id":"t5","q":"How would you approach a new machine learning problem from scratch?","tip":"Frame: understand business problem → explore data → choose baseline → iterate → validate → deploy. Show systematic thinking.","category":"technical","difficulty":"Hard","time":180},
        {"id":"t6","q":"Explain time and space complexity with an example.","tip":"Use Big O notation. Give concrete example: binary search is O(log n), bubble sort is O(n²).","category":"technical","difficulty":"Medium","time":90},
        {"id":"t7","q":"What areas of computer science are you most passionate about and why?","tip":"Choose 1-2 areas and connect them to the program's research strengths. Show you've done homework.","category":"technical","difficulty":"Medium","time":90},
        {"id":"t8","q":"Describe your most technically challenging project.","tip":"Focus on the technical decisions, trade-offs you made, and what you'd do differently.","category":"technical","difficulty":"Hard","time":180},
    ],
    "technical_mba": [
        {"id":"m1","q":"Walk me through a DCF valuation.","tip":"Cash flows → terminal value → discount rate (WACC) → NPV. Practice saying this fluently.","category":"technical","difficulty":"Hard","time":180},
        {"id":"m2","q":"What are the key drivers of business profitability?","tip":"Revenue growth, margin expansion, asset efficiency (ROIC), capital allocation.","category":"technical","difficulty":"Medium","time":120},
        {"id":"m3","q":"Tell me about a recent business news story and its implications.","tip":"Pick something from WSJ/ET in the last 2 weeks. Analyze: what happened, why it matters, what happens next.","category":"technical","difficulty":"Medium","time":120},
        {"id":"m4","q":"What makes a good leader?","tip":"Use frameworks: Situational leadership, emotional intelligence. Give specific examples from your experience.","category":"technical","difficulty":"Easy","time":90},
        {"id":"m5","q":"How would you turn around a struggling business unit?","tip":"Diagnose: revenue or cost problem? Then: prioritize, cut waste, invest in growth, measure KPIs.","category":"technical","difficulty":"Hard","time":180},
    ],
    "research": [
        {"id":"r1","q":"What research question are you most interested in pursuing?","tip":"Be specific. Don't say 'AI' — say 'adversarial robustness in NLP models for low-resource languages'.","category":"research","difficulty":"Hard","time":180},
        {"id":"r2","q":"Which professors in our department would you like to work with and why?","tip":"Name 2-3 specific professors, cite their recent papers by title, and explain the connection to your interests.","category":"research","difficulty":"Hard","time":180},
        {"id":"r3","q":"How has your undergraduate research prepared you for a PhD?","tip":"Walk through: research question → methodology → results → limitations → what you'd do next.","category":"research","difficulty":"Medium","time":150},
        {"id":"r4","q":"Describe a paper you've read recently that impressed you.","tip":"Title, authors, key contribution, why it's novel, one limitation you spotted.","category":"research","difficulty":"Medium","time":120},
        {"id":"r5","q":"How do you handle ambiguity in a research problem?","tip":"Show process: literature review → define scope → form hypotheses → iterate. Embrace uncertainty as part of research.","category":"research","difficulty":"Hard","time":150},
    ],
    "motivation": [
        {"id":"mo1","q":"Why did you choose this specific program over others?","tip":"Cite 3 specific reasons: faculty, curriculum, location/industry access, alumni outcomes.","category":"motivation","difficulty":"Medium","time":90},
        {"id":"mo2","q":"What has been the most influential experience in shaping your career goals?","tip":"Tell a specific story with emotional resonance. Connect it directly to your application.","category":"motivation","difficulty":"Medium","time":120},
        {"id":"mo3","q":"How will this degree help you achieve your long-term goals?","tip":"Bridge present skills → program fills the gap → future role. Be specific about what skills you'll gain.","category":"motivation","difficulty":"Easy","time":90},
        {"id":"mo4","q":"Why are you the right fit for our program?","tip":"Three pillars: academic strength (GPA/research) + professional experience + cultural fit with program values.","category":"motivation","difficulty":"Medium","time":90},
    ],
}

FRAMEWORKS = [
    {"name":"STAR Method","icon":"⭐","desc":"Situation, Task, Action, Result — for behavioral questions","use_for":["behavioral"],"steps":["Situation: Set the context (1 sentence)","Task: What was your responsibility?","Action: What did YOU specifically do? (most important part)","Result: Quantify the outcome (%, $, time saved, etc.)"]},
    {"name":"PPF Structure","icon":"🔮","desc":"Past, Present, Future — for 'Tell me about yourself'","use_for":["behavioral","motivation"],"steps":["Present: Who you are now and current role","Past: How you got here (academic + professional journey)","Future: Why this program and where you want to go"]},
    {"name":"WHY-HOW-WHAT","icon":"💡","desc":"Simon Sinek's Golden Circle for motivation questions","use_for":["motivation"],"steps":["WHY: Your core belief/motivation (the inspiring part)","HOW: Your specific approach or differentiator","WHAT: The concrete deliverable or goal"]},
    {"name":"PARADE Method","icon":"🏆","desc":"Problem, Anticipated, Role, Action, Decision, End Result","use_for":["behavioral","technical"],"steps":["Problem: Describe the challenge clearly","Anticipated: What was the expected solution?","Role: What was your specific role?","Action: What did you do?","Decision: What trade-offs did you make?","End Result: What was the outcome?"]},
]

@bp.route("/interview-prep")
def interview_prep():
    return render_template("interview_prep.html")

@bp.route("/api/interview/questions", methods=["GET"])
def api_get_questions():
    program_type = request.args.get("type","cs")
    category = request.args.get("category","all")
    difficulty = request.args.get("difficulty","all")

    all_q = list(QUESTIONS["behavioral"]) + list(QUESTIONS["motivation"])
    if "mba" in program_type.lower():
        all_q += QUESTIONS["technical_mba"]
    else:
        all_q += QUESTIONS["technical_cs"]
        all_q += QUESTIONS["research"]

    if category != "all":
        all_q = [q for q in all_q if q["category"] == category]
    if difficulty != "all":
        all_q = [q for q in all_q if q["difficulty"].lower() == difficulty.lower()]

    return jsonify({"success": True, "questions": all_q, "total": len(all_q), "frameworks": FRAMEWORKS})

@bp.route("/api/interview/evaluate", methods=["POST"])
def api_evaluate_answer():
    from app import generate, safe_json_parse
    data = request.json
    question = data.get("question","")
    answer = data.get("answer","")
    category = data.get("category","behavioral")
    tip = data.get("tip","")

    if not answer or len(answer) < 30:
        return jsonify({"success": False, "error": "Please provide a more detailed answer"})

    prompt = f"""You are an expert graduate admissions interviewer evaluating an Indian student's interview answer.

Question: {question}
Category: {category}
Interview Tip: {tip}

Student's Answer:
{answer}

Evaluate the answer and respond with valid JSON only (no markdown):
{{
  "overall_score": 78,
  "scores": {{
    "content": 80,
    "structure": 75,
    "specificity": 70,
    "confidence": 85,
    "relevance": 80
  }},
  "grade": "B+",
  "verdict": "Good answer with room for improvement",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "example_strong_answer": "A brief example of how a strong answer would start...",
  "key_words_used": ["word1", "word2"],
  "missing_elements": ["element1", "element2"],
  "follow_up_questions": ["What would an interviewer ask next?", "Another follow-up?"]
}}"""

    try:
        result = generate(prompt, temperature=0.5)
        parsed = safe_json_parse(result)
        if not parsed:
            return jsonify({"success": False, "error": "Could not evaluate answer. Please retry."})

        # Track practice in session
        history = session.get("interview_history", [])
        history.append({
            "question": question[:100],
            "score": parsed.get("overall_score",0),
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        session["interview_history"] = history[-20:]

        # Award XP
        if "profile" not in session:
            session["profile"] = {"xp":0,"level":1,"streak":0,"badges":[],"completed_modules":[],"last_visit":None,"weekly_xp":0}
        session["profile"]["xp"] = session["profile"].get("xp",0) + 30
        if "interview_prep" not in session["profile"].get("completed_modules",[]):
            session["profile"]["completed_modules"].append("interview_prep")
            if not any(b.get("id")=="interview" for b in session["profile"]["badges"]):
                session["profile"]["badges"].append({"id":"interview","name":"🎤 Interview Ready","desc":"Practiced interview questions"})
        session.modified = True

        return jsonify({"success": True, "evaluation": parsed, "xp_gained": 30})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@bp.route("/api/interview/mock-session", methods=["POST"])
def api_mock_session():
    """Generate a full mock interview session with N questions."""
    data = request.json
    program_type = data.get("type","cs")
    n = min(int(data.get("count",5)), 10)

    all_q = list(QUESTIONS["behavioral"]) + list(QUESTIONS["motivation"])
    if "mba" in program_type.lower():
        all_q += QUESTIONS["technical_mba"]
    else:
        all_q += QUESTIONS["technical_cs"]

    session_questions = random.sample(all_q, min(n, len(all_q)))
    return jsonify({"success": True, "session": session_questions, "total_time": sum(q["time"] for q in session_questions)})

@bp.route("/api/interview/history", methods=["GET"])
def api_interview_history():
    history = session.get("interview_history", [])
    avg_score = round(sum(h["score"] for h in history) / len(history), 1) if history else 0
    return jsonify({"success": True, "history": history, "avg_score": avg_score, "total_practiced": len(history)})
