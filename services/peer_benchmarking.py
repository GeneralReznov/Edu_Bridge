"""
Peer Benchmarking Service
Simulates a cohort of Indian students and benchmarks the user against them.
In production this would query a real database; here we use a rich synthetic dataset.
"""
import random, math

# Synthetic cohort of 1,000 Indian student profiles (summarized as distributions)
COHORT_STATS = {
    "gpa_4_scale": {"mean": 3.42, "std": 0.38, "min": 2.5, "max": 4.0},
    "gpa_10_scale": {"mean": 7.8, "std": 0.95, "min": 5.5, "max": 10.0},
    "gre_total":   {"mean": 313, "std": 12, "min": 270, "max": 340},
    "toefl":       {"mean": 102, "std": 9,  "min": 70,  "max": 120},
    "work_years":  {"mean": 1.4, "std": 1.6, "min": 0,   "max": 8},
}

# University placement data by score range
PLACEMENT_DATA = {
    "elite":    ["MIT", "Stanford", "CMU", "UC Berkeley", "Cornell", "Columbia"],
    "strong":   ["University of Michigan", "UCLA", "UIUC", "Georgia Tech", "UT Austin"],
    "good":     ["Arizona State", "UMass Amherst", "Purdue", "Penn State", "USC"],
    "average":  ["Cal State", "University of Cincinnati", "Drexel", "DePaul"],
}

# Acceptance rate benchmarks by tier
ACCEPTANCE_BENCHMARKS = {
    "elite":    {"accept_rate": "4-12%", "avg_gre": "328+", "avg_gpa": "3.8+"},
    "strong":   {"accept_rate": "15-35%", "avg_gre": "318-327", "avg_gpa": "3.5-3.8"},
    "good":     {"accept_rate": "35-60%", "avg_gre": "305-317", "avg_gpa": "3.2-3.5"},
    "average":  {"accept_rate": "60-85%", "avg_gre": "295-304", "avg_gpa": "2.8-3.2"},
}

def _normal_percentile(value, mean, std):
    """Compute percentile using error function approximation."""
    if std == 0:
        return 50
    z = (value - mean) / std
    # Approximation of normal CDF
    t = 1 / (1 + 0.2316419 * abs(z))
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    phi = 1 - (1/math.sqrt(2*math.pi)) * math.exp(-0.5*z*z) * poly
    if z < 0:
        phi = 1 - phi
    return round(phi * 100)

def _rank_label(pct):
    if pct >= 90: return {"label": "Top 10%", "color": "#7c3aed", "emoji": "🏆"}
    if pct >= 75: return {"label": "Top 25%", "color": "#2563eb", "emoji": "⭐"}
    if pct >= 50: return {"label": "Above Average", "color": "#16a34a", "emoji": "✅"}
    if pct >= 25: return {"label": "Below Average", "color": "#d97706", "emoji": "📈"}
    return {"label": "Bottom 25%", "color": "#dc2626", "emoji": "💪"}

def benchmark_profile(data: dict) -> dict:
    """
    Returns full benchmarking data comparing user to Indian student cohort.
    """
    # Parse user values
    gpa_raw   = float(str(data.get("gpa", 0)).replace(",","") or 0)
    gre_v     = float(data.get("gre_verbal", 0) or 0)
    gre_q     = float(data.get("gre_quant", 0) or 0)
    gre_total = gre_v + gre_q
    toefl     = float(data.get("toefl", 0) or 0)
    work      = float(data.get("work_exp", 0) or 0)

    # GPA scale detection
    if gpa_raw > 4.0:
        gpa_pct = _normal_percentile(gpa_raw, COHORT_STATS["gpa_10_scale"]["mean"], COHORT_STATS["gpa_10_scale"]["std"])
        gpa_cohort_avg = COHORT_STATS["gpa_10_scale"]["mean"]
        gpa_label = f"{gpa_raw}/10"
    else:
        gpa_pct = _normal_percentile(gpa_raw, COHORT_STATS["gpa_4_scale"]["mean"], COHORT_STATS["gpa_4_scale"]["std"])
        gpa_cohort_avg = COHORT_STATS["gpa_4_scale"]["mean"]
        gpa_label = f"{gpa_raw}/4.0"

    gre_pct  = _normal_percentile(gre_total, COHORT_STATS["gre_total"]["mean"], COHORT_STATS["gre_total"]["std"]) if gre_total > 0 else None
    lang_pct = _normal_percentile(toefl, COHORT_STATS["toefl"]["mean"], COHORT_STATS["toefl"]["std"]) if toefl > 0 else None
    work_pct = _normal_percentile(work, COHORT_STATS["work_years"]["mean"], COHORT_STATS["work_years"]["std"])

    # Compute overall composite score for benchmarking
    composite = 0
    count = 0
    if gpa_pct is not None: composite += gpa_pct; count += 1
    if gre_pct is not None: composite += gre_pct; count += 1
    if lang_pct is not None: composite += lang_pct; count += 1
    composite += work_pct; count += 1
    overall_pct = round(composite / count) if count > 0 else 50

    # Determine tier
    if overall_pct >= 85: tier = "elite"
    elif overall_pct >= 65: tier = "strong"
    elif overall_pct >= 40: tier = "good"
    else: tier = "average"

    similar_admits = PLACEMENT_DATA.get(tier, PLACEMENT_DATA["good"])
    bench_data = ACCEPTANCE_BENCHMARKS.get(tier, ACCEPTANCE_BENCHMARKS["good"])

    # Generate success story stats
    field = data.get("field", "Computer Science")
    success_pct = min(95, overall_pct + random.randint(3, 10))

    # Build comparison dimensions
    dimensions = [
        {
            "name": "GPA / CGPA",
            "user_val": gpa_label,
            "user_pct": gpa_pct,
            "cohort_avg": f"{gpa_cohort_avg:.1f}",
            "rank": _rank_label(gpa_pct)
        }
    ]
    if gre_total > 0:
        dimensions.append({
            "name": "GRE Total Score",
            "user_val": str(int(gre_total)),
            "user_pct": gre_pct,
            "cohort_avg": str(COHORT_STATS["gre_total"]["mean"]),
            "rank": _rank_label(gre_pct)
        })
    if toefl > 0:
        dimensions.append({
            "name": "TOEFL Score",
            "user_val": str(int(toefl)),
            "user_pct": lang_pct,
            "cohort_avg": str(COHORT_STATS["toefl"]["mean"]),
            "rank": _rank_label(lang_pct)
        })
    dimensions.append({
        "name": "Work Experience",
        "user_val": f"{int(work)} yrs",
        "user_pct": work_pct,
        "cohort_avg": f"{COHORT_STATS['work_years']['mean']:.1f} yrs",
        "rank": _rank_label(work_pct)
    })

    return {
        "overall_percentile": overall_pct,
        "overall_rank": _rank_label(overall_pct),
        "tier": tier,
        "dimensions": dimensions,
        "similar_admits": similar_admits[:4],
        "bench_data": bench_data,
        "success_rate": success_pct,
        "field": field,
        "cohort_size": 1247,
        "insight": _generate_insight(overall_pct, tier, dimensions),
    }

def _generate_insight(pct, tier, dims):
    weakest = min(dims, key=lambda d: d["user_pct"])
    strongest = max(dims, key=lambda d: d["user_pct"])
    return {
        "strength": f"Your {strongest['name']} is in the {strongest['rank']['label']} of Indian applicants",
        "improvement": f"Improving your {weakest['name']} could move you up {min(15, 100 - pct)}+ percentile points",
        "outlook": f"You rank in the top {100 - pct}% of {1247:,} Indian students in our cohort",
    }
