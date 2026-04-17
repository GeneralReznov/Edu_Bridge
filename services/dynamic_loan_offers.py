"""
Dynamic Loan Offers Service (Enhanced)
Personalizes loan offers based on the student's complete profile.
Simulates partner API responses with realistic, profile-aware data.
"""

LENDER_BASE_DATA = [
    {
        "id": "sbi",
        "name": "SBI Global Ed-Vantage",
        "logo_icon": "fas fa-university",
        "type": "PSU Bank",
        "badge": "Lowest Rate",
        "badge_color": "#16a34a",
        "base_rate": 10.15,
        "max_amount_lakhs": 150,
        "max_tenure": 15,
        "moratorium": "Course + 1 year",
        "processing_fee_pct": 0.0,
        "collateral_threshold_lakhs": 7.5,
        "approval_days": "21-28",
        "features": ["No processing fee", "Interest subsidy available (CSIS)", "Longest tenure", "Wide branch network"],
        "best_for": "Students going to top 200 QS ranked universities",
        "eligibility_factors": {"cibil_min": 650, "income_min_lakhs": 3.0},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Singapore"],
    },
    {
        "id": "hdfc_credila",
        "name": "HDFC Credila",
        "logo_icon": "fas fa-chart-bar",
        "type": "NBFC",
        "badge": "Fastest Approval",
        "badge_color": "#2563eb",
        "base_rate": 11.25,
        "max_amount_lakhs": 150,
        "max_tenure": 14,
        "moratorium": "Course + 6 months",
        "processing_fee_pct": 1.0,
        "collateral_threshold_lakhs": 0,
        "approval_days": "5-7",
        "features": ["Pre-admission loans", "No collateral for top unis", "Online application", "Dedicated manager"],
        "best_for": "Students with admits from top US/UK universities",
        "eligibility_factors": {"cibil_min": 700, "income_min_lakhs": 4.0},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
    },
    {
        "id": "avanse",
        "name": "Avanse Financial Services",
        "logo_icon": "fas fa-rocket",
        "type": "NBFC",
        "badge": "Pre-Admission",
        "badge_color": "#7c3aed",
        "base_rate": 11.00,
        "max_amount_lakhs": 100,
        "max_tenure": 15,
        "moratorium": "Course + 1 year",
        "processing_fee_pct": 1.0,
        "collateral_threshold_lakhs": 0,
        "approval_days": "5-7",
        "features": ["Pre-admission sanction", "Top 200 global universities", "Flexible repayment", "Co-applicant not mandatory"],
        "best_for": "Early planners who need pre-admission loan letters",
        "eligibility_factors": {"cibil_min": 650, "income_min_lakhs": 3.0},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Ireland"],
    },
    {
        "id": "prodigy",
        "name": "Prodigy Finance",
        "logo_icon": "fas fa-globe",
        "type": "International NBFC",
        "badge": "No Co-applicant",
        "badge_color": "#0891b2",
        "base_rate": 11.90,
        "max_amount_lakhs": 100,
        "max_tenure": 10,
        "moratorium": "Course period",
        "processing_fee_pct": 2.5,
        "collateral_threshold_lakhs": 0,
        "approval_days": "2-3",
        "features": ["No co-applicant needed", "No collateral", "Based on future earnings", "Repay in local currency"],
        "best_for": "Students with strong admits, no family co-applicant",
        "eligibility_factors": {"cibil_min": 0, "income_min_lakhs": 0},
        "countries": ["USA", "UK", "Canada", "Germany", "France", "Spain"],
    },
    {
        "id": "icici",
        "name": "ICICI Bank Education Loan",
        "logo_icon": "fas fa-landmark",
        "type": "Private Bank",
        "badge": "Wide Network",
        "badge_color": "#dc2626",
        "base_rate": 10.50,
        "max_amount_lakhs": 100,
        "max_tenure": 15,
        "moratorium": "Course + 12 months",
        "processing_fee_pct": 0.5,
        "collateral_threshold_lakhs": 7.5,
        "approval_days": "10-14",
        "features": ["Instant in-principle approval", "doorstep service", "Tax benefit 80E", "Travel insurance"],
        "best_for": "Students wanting a trusted private bank with fast processing",
        "eligibility_factors": {"cibil_min": 700, "income_min_lakhs": 3.5},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Singapore"],
    },
    {
        "id": "auxilo",
        "name": "Auxilo Finserve",
        "logo_icon": "fas fa-hand-holding-heart",
        "type": "NBFC",
        "badge": "Flexible Eligibility",
        "badge_color": "#d97706",
        "base_rate": 12.25,
        "max_amount_lakhs": 75,
        "max_tenure": 14,
        "moratorium": "Course + 12 months",
        "processing_fee_pct": 1.5,
        "collateral_threshold_lakhs": 0,
        "approval_days": "3-5",
        "features": ["Weak credit history accepted", "Unconventional courses covered", "Part-time students eligible"],
        "best_for": "Students with limited credit history or non-standard programs",
        "eligibility_factors": {"cibil_min": 550, "income_min_lakhs": 1.5},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
    },
    {
        "id": "axis",
        "name": "Axis Bank Education Loan",
        "logo_icon": "fas fa-building",
        "type": "Private Bank",
        "badge": "Digital-First",
        "badge_color": "#0f172a",
        "base_rate": 13.70,
        "max_amount_lakhs": 75,
        "max_tenure": 15,
        "moratorium": "Course + 12 months",
        "processing_fee_pct": 1.0,
        "collateral_threshold_lakhs": 4.0,
        "approval_days": "7-10",
        "features": ["100% digital process", "Low collateral threshold", "Prepayment allowed free", "Dedicated NRI desk"],
        "best_for": "Students who want full digital process with lower collateral",
        "eligibility_factors": {"cibil_min": 650, "income_min_lakhs": 2.5},
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
    },
]

