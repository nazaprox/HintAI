import streamlit as st
from datetime import date, timedelta


# ============================================================
# INITIALISATION
# ============================================================

def init_storage():

    defaults = {
        "credits": 30,
        "streak": 0,
        "last_login": None,

        "history": [],

        "help_me_step": 1,

        "exercise_file": None,
        "work_file": None,

        "exercise_quality": None,
        "work_quality": None,

        "analysis": None,

        "hint1": None,
        "hint2": None,
        "hint3": None,

        "questions": [],

        "resolution": None,

        "evaluation": None,

        "is_premium": False,

        "premium_package": None,

        "daily_questions": 0,
        "daily_question_date": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ============================================================
# CREDITS
# ============================================================

def get_credits():

    return st.session_state.credits


def spend_credits(amount):

    if st.session_state.credits < amount:

        return False

    st.session_state.credits -= amount

    return True


def add_credits(amount):

    st.session_state.credits += amount


# ============================================================
# HISTORIQUE
# ============================================================

def save_history(item):

    st.session_state.history.append(item)


def get_history():

    return st.session_state.history


# ============================================================
# SERIE QUOTIDIENNE
# ============================================================

def daily_login():

    today = date.today()

    last_login = st.session_state.last_login

    if last_login == str(today):

        return 0

    if last_login is None:

        st.session_state.streak = 1

    else:

        previous = date.fromisoformat(last_login)

        if today == previous + timedelta(days=1):

            st.session_state.streak += 1

        else:

            # La série est cassée.
            st.session_state.streak = 1

    st.session_state.last_login = str(today)

    rewards = {
        1: 0,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 10,
    }

    reward = rewards.get(
        st.session_state.streak,
        10
    )

    if reward > 0:

        add_credits(reward)

    return reward


# ============================================================
# QUESTIONS QUOTIDIENNES
# ============================================================

def reset_daily_questions():

    today = str(date.today())

    if st.session_state.daily_question_date != today:

        st.session_state.daily_question_date = today
        st.session_state.daily_questions = 0


def can_ask_question():

    reset_daily_questions()

    if st.session_state.is_premium:
        return st.session_state.daily_questions < 5

    return True


def register_question():

    reset_daily_questions()

    st.session_state.daily_questions += 1