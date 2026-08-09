
import streamlit as st
from datetime import datetime


from ai.pipeline import (
    create_help_session,
    attach_exercise,
    attach_student_work,
    skip_student_work,
    analyze_exercise_image,
    analyze_student_work,
    start_tutor_session,
    create_learning_session,
    learn_concept,
    evaluate_learning_session
)

from storage.local_storage import (
    save_session,
    load_session,
    list_sessions,
    delete_session
)


# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(

    page_title="HintAI",

    page_icon="🧠",

    layout="centered"

)


# ==========================================
# INITIALISATION SESSION STREAMLIT
# ==========================================

if "page" not in st.session_state:

    st.session_state.page = "home"


if "help_session" not in st.session_state:

    st.session_state.help_session = None


if "learning_session" not in st.session_state:

    st.session_state.learning_session = None


if "exercise_file" not in st.session_state:

    st.session_state.exercise_file = None


if "work_file" not in st.session_state:

    st.session_state.work_file = None


if "exercise_analyzed" not in st.session_state:

    st.session_state.exercise_analyzed = False


if "work_analyzed" not in st.session_state:

    st.session_state.work_analyzed = False


if "current_hint" not in st.session_state:

    st.session_state.current_hint = None


if "hint_number" not in st.session_state:

    st.session_state.hint_number = 0


# ==========================================
# STYLE
# ==========================================

st.markdown(
"""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
}

.subtitle {
    font-size: 19px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(128,128,128,.25);
    margin-bottom: 15px;
}

</style>
""",
unsafe_allow_html=True
)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🧠 HintAI")

    st.divider()

    if st.button(
        "🏠 Accueil",
        use_container_width=True
    ):

        st.session_state.page = "home"

        st.rerun()


    if st.button(
        "💡 Help Me",
        use_container_width=True
    ):

        st.session_state.page = "help"

        st.rerun()


    if st.button(
        "📚 Apprendre un concept",
        use_container_width=True
    ):

        st.session_state.page = "learn"

        st.rerun()


    if st.button(
        "🗂️ Mon historique",
        use_container_width=True
    ):

        st.session_state.page = "history"

        st.rerun()


    if st.button(
        "👤 Mon profil",
        use_container_width=True
    ):

        st.session_state.page = "profile"

        st.rerun()


# ==========================================
# ACCUEIL
# ==========================================

