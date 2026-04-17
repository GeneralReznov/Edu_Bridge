"""
Adaptive Learning Service
Tracks user interactions and recommends next-best actions.
"""
from datetime import datetime

# Recommendation rules based on completed modules
NEXT_ACTIONS = {
    "career_navigator": [
        {"action": "admission_predictor", "reason": "Check your admission chances for the universities you shortlisted", "url": "/admission-predictor", "xp": 90},
        {"action": "roi_calculator", "reason": "Calculate the ROI of your preferred programs", "url": "/roi-calculator", "xp": 80},
    ],
    "roi_calculator": [
        {"action": "loan_planner", "reason": "Plan how to finance your education with the best loan", "url": "/loan-planner", "xp": 120},
        {"action": "application_strategy", "reason": "Get a personalized application strategy", "url": "/application-strategy", "xp": 110},
    ],
    "admission_predictor": [
        {"action": "application_strategy", "reason": "Build a targeted application strategy based on your chances", "url": "/application-strategy", "xp": 110},
        {"action": "peer_benchmarks", "reason": "See how you compare to other Indian students", "url": "/peer-benchmarks", "xp": 75},
    ],
    "loan_planner": [
        {"action": "timeline_generator", "reason": "Create a month-by-month application roadmap", "url": "/timeline-generator", "xp": 70},
        {"action": "analytics", "reason": "View your complete progress analytics", "url": "/analytics", "xp": 50},
    ],
    "timeline_generator": [
        {"action": "chatbot", "reason": "Ask EduMentor for any specific doubts about your plan", "url": "/chatbot", "xp": 50},
    ],
    "application_strategy": [
        {"action": "loan_planner", "reason": "Now plan your education financing", "url": "/loan-planner", "xp": 120},
        {"action": "university_comparison", "reason": "Deep-compare your shortlisted universities", "url": "/university-comparison", "xp": 85},
    ],
    "peer_benchmarks": [
        {"action": "application_strategy", "reason": "Build a strategy based on your benchmarking results", "url": "/application-strategy", "xp": 110},
    ],
}

# Learning content recommendations by profile gap
CONTENT_RECS = {
    "gre_low": {
        "title": "GRE Preparation Masterplan",
        "icon": "fas fa-brain",
        "items": [
            "Manhattan Prep GRE (highest rated course)",
            "Magoosh GRE (best value for money)",
            "ETS Official GRE Practice Tests (mandatory)",
            "GregMat+ YouTube channel (free)",
        ]
    },
    "toefl_low": {
        "title": "TOEFL/IELTS Preparation",
        "icon": "fas fa-language",
        "items": [
            "Magoosh TOEFL prep course",
            "British Council IELTS resources",
            "ETS TOEFL official practice",
            "EnglishClub listening exercises",
        ]
    },
    "research_low": {
        "title": "Build Research Profile",
        "icon": "fas fa-flask",
        "items": [
            "Apply for IIT/NIT research internships",
            "Contribute to GitHub open source projects",
            "Write technical blog posts on Medium",
            "Apply for SURGE/SRP summer programs",
        ]
    },
    "work_low": {
        "title": "Strengthen Work Experience",
        "icon": "fas fa-briefcase",
        "items": [
            "Seek leadership roles in current position",
            "Document quantifiable impact of your work",
            "Apply for industry certifications (AWS, GCP, CFA)",
            "Take on cross-functional projects",
        ]
    }
}

def get_adaptive_recommendations(profile_session: dict) -> dict:
    """Generate next-best-action recommendations based on session state."""
    completed = profile_session.get("completed_modules", [])
    xp = profile_session.get("xp", 0)
    streak = profile_session.get("streak", 0)

    # Find uncompleted next actions
    recommendations = []
    for module in completed:
        for action in NEXT_ACTIONS.get(module, []):
            if action["action"] not in completed:
                if not any(r["action"] == action["action"] for r in recommendations):
                    recommendations.append(action)

    # If nothing completed, start recommendations
    if not recommendations:
        recommendations = [
            {"action": "career_navigator", "reason": "Start with an AI analysis of your profile", "url": "/career-navigator", "xp": 100},
            {"action": "chatbot", "reason": "Chat with EduMentor for instant guidance", "url": "/chatbot", "xp": 50},
        ]

    # Engagement nudge
    nudge = None
    if streak == 0:
        nudge = {"type": "streak", "message": "Start your daily streak today — consistent users get 40% better results!"}
    elif xp < 100:
        nudge = {"type": "xp", "message": f"You have {xp} XP. Complete 1 more tool to unlock your first achievement badge!"}
    elif len(completed) >= 5:
        nudge = {"type": "achievement", "message": "🌟 You're an All-Rounder! Share your EduBridge journey with friends."}

    return {
        "recommendations": recommendations[:3],
        "nudge": nudge,
        "completion_pct": round(len(completed) / 7 * 100),
        "tools_remaining": max(0, 7 - len(completed)),
    }