def _cibil_score_to_num(cibil_str: str) -> int:
    mapping = {
        "750+ (excellent)": 780, "750+": 780,
        "700-750 (good)": 725, "700-750": 725,
        "650-700 (fair)": 675, "650-700": 675,
        "below 650 (needs work)": 600, "below 650": 600,
        "no credit history": 620,
    }
    return mapping.get(str(cibil_str).lower().strip(), 700)

def _rate_adjustment(lender, profile) -> float:
    """Adjust rate based on profile quality: better profile → lower rate."""
    adj = 0.0
    cibil = _cibil_score_to_num(profile.get("cibil", "700-750"))
    if cibil >= 750: adj -= 0.25
    elif cibil < 650: adj += 0.50

    income = float(profile.get("family_income_lakhs", 6))
    if income >= 12: adj -= 0.15
    elif income < 3: adj += 0.40

    collateral = float(profile.get("collateral_lakhs", 0))
    if collateral >= 20: adj -= 0.30
    elif collateral >= 10: adj -= 0.15

    academics = profile.get("academics", "")
    if "merit" in str(academics).lower() or "scholarship" in str(academics).lower():
        adj -= 0.20

    return round(adj, 2)

def get_personalized_offers(profile: dict) -> list:
    """
    Returns list of personalized loan offers for the student's profile.
    Filters, sorts, and adjusts rates based on profile.
    """
    cibil_num = _cibil_score_to_num(profile.get("cibil", "700-750"))
    income    = float(profile.get("family_income_lakhs", 6))
    loan_amt  = float(profile.get("loan_lakhs", 40))
    country   = profile.get("country", "USA")
    collateral_lakhs = float(profile.get("collateral_lakhs", 0))

    offers = []
    for lender in LENDER_BASE_DATA:
        # Basic eligibility check
        eligible = True
        reasons = []

        if cibil_num < lender["eligibility_factors"]["cibil_min"] and lender["eligibility_factors"]["cibil_min"] > 0:
            eligible = False
            reasons.append(f"CIBIL score below {lender['eligibility_factors']['cibil_min']}")

        if income < lender["eligibility_factors"]["income_min_lakhs"]:
            eligible = False
            reasons.append(f"Family income below ₹{lender['eligibility_factors']['income_min_lakhs']}L threshold")

        if loan_amt > lender["max_amount_lakhs"]:
            eligible = False
            reasons.append(f"Loan amount exceeds ₹{lender['max_amount_lakhs']}L maximum")

        adj = _rate_adjustment(lender, profile)
        effective_rate = round(lender["base_rate"] + adj, 2)
        effective_rate = max(lender["base_rate"] - 0.5, effective_rate)  # floor

        # Match score (0-100) for sorting
        match_score = 100
        if not eligible: match_score = 20
        if cibil_num >= 750: match_score += 10
        if country in lender["countries"]: match_score += 15
        if collateral_lakhs >= lender["collateral_threshold_lakhs"]: match_score += 10
        if loan_amt <= lender["max_amount_lakhs"] * 0.7: match_score += 5

        # EMI preview (simple)
        monthly_rate = effective_rate / 12 / 100
        tenure_months = lender["max_tenure"] * 12
        loan_amount_rs = loan_amt * 100000
        if monthly_rate > 0:
            emi = loan_amount_rs * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
        else:
            emi = loan_amount_rs / tenure_months

        offers.append({
            **lender,
            "eligible": eligible,
            "ineligible_reasons": reasons,
            "effective_rate": effective_rate,
            "rate_adjustment": adj,
            "match_score": min(100, match_score),
            "country_supported": country in lender["countries"],
            "emi_preview": round(emi / 100) * 100,  # rounded to 100
            "total_payable_lakhs": round(emi * tenure_months / 100000, 1),
            "interest_payable_lakhs": round((emi * tenure_months - loan_amount_rs) / 100000, 1),
        })

    # Sort: eligible first, then by match score
    offers.sort(key=lambda x: (-x["eligible"], -x["match_score"]))
    return offers

def get_loan_comparison_insights(offers: list, loan_lakhs: float) -> dict:
    """Generate comparison insights from the offers list."""
    eligible = [o for o in offers if o["eligible"]]
    if not eligible:
        return {"min_rate": "N/A", "max_rate": "N/A", "best_lender": "N/A", "savings": 0}

    rates = [o["effective_rate"] for o in eligible]
    best = eligible[0]
    worst = max(eligible, key=lambda x: x["effective_rate"])

    # Interest savings: best vs worst over 10 years
    loan_rs = loan_lakhs * 100000
    r1 = best["effective_rate"] / 12 / 100
    r2 = worst["effective_rate"] / 12 / 100
    t  = 120  # 10 years
    emi1 = loan_rs * r1 * (1+r1)**t / ((1+r1)**t - 1) if r1 > 0 else loan_rs/t
    emi2 = loan_rs * r2 * (1+r2)**t / ((1+r2)**t - 1) if r2 > 0 else loan_rs/t
    savings = round((emi2 - emi1) * t / 100000, 1)

    return {
        "min_rate": f"{min(rates):.2f}%",
        "max_rate": f"{max(rates):.2f}%",
        "best_lender": best["name"],
        "eligible_count": len(eligible),
        "total_lenders": len(offers),
        "savings_vs_worst_lakhs": savings,
        "recommended": best["id"],
    }