if st.session_state.page == "home":

    st.markdown(
        '<div class="main-title">🧠 HintAI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Ton professeur IA qui te guide vers la solution.'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()


    st.info(
        "HintAI ne te donne pas directement la réponse. "
        "Il t'aide à comprendre et à construire la compétence."
    )


    st.subheader("Que veux-tu faire ?")


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "💡 HELP ME",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.page = "help"

            st.rerun()


    with col2:

        if st.button(
            "📚 APPRENDRE",
            use_container_width=True
        ):

            st.session_state.page = "learn"

            st.rerun()


    st.divider()


    st.subheader("🚀 Bientôt disponible")

    st.write(
        "📖 Épreuves BEPC / BAC"
    )

    st.write(
        "🎮 XP, séries et crédits"
    )

    st.write(
        "🏆 Progression par compétences"
    )


# ==========================================
# HELP ME
# ==========================================

elif st.session_state.page == "help":


    st.title("💡 Help Me")


    # --------------------------------------
    # ETAPE 1
    # --------------------------------------

    if st.session_state.help_session is None:

        st.header(
            "1️⃣ Ajoute ton exercice"
        )

        st.write(
            "Prends une photo ou importe ton exercice."
        )


        exercise_file = st.file_uploader(

            "Exercice",

            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "pdf"
            ],

            key="exercise_uploader"

        )


        if exercise_file:

            st.session_state.exercise_file = (
                exercise_file
            )


            st.success(
                "Exercice ajouté ✅"
            )


            if st.button(
                "Suivant ➜",
                type="primary"
            ):

                session = create_help_session()


                session = attach_exercise(
                    session,
                    exercise_file
                )


                st.session_state.help_session = (
                    session
                )


                st.rerun()


    # --------------------------------------
    # ETAPE 2
    # --------------------------------------

    else:

        session = (
            st.session_state.help_session
        )


        if not st.session_state.work_analyzed:


            st.header(
                "2️⃣ Montre ton travail"
            )


            st.write(
                "Ajoute ce que tu as déjà essayé."
            )


            work_file = st.file_uploader(

                "Ton travail",

                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "pdf"
                ],

                key="work_uploader"

            )


            col1, col2 = st.columns(2)


            with col1:

                if work_file:

                    if st.button(
                        "Continuer ➜",
                        type="primary"
                    ):

                        session = attach_student_work(
                            session,
                            work_file
                        )


                        st.session_state.work_file = (
                            work_file
                        )


                        result = analyze_student_work(
                            session,
                            work_file
                        )


                        if result["success"]:

                            st.session_state.help_session = (
                                session
                            )

                            st.session_state.work_analyzed = True

                            st.rerun()

                        else:

                            st.error(
                                result["error"]
                            )


            with col2:

                if st.button(
                    "Sauter",
                ):

                    session = skip_student_work(
                        session
                    )


                    st.session_state.help_session = (
                        session
                    )


                    st.session_state.work_analyzed = True

                    st.rerun()


        # ----------------------------------
        # ANALYSE EXERCICE
        # ----------------------------------

        if (
            st.session_state.work_analyzed
            and
            not st.session_state.exercise_analyzed
        ):


            st.header(
                "3️⃣ Analyse de l'exercice"
            )


            st.write(
                "HintAI vérifie la qualité du document "
                "avant de l'envoyer au moteur."
            )


            exercise_file = (
                st.session_state.exercise_file
            )


            if st.button(
                "Analyser l'exercice",
                type="primary"
            ):

                with st.spinner(
                    "Analyse en cours..."
                ):

                    result = analyze_exercise_image(

                        session,

                        exercise_file

                    )


                if result["success"]:

                    st.session_state.help_session = (
                        session
                    )

                    st.session_state.exercise_analyzed = True

                    st.success(
                        "Exercice analysé ✅"
                    )

                    st.rerun()

                else:

                    st.error(
                        result["error"]
                    )


        # ----------------------------------
        # TUTEUR
        # ----------------------------------

        if st.session_state.exercise_analyzed:


            st.header(
                "4️⃣ Ton professeur HintAI"
            )


            if st.session_state.current_hint is None:

                if st.button(
                    "Obtenir l'indice 1 💡",
                    type="primary"
                ):

                    result = start_tutor_session(
                        session
                    )


                    st.session_state.help_session = (
                        result["session"]
                    )


                    st.session_state.current_hint = (
                        result["hint"]
                    )


                    st.session_state.hint_number = 1

                    st.rerun()


            else:

                st.info(
                    f"💡 Indice "
                    f"{st.session_state.hint_number}"
                )


                st.write(
                    st.session_state.current_hint
                )


                st.divider()


                st.subheader(
                    "🤔 Tu es bloqué ?"
                )


                question = st.text_input(
                    "Pose ta question à HintAI",
                    key="student_question"
                )


                if st.button(
                    "Envoyer la question"
                ):

                    if question.strip():

                        st.warning(
                            "Le moteur de dialogue sera "
                            "connecté à cette zone dans "
                            "la prochaine couche du parcours."
                        )


                if st.button(
                    "Indice suivant ➜"
                ):

                    st.session_state.hint_number += 1

                    st.warning(
                        "Indice suivant à générer "
                        "par le moteur pédagogique."
                    )


                st.divider()


                st.subheader(
                    "🎯 Quand tu penses avoir trouvé"
                )


                if st.button(
                    "J'ai terminé"
                ):

                    st.success(
                        "Parfait ! La phase d'évaluation "
                        "va maintenant vérifier ta démarche."
                    )


# ==========================================
# LEARN A CONCEPT
# ==========================================

elif st.session_state.page == "learn":


    st.title(
        "📚 Apprendre un concept"
    )


    st.write(
        "Choisis une notion et laisse HintAI "
        "construire ton parcours d'apprentissage."
    )


    concept = st.text_input(
        "Quel concept veux-tu apprendre ?",
        placeholder="Exemple : équation du second degré"
    )


    class_level = st.selectbox(

        "Ta classe",

        [
            "6ème",
            "5ème",
            "4ème",
            "3ème",
            "Seconde",
            "Première",
            "Terminale"
        ]

    )


    st.subheader(
        "Exercices que tu possèdes "
        "(facultatif)"
    )


    examples = st.file_uploader(

        "Ajoute jusqu'à 3 exercices",

        type=[
            "png",
            "jpg",
            "jpeg",
            "pdf"
        ],

        accept_multiple_files=True,

        key="learning_examples"

    )


    if len(examples) > 3:

        st.warning(
            "Tu peux ajouter au maximum 3 exercices."
        )

        examples = examples[:3]


    student_work = st.file_uploader(

        "Ton travail "
        "(facultatif)",

        type=[
            "png",
            "jpg",
            "jpeg",
            "pdf"
        ],

        key="learning_work"

    )


    if st.button(
        "Commencer l'apprentissage 🚀",
        type="primary"
    ):


        if not concept.strip():

            st.error(
                "Entre d'abord le concept à apprendre."
            )

        else:

            learning_session = (
                create_learning_session(

                    concept,

                    class_level

                )
            )


            for example in examples:

                learning_session.add_example(
                    example.name
                )


            if student_work:

                learning_session.set_student_work(
                    student_work.name
                )


            with st.spinner(
                "Ton parcours est en préparation..."
            ):

                learning_session = learn_concept(
                    learning_session
                )


            st.session_state.learning_session = (
                learning_session
            )


            st.success(
                "Parcours créé ✅"
            )


    # --------------------------------------
    # RESULTAT APPRENTISSAGE
    # --------------------------------------

    if st.session_state.learning_session:

        learning_session = (
            st.session_state.learning_session
        )


        st.divider()


        st.header(
            "🧠 Ton cours personnalisé"
        )


        st.write(
            learning_session.explanation
        )


        st.divider()


        st.header(
            "🎯 Exercice guidé"
        )


        st.write(
            learning_session.guided_exercise
        )


        st.info(
            "La correction assistée et l'évaluation "
            "seront conservées dans ta session."
        )


# ==========================================
# HISTORIQUE
# ==========================================

elif st.session_state.page == "history":


    st.title(
        "🗂️ Mon historique"
    )


    sessions = list_sessions()


    if not sessions:

        st.info(
            "Aucune session enregistrée pour le moment."
        )


    else:

        for session in sessions:

            session_id = session.get(
                "session_id",
                "unknown"
            )


            created = session.get(
                "created_at",
                ""
            )


            with st.expander(
                f"📚 Session {created}"
            ):

                st.json(
                    session
                )


                if st.button(
                    "Supprimer",
                    key=f"delete_{session_id}"
                ):

                    delete_session(
                        session_id
                    )

                    st.rerun()


# ==========================================
# PROFIL
# ==========================================

elif st.session_state.page == "profile":


    st.title(
        "👤 Mon profil"
    )


    st.info(
        "Le système d'authentification sera "
        "branché dans le prochain bloc."
    )


    st.text_input(
        "Nom",
        placeholder="Ton prénom"
    )


    st.selectbox(
        "Classe",
        [
            "6ème",
            "5ème",
            "4ème",
            "3ème",
            "Seconde",
            "Première",
            "Terminale"
        ]
    )


    st.selectbox(
        "Matière préférée",
        [
            "Maths",
            "Physique",
            "Chimie"
        ]
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "HintAI V1 • Ton professeur IA, "
    "conçu pour te faire comprendre plutôt "
    "que simplement te donner la réponse."
)
