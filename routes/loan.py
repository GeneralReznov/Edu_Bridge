from flask import Blueprint, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("loan_enhanced", __name__)

@bp.route("/api/dynamic-loan-offers", methods=["POST"])
def api_dynamic_loan_offers():
    from services.dynamic_loan_offers import get_personalized_offers, get_loan_comparison_insights
    data = request.json

    # Build profile for loan matching
    loan_lakhs = float(data.get("loan_amount", 0)) / 100000
    total_cost = float(data.get("total_cost", 0))
    family_income = float(data.get("family_income", 0)) / 100000

    profile = {
        "loan_lakhs": loan_lakhs,
        "total_cost_lakhs": total_cost / 100000,
        "family_income_lakhs": family_income,
        "cibil": data.get("cibil", "700-750 (Good)"),
        "collateral_lakhs": float(data.get("collateral_value", 0) or 0) / 100000,
        "country": data.get("country", "USA"),
        "academics": data.get("academics", ""),
        "employment": data.get("employment", "Salaried"),
    }

    try:
        offers = get_personalized_offers(profile)
        insights = get_loan_comparison_insights(offers, loan_lakhs)

        # Strip non-serializable keys
        safe_offers = []
        for o in offers:
            safe_offers.append({k: v for k, v in o.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))})

        return jsonify({"success": True, "offers": safe_offers, "insights": insights, "loan_lakhs": round(loan_lakhs, 1)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
