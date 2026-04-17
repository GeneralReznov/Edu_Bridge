from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("documents", __name__)

DOC_TYPES = {
    "sop":      {"label":"Statement of Purpose","icon":"fas fa-pen-fancy","color":"#7c3aed","template":"I am applying to [Program] at [University] because..."},
    "lor":      {"label":"LOR Briefing Note","icon":"fas fa-envelope-open-text","color":"#16a34a","template":"Dear [Recommender Name],\nThank you for agreeing to write my recommendation..."},
    "resume":   {"label":"Resume / CV","icon":"fas fa-file-alt","color":"#4f46e5","template":"[Your Name]\n[Email] | [Phone] | [LinkedIn]\n\nEDUCATION\n..."},
    "essay":    {"label":"Scholarship Essay","icon":"fas fa-award","color":"#d97706","template":"Scholarship: [Name]\nPrompt: [Prompt]\n\nResponse:\n..."},
    "financial":{"label":"Financial Plan","icon":"fas fa-coins","color":"#dc2626","template":"Loan Amount: ₹\nLender: \nEMI: ₹\nRepayment Start: "},
    "notes":    {"label":"University Notes","icon":"fas fa-sticky-note","color":"#0891b2","template":"University: \nDeadline: \nStatus: \nNotes: \n"},
    "visa":     {"label":"Visa Document Checklist","icon":"fas fa-passport","color":"#0f766e","template":"Visa Type: F-1 / Study Permit / Tier-4\n\n☐ Valid Passport\n☐ I-20 / CAS\n☐ SEVIS Receipt\n☐ DS-160 Confirmation\n☐ Visa Fee Receipt\n"},
    "other":    {"label":"Other Document","icon":"fas fa-file","color":"#64748b","template":""},
}

def get_docs():
    return session.get("document_vault", [])

def save_docs(docs):
    session["document_vault"] = docs
    session.modified = True

@bp.route("/document-vault")
def document_vault():
    return render_template("document_vault.html")

@bp.route("/api/documents/list", methods=["GET"])
def api_list_docs():
    docs = get_docs()
    doc_type_filter = request.args.get("type","")
    if doc_type_filter:
        docs = [d for d in docs if d["type"] == doc_type_filter]
    docs_sorted = sorted(docs, key=lambda x: x["updated_at"], reverse=True)
    return jsonify({"success": True, "documents": docs_sorted, "total": len(docs_sorted)})

@bp.route("/api/documents/create", methods=["POST"])
def api_create_doc():
    data = request.json
    docs = get_docs()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = {
        "id": int(datetime.now().timestamp() * 1000),
        "type": data.get("type","other"),
        "title": data.get("title","Untitled Document"),
        "content": data.get("content",""),
        "university": data.get("university",""),
        "tags": data.get("tags",[]),
        "created_at": now,
        "updated_at": now,
        "word_count": len(data.get("content","").split()),
        "char_count": len(data.get("content","")),
        "version": 1,
        "status": data.get("status","draft"),
    }
    docs.append(doc)
    save_docs(docs)
    return jsonify({"success": True, "document": doc})

@bp.route("/api/documents/update", methods=["POST"])
def api_update_doc():
    data = request.json
    doc_id = data.get("id")
    docs = get_docs()
    for doc in docs:
        if doc["id"] == doc_id:
            doc["title"] = data.get("title", doc["title"])
            doc["content"] = data.get("content", doc["content"])
            doc["university"] = data.get("university", doc.get("university",""))
            doc["tags"] = data.get("tags", doc.get("tags",[]))
            doc["status"] = data.get("status", doc.get("status","draft"))
            doc["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            doc["word_count"] = len(doc["content"].split())
            doc["char_count"] = len(doc["content"])
            doc["version"] = doc.get("version", 1) + 1
            save_docs(docs)
            return jsonify({"success": True, "document": doc})
    return jsonify({"success": False, "error": "Document not found"})

@bp.route("/api/documents/delete", methods=["POST"])
def api_delete_doc():
    doc_id = request.json.get("id")
    docs = [d for d in get_docs() if d["id"] != doc_id]
    save_docs(docs)
    return jsonify({"success": True})

@bp.route("/api/documents/templates", methods=["GET"])
def api_templates():
    templates = [{"id": k, **v} for k, v in DOC_TYPES.items()]
    return jsonify({"success": True, "templates": templates})

@bp.route("/api/documents/ai-improve", methods=["POST"])
def api_ai_improve():
    from app import generate
    data = request.json
    content = data.get("content","")
    doc_type = data.get("type","sop")
    instruction = data.get("instruction","Improve this document for a graduate school application")
    if not content:
        return jsonify({"success": False, "error": "No content provided"})
    prompt = f"""You are an expert graduate admissions consultant. {instruction} for an Indian student.

Document type: {doc_type}
Current content:
{content[:3000]}

Provide an improved version with track-changes style feedback. Return ONLY the improved text followed by a separator line "---FEEDBACK---" and then 3 specific improvements made."""
    try:
        result = generate(prompt, temperature=0.6)
        parts = result.split("---FEEDBACK---")
        improved = parts[0].strip()
        feedback = parts[1].strip() if len(parts) > 1 else "Document improved for clarity and impact."
        return jsonify({"success": True, "improved": improved, "feedback": feedback})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
