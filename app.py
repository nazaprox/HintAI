import streamlit as st
from datetime import date

from config import (
    CREDIT_COSTS,
    PREMIUM_PACKAGES,
    FREE_MONTHLY_CREDITS,
)

from quality import quality_check

from storage import (
    init_storage,
    daily_login,
    get_credits,
    spend_credits,
    add_credits,
    save_history,
    get_history,
    can_ask_question,
    register_question,
)

from ai import (
    analyze_exercise,
    ask_student_question,
    learn_concept,
)


# ============================================================
# CONFIG STREAMLIT
# ============================================================

st.set_page_config(
    page_title="HintAI",
    page_icon="🧠",
    layout="centered",
)


# ============================================================
# STORAGE
# ============================================================

init_storage()

reward = daily_login()


# ============================================================
# HEADER
# ============================================================

st.title("🧠 HintAI")

st.caption(
    "Ton professeur IA : comprendre avant de répondre."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("👤 Mon compte")

    st.metric(
        "💳 Crédits",
        get_credits()
    )

    st.metric(
        "🔥 Série",
        st.session_state.streak
    )

    if reward > 0:

        st.success(
            f"🎁 +{reward} crédits aujourd'hui !"
        )

    st.divider()

    st.write("### 📺 Publicité")

    st.info(
        "Emplacement réservé aux Rewarded Ads."
    )

    st.divider()

    st.write("### 💎 Premium")

    st.write(
        "Des packs de crédits plus généreux."
    )


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Menu",
    [
        "🏠 Accueil",
        "🆘 Help Me",
        "🧠 Apprendre",
        "📚 BEPC / BAC",
        "💎 Premium",
        "💾 Historique",
        "👤 Compte",
    ],
)


# ============================================================
# ACCUEIL
# ============================================================

if page == "🏠 Accueil":

    st.header("Bienvenue sur HintAI 👋")

    st.write(
        "Apprends à résoudre tes exercices avec "
        "des indices progressifs."
    )

    st.divider()

    st.subheader("🚀 Commencer")

    if st.button(
        "🆘 HELP ME",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.open_help = True

        st.rerun()

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "📷 Photo\n\n"
            "Analyse ton exercice."
        )

    with col2:

        st.info(
            "🧠 Apprentissage\n\n"
            "Maîtrise une compétence."
        )

    st.divider()

    st.subheader("🎯 Notre méthode")

    st.write(
        """
**Pas de réponse jetée à la figure.**

HintAI commence par un indice.

Puis un deuxième.

Puis un troisième.

Et seulement ensuite une résolution complète
si elle est nécessaire.

Enfin, HintAI vérifie si tu as réellement compris.
"""
    )


# ============================================================
# HELP ME
# ============================================================

