import math

def transform_achievements_for_leaderboard(achievements):
    user_scores = {}
    for ach in achievements:
        user_scores.setdefault(ach.user_id, 0)
        user_scores[ach.user_id] += ach.score

    return [{"user_id": uid, "total_score": score} for uid, score in user_scores.items()]


BASE_EXP = 100
FACTOR = 2
def get_level_threshold(level: int) -> int:
    # Quadratic formula: 50 * level^2 + 50 * level
    return 50 * level * level + 50 * level

def get_achievement_level(achievement_id: int, score: int) -> int:
    level = 0
    while score >= get_level_threshold(level + 1):
        level += 1
    return level

def get_level_score_curr(achievement_id: int, level: int, score: int) -> int:
    required_prev = get_level_threshold(level)
    return score - required_prev

def get_level_score_full(achievement_id: int, level: int, score: int) -> int:
    return get_level_threshold(level + 1) - get_level_threshold(level)
