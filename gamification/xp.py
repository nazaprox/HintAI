

# ==========================================
# SYSTEME XP
# ==========================================


XP_REWARDS = {

    "exercise_completed": 20,

    "skill_mastered": 50,

    "daily_login": 5,

    "perfect_solution": 30

}




def add_xp(current_xp, action):

    reward = XP_REWARDS.get(
        action,
        0
    )


    return current_xp + reward





def get_level(xp):

    """
    Calcul niveau élève.
    """

    if xp < 100:
        return 1

    elif xp < 300:
        return 2

    elif xp < 600:
        return 3

    elif xp < 1000:
        return 4

    else:
        return 5

