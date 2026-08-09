
from gamification.credits import (
    add_credits,
    add_xp
)



def exercise_completed():


    add_xp(10)

    add_credits(3)



def skill_mastered():


    add_xp(50)

    add_credits(10)



def daily_reward(streak):


    reward = min(
        streak,
        10
    )


    add_credits(
        reward
    )


    return reward