elif page == "🆘 Help Me":

    st.header("🆘 Help Me")

    st.progress(
        min(
            st.session_state.help_me_step / 5,
            1.0
        )
    )

    # ========================================================
    # ETAPE 1
    # ========================================================

    if st.session_state.help_me_step == 1:

        st.subheader("1️⃣ Ajoute ton exercice")

        st.write(
            "Prends une photo ou importe ton exercice."
        )

        camera = st.camera_input(
            "📷 Prendre une photo"
        )

        upload = st.file_uploader(
            "📁 Image ou PDF",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "pdf",
            ],
            key="exercise",
        )

        selected = camera or upload

        if selected is not None:

            st.session_state.exercise_file = selected

            result = quality_check(selected)

            st.session_state.exercise_quality = result

            if result["valid"]:

                st.success(
                    "✅ Contrôle qualité réussi."
                )

                if result["type"] == "image":

                    st.image(
                        selected,
                        use_container_width=True,
                    )

                if st.button(
                    "➡️ Suivant",
                    type="primary",
                    use_container_width=True,
                ):

                    st.session_state.help_me_step = 2

                    st.rerun()

            else:

                st.error(
                    "❌ " + result["message"]
                )

                st.warning(
                    "L'image n'est pas envoyée à Gemini."
                )


    # ========================================================
    # ETAPE 2
    # ========================================================

    elif st.session_state.help_me_step == 2:

        st.subheader("2️⃣ Ton travail")

        st.write(
            "Ajoute ton brouillon si tu en as un."
        )

        camera = st.camera_input(
            "📷 Photographier mon travail",
            key="work_camera",
        )

        upload = st.file_uploader(
            "📁 Importer mon travail",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "pdf",
            ],
            key="work",
        )

        selected = camera or upload

        if selected is not None:

            result = quality_check(selected)

            st.session_state.work_quality = result

            if result["valid"]:

                st.session_state.work_file = selected

                st.success(
                    "✅ Travail accepté."
                )

                if result["type"] == "image":

                    st.image(
                        selected,
                        use_container_width=True,
                    )

            else:

                st.error(
                    "❌ " + result["message"]
                )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "⏭️ Passer",
                use_container_width=True,
            ):

                st.session_state.work_file = None

                st.session_state.help_me_step = 3

                st.rerun()

        with col2:

            if st.button(
                "➡️ Suivant",
                type="primary",
                use_container_width=True,
            ):

                st.session_state.help_me_step = 3

                st.rerun()


    # ========================================================
    # ETAPE 3
    # ========================================================

    elif st.session_state.help_me_step == 3:

        st.subheader("3️⃣ Analyse")

        st.info(
            "L'image validée va maintenant être envoyée "
            "à Gemini."
        )

        student_class = st.selectbox(
            "Ta classe",
            [
                "3ème",
                "Seconde",
                "Première",
                "Terminale",
                "Autre",
            ],
        )

        if st.button(
            "🔎 Analyser",
            type="primary",
            use_container_width=True,
        ):

            if not spend_credits(
                CREDIT_COSTS["help_me"]
            ):

                st.error(
                    "❌ Tu n'as plus assez de crédits."
                )

                st.info(
                    "Gagne des crédits avec les "
                    "récompenses ou passe en Premium."
                )

            else:

                with st.spinner(
                    "🧠 HintAI analyse ton exercice..."
                ):

                    try:

                        result = analyze_exercise(
                            st.session_state.exercise_file,
                            st.session_state.work_file,
                            student_class,
                        )

                        st.session_state.analysis = result

                        st.session_state.help_me_step = 4

                        save_history({
                            "date": str(date.today()),
                            "type": "Help Me",
                            "analysis": result,
                        })

                        st.rerun()

                    except Exception as e:

                        add_credits(
                            CREDIT_COSTS["help_me"]
                        )

                        st.error(
                            f"❌ Erreur : {e}"
                        )


    # ========================================================
    # ETAPE 4 : INDICES
    # ========================================================

    elif st.session_state.help_me_step == 4:

        st.subheader("💡 Ton accompagnement")

        st.success(
            "HintAI a analysé ton exercice."
        )

        st.write(
            st.session_state.analysis
        )

        st.divider()

        st.subheader("💡 Indice 1")

        st.info(
            "Commence par identifier la notion "
            "ou la formule nécessaire."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "❓ Je veux poser une question",
                use_container_width=True,
            ):

                st.session_state.help_me_step = 5

                st.rerun()

        with col2:

            if st.button(
                "➡️ Indice 2",
                type="primary",
                use_container_width=True,
            ):

                st.session_state.help_me_step = 6

                st.rerun()


    # ========================================================
    # ETAPE 5 : QUESTION
    # ========================================================

    elif st.session_state.help_me_step == 5:

        st.subheader("❓ Pose ta question")

        question = st.text_area(
            "Qu'est-ce qui te bloque ?",
            placeholder=(
                "Exemple : je ne comprends pas "
                "quelle formule utiliser."
            ),
        )

        if st.button(
            "💬 Demander à HintAI",
            type="primary",
            use_container_width=True,
        ):

            if not can_ask_question():

                st.error(
                    "Tu as atteint ta limite quotidienne."
                )

            else:

                answer = ask_student_question(
                    st.session_state.analysis,
                    question,
                )

                register_question()

                st.session_state.questions.append({
                    "question": question,
                    "answer": answer,
                })

                st.write(answer)

        st.divider()

        if st.button(
            "➡️ Continuer vers l'indice 2",
            use_container_width=True,
        ):

            st.session_state.help_me_step = 6

            st.rerun()


    # ========================================================
    # INDICE 2
    # ========================================================

    elif st.session_state.help_me_step == 6:

        st.subheader("💡 Indice 2")

        st.info(
            "Maintenant, précise la méthode : "
            "quelle formule, propriété ou transformation "
            "peut te permettre d'avancer ?"
        )

        if st.button(
            "➡️ Indice 3",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.help_me_step = 7

            st.rerun()


    # ========================================================
    # INDICE 3
    # ========================================================

    elif st.session_state.help_me_step == 7:

        st.subheader("💡 Indice 3")

        st.warning(
            "Tu as maintenant une piste très précise."
        )

        st.write(
            "Effectue l'étape indiquée et vérifie "
            "ton résultat."
        )

        if st.button(
            "🧾 Voir la résolution",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.help_me_step = 8

            st.rerun()


    # ========================================================
    # RESOLUTION
    # ========================================================

    elif st.session_state.help_me_step == 8:

        st.subheader("🧾 Résolution")

        resolution = ask_student_question(
            st.session_state.analysis,
            """
Maintenant donne la résolution complète de
l'exercice.

Explique chaque étape.

Montre pourquoi chaque formule ou méthode
est utilisée.

Termine par le résultat.

Ajoute une section :
"Ce qu'il faut retenir".
""",
        )

        st.write(resolution)

        st.session_state.resolution = resolution

        if st.button(
            "🎓 Passer à l'évaluation",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.help_me_step = 9

            st.rerun()


    # ========================================================
    # EVALUATION
    # ========================================================

    elif st.session_state.help_me_step == 9:

        st.subheader("🎓 Validation de compétence")

        st.write(
            "Dernière étape : vérifier que tu sais "
            "maintenant refaire la méthode."
        )

        evaluation = st.text_area(
            "Explique avec tes mots comment résoudre "
            "ce type d'exercice."
        )

        if st.button(
            "✅ Vérifier ma compréhension",
            type="primary",
            use_container_width=True,
        ):

            if not spend_credits(
                CREDIT_COSTS["evaluation"]
            ):

                st.error(
                    "Pas assez de crédits."
                )

            else:

                result = ask_student_question(
                    st.session_state.analysis,
                    f"""
Évalue cette explication de l'élève :

{evaluation}

Dis :

1. compétence maîtrisée ou non
2. erreur éventuelle
3. conseil
4. niveau de maîtrise
5. ce que l'élève doit retravailler
""",
                )

                st.session_state.evaluation = result

                st.success(
                    "🎯 Évaluation terminée."
                )

                st.write(result)

                if st.button(
                    "🏠 Nouvel exercice"
                ):

                    st.session_state.help_me_step = 1
                    st.session_state.exercise_file = None
                    st.session_state.work_file = None
                    st.rerun()


# ============================================================
# APPRENDRE
# ============================================================

elif page == "🧠 Apprendre":

    st.header("🧠 Apprendre un concept")

    concept = st.text_input(
        "Quel concept veux-tu apprendre ?",
        placeholder="Ex : dérivées",
    )

    student_class = st.selectbox(
        "Ta classe",
        [
            "6ème",
            "5ème",
            "4ème",
            "3ème",
            "Seconde",
            "Première",
            "Terminale",
        ],
    )

    st.write(
        "### 📚 Tes exercices personnels"
    )

    files = st.file_uploader(
        "Jusqu'à 3 exercices (optionnel)",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
            "pdf",
        ],
        accept_multiple_files=True,
    )

    if len(files) > 3:

        st.warning(
            "Maximum 3 exercices."
        )

        files = files[:3]

    work = st.file_uploader(
        "Ton travail (optionnel)",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
            "pdf",
        ],
        key="concept_work",
    )

    if st.button(
        "🚀 Apprendre",
        type="primary",
        use_container_width=True,
    ):

        if not concept.strip():

            st.warning(
                "Entre un concept."
            )

        elif not spend_credits(
            CREDIT_COSTS["concept"]
        ):

            st.error(
                "Pas assez de crédits."
            )

        else:

            with st.spinner(
                "🧠 Préparation de ton parcours..."
            ):

                try:

                    result = learn_concept(
                        concept,
                        student_class,
                    )

                    st.subheader(
                        "📚 Ton parcours"
                    )

                    st.write(result)

                except Exception as e:

                    add_credits(
                        CREDIT_COSTS["concept"]
                    )

                    st.error(
                        f"Erreur : {e}"
                    )


# ============================================================
# BEPC / BAC
# ============================================================

elif page == "📚 BEPC / BAC":

    st.header("📚 Bibliothèque BEPC & BAC")

    st.info(
        "La bibliothèque de fichiers sera branchée "
        "sur notre stockage dans l'étape suivante."
    )

    st.subheader("🆓 Gratuit")

    st.write(
        "Épreuves gratuites avec publicité."
    )

    st.subheader("💎 Premium")

    st.write(
        "Épreuves premium accessibles avec crédits."
    )

    st.write(
        "📐 Maths   •   ⚡ Physique   •   🧪 Chimie"
    )


# ============================================================
# PREMIUM
# ============================================================

elif page == "💎 Premium":

    st.header("💎 Premium")

    st.write(
        "Choisis ton pack."
    )

    for name, package in PREMIUM_PACKAGES.items():

        if name == "30$":

            st.subheader(
                "🔥 Offre spéciale 30$"
            )

            st.write(
                "2 Help Me complets"
            )

            st.write(
                "3 indices + résolution"
            )

            st.write(
                "5 questions avec validation par jour"
            )

        else:

            st.subheader(
                f"💳 Pack {name}"
            )

            st.write(
                f"{package['credits']} crédits"
            )

        if st.button(
            f"Choisir {name}",
            key=f"premium_{name}",
            use_container_width=True,
        ):

            st.info(
                "💳 Paiement à connecter."
            )


# ============================================================
# HISTORIQUE
# ============================================================

elif page == "💾 Historique":

    st.header("💾 Mon historique")

    history = get_history()

    if not history:

        st.info(
            "Aucun exercice enregistré."
        )

    else:

        for index, item in enumerate(
            reversed(history),
            1,
        ):

            with st.expander(
                f"Exercice {index} • {item['date']}"
            ):

                st.write(
                    item.get("analysis", "")
                )


# ============================================================
# COMPTE
# ============================================================

elif page == "👤 Compte":

    st.header("👤 Mon compte")

    st.write(
        "### Connexion Google"
    )

    st.info(
        "L'authentification Google sera activée "
        "avec les paramètres OAuth/OIDC de "
        "Streamlit Community Cloud."
    )

    st.write(
        f"💳 Crédits : {get_credits()}"
    )

    st.write(
        f"🔥 Série : {st.session_state.streak} jours"
    )

    st.write(
        f"💎 Premium : "
        f"{'Oui' if st.session_state.is_premium else 'Non'}"
    )