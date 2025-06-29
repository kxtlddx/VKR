import math
import pytest
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
    assert any(u["user_id"] == 2 and u["total_score"] == 100 for u in result)

@pytest.mark.parametrize("score,expected_level", [
    (   0, 0),
    (  50, 0),
    ( 100, 1),
    ( 250, 1),
    ( 300, 2),
    ( 599, 2),
    ( 600, 3),
    ( 999, 3),
    (1000, 4),
    (1500, 5),
])
def test_get_achievement_level(score, expected_level):
    assert get_achievement_level(1, score) == expected_level

def test_level_score_current_and_full():
    # for level 2 threshold=300; level 3 threshold=600
    lvl = 2
    score = 350
    curr = get_level_score_curr(1, lvl, score)
    full = get_level_score_full(1, lvl, score)
    assert curr == 50
    assert full == 300
