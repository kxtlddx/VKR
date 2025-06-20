from logic import (
    transform_achievements_for_leaderboard,
    get_achievement_level,
    get_level_score_curr,
    get_level_score_full
)

class DummyAchievement:
    def __init__(self, user_id, score):
        self.user_id = user_id
        self.score = score

def test_leaderboard_aggregation():
    data = [
        DummyAchievement(1, 500),
        DummyAchievement(2, 100),
        DummyAchievement(1, 200)
    ]
    result = transform_achievements_for_leaderboard(data)
    assert any(u["user_id"] == 1 and u["total_score"] == 700 for u in result)

def test_achievement_leveling():
    assert get_achievement_level(1, 900) == 1
    assert get_achievement_level(1, 1200) == 2

def test_level_score_current():
    assert get_level_score_curr(1, 2, 1250) == 250

def test_level_score_full():
    assert get_level_score_full(1, 2, 1250) == 1000
