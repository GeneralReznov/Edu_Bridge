"""
Profile Analyzer Service
Computes structured profile scores, percentiles, and strengths
"""
import json, re

def compute_profile_score(data: dict) -> dict:
    """
    Returns a detailed scoring breakdown for a student profile.
    data keys: gpa, gre_verbal, gre_quant, gre_awa, toefl_ielts,
               work_exp, research, publications, internships, sop_quality,
               lor_quality, extracurriculars
    """
    def norm(val, lo, hi):
        try:
            v = float(str(val).replace(",",""))
            return max(0, min(100, (v - lo) / (hi - lo) * 100))
        except:
            return 0

    gpa_raw  = data.get("gpa", 0)
    gre_v    = data.get("gre_verbal", 0)
    gre_q    = data.get("gre_quant", 0)
    gre_awa  = data.get("gre_awa", 0)
    toefl    = data.get("toefl", 0)
    work     = int(data.get("work_exp", 0) or 0)
    research = data.get("research", "none")
    pubs     = int(data.get("publications", 0) or 0)
    interns  = int(data.get("internships", 0) or 0)
    sop_q    = data.get("sop_quality", "basic")
    lor_q    = data.get("lor_quality", "average")
    extras   = data.get("extracurriculars", "none")

    # GPA: normalize assuming max 10 or 4
    g = float(str(gpa_raw).replace(",","")) if gpa_raw else 0
    academic = norm(g, 2.5, 4.0) if g <= 4.0 else norm(g, 6.0, 10.0)

    # GRE
    gre_total = float(gre_v or 0) + float(gre_q or 0)
    gre_score = norm(gre_total, 260, 340)
    awa_score = norm(float(gre_awa or 0), 2.0, 6.0)

    # Language
    lang_score = norm(float(toefl or 0), 60, 120) if toefl else 40

    # Work
    work_score = min(100, work * 18)

    # Research
    res_map = {"none": 10, "minor": 35, "moderate": 65, "strong": 90}
    res_score = res_map.get(str(research).lower(), 10) + min(30, pubs * 15)
    res_score = min(100, res_score)

    # Internships
    intern_score = min(100, interns * 25)

    # Profile Quality
    sop_map  = {"basic draft": 30, "basic": 30, "good": 60, "strong": 85, "excellent": 100}
    lor_map  = {"weak": 20, "1-2 average lors": 40, "average": 40, "strong": 75, "exceptional": 100}
    ext_map  = {"none": 10, "minor": 35, "moderate": 65, "strong": 90}
    sop_val  = sop_map.get(str(sop_q).lower(), 30)
    lor_val  = lor_map.get(str(lor_q).lower(), 40)
    ext_val  = ext_map.get(str(extras).lower(), 10)
    profile_score = (sop_val + lor_val + ext_val) / 3

    # Weighted overall
    weights = {
        "academic": 0.22, "gre": 0.16, "awa": 0.05, "language": 0.08,
        "work": 0.14, "research": 0.14, "internships": 0.08, "profile": 0.13
    }
    overall = (
        academic      * weights["academic"] +
        gre_score     * weights["gre"] +
        awa_score     * weights["awa"] +
        lang_score    * weights["language"] +
        work_score    * weights["work"] +
        res_score     * weights["research"] +
        intern_score  * weights["internships"] +
        profile_score * weights["profile"]
    )

    return {
        "overall": round(overall),
        "dimensions": {
            "academic":    round(academic),
            "gre":         round(gre_score),
            "awa":         round(awa_score),
            "language":    round(lang_score),
            "work":        round(work_score),
            "research":    round(res_score),
            "internships": round(intern_score),
            "profile":     round(profile_score)
        }
    }


def get_profile_tier(score: int) -> dict:
    if score >= 85:
        return {"tier": "Elite", "color": "#7c3aed", "desc": "Top 5% of applicants worldwide"}
    elif score >= 72:
        return {"tier": "Strong", "color": "#2563eb", "desc": "Competitive for top-30 programs"}
    elif score >= 58:
        return {"tier": "Good", "color": "#16a34a", "desc": "Competitive for top-100 programs"}
    elif score >= 42:
        return {"tier": "Average", "color": "#d97706", "desc": "Target mid-range programs"}
    else:
        return {"tier": "Needs Work", "color": "#dc2626", "desc": "Focus on strengthening key areas"}
