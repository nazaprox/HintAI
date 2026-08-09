import streamlit as st
import base64
import json
from datetime import datetime

from PIL import Image
import cv2
import numpy as np
import fitz

from config import (
    APP_NAME,
    APP_VERSION,
    GEMINI_MODEL,
    FREE_INITIAL_CREDITS,
    HELP_ME_COST,
    LEARN_CONCEPT_COST,
    EXTRA_QUESTION_COST,
    MAX_IMAGE_SIZE_MB,
    MAX_HISTORY_ITEMS,
    SUBJECTS,
    CLASS_LEVELS,
    PLANS,
    ADS_ENABLED,
    REWARDED_AD_CREDIT_REWARD,
    validate_config,
)

from ai import (
    help_me,
    help_me_image,
    next_hint,
    ask_student_question,
    validate_skill,
    learn_concept,
    test_connection,
)


# ============================================================
# CONFIG STREAMLIT
# ============================================================

st.set_page_config(
    page_title="HintAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CHARGEMENT CSS
# ============================================================

def load_css():
    try:
        with open("styles.css", "r", encoding="utf-8") as file:
            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )

    except FileNotFoundError:
        pass


load_css()


# ============================================================
# INITIALISATION SESSION
# ============================================================

def init_session():

    if "credits" not in st.session_state:
        st.session_state.credits = FREE_INITIAL_CREDITS

    if "plan" not in st.session_state:
        st.session_state.plan = "Free"

    if "history" not in st.session_state:
        st.session_state.history = []

    if "page" not in st.session_state:
        st.session_state.page = "Accueil"

    if "help_step" not in st.session_state:
        st.session_state.help_step = 1

    if "exercise_file" not in st.session_state:
        st.session_state.exercise_file = None

    if "student_file" not in st.session_state:
        st.session_state.student_file = None

    if "exercise_bytes" not in st.session_state:
        st.session_state.exercise_bytes = None

    if "student_bytes" not in st.session_state:
        st.session_state.student_bytes = None

    if "exercise_mime" not in st.session_state:
        st.session_state.exercise_mime = None

    if "student_mime" not in st.session_state:
        st.session_state.student_mime = None

    if "exercise_context" not in st.session_state:
        st.session_state.exercise_context = ""

    if "student_context" not in st.session_state:
        st.session_state.student_context = ""

    if "current_response" not in st.session_state:
        st.session_state.current_response = ""

    if "hint_level" not in st.session_state:
        st.session_state.hint_level = 1

    if "subject" not in st.session_state:
        st.session_state.subject = "Mathématiques"

    if "level" not in st.session_state:
        st.session_state.level = "3ème"

    if "history_loaded" not in st.session_state:
        st.session_state.history_loaded = False


init_session()


# ============================================================
# UTILITAIRES
# ============================================================

def add_history(title, content, mode):
    item = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": mode,
        "title": title,
        "content": content,
    }

    st.session_state.history.insert(0, item)

    st.session_state.history = (
        st.session_state.history[:MAX_HISTORY_ITEMS]
    )


def can_spend(amount):
    return st.session_state.credits >= amount


def spend_credits(amount):
    if not can_spend(amount):
        return False

    st.session_state.credits -= amount
    return True


def add_credits(amount):
    st.session_state.credits += amount


def get_file_bytes(uploaded_file):
    if uploaded_file is None:
        return None

    return uploaded_file.getvalue()


def file_size_ok(uploaded_file):
    if uploaded_file is None:
        return False

    size_mb = uploaded_file.size / (1024 * 1024)

    return size_mb <= MAX_IMAGE_SIZE_MB


# ============================================================
# CONTRÔLE QUALITÉ IMAGE LOCAL
# ============================================================

def quality_check_image(image_bytes):
    """
    Contrôle qualité local avec OpenCV.

    Ce contrôle ne fait PAS de reconnaissance de contenu.
    Il vérifie principalement si l'image est exploitable.
    """

    if not image_bytes:
        return False, "Image vide."

    try:

        array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            array,
            cv2.IMREAD_GRAYSCALE,
        )

        if image is None:
            return False, "Impossible de lire l'image."

        height, width = image.shape

        if width < 500 or height < 500:
            return False, (
                "Image trop petite. "
                "Prends une photo plus proche de l'exercice."
            )

        # Détection simple du flou avec variance du Laplacien
        blur_score = cv2.Laplacian(
            image,
            cv2.CV_64F,
        ).var()

        if blur_score < 35:
            return False, (
                "L'image semble trop floue. "
                "Reprends une photo plus nette."
            )

        # Contraste
        contrast = image.std()

        if contrast < 20:
            return False, (
                "Le contraste est insuffisant. "
                "Évite une photo trop sombre ou trop claire."
            )

        return True, (
            f"Image valide. "
            f"Résolution : {width}×{height}"
        )

    except Exception as error:

        return False, (
            f"Erreur pendant le contrôle : {error}"
        )


# ============================================================
# PDF → IMAGE
# ============================================================

def pdf_first_page_to_image(pdf_bytes):
    """
    Convertit la première page d'un PDF en image.

    Pour la V1, on analyse la première page.
    """

    try:

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        if len(document) == 0:
            return None

        page = document[0]

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False,
        )

        image_bytes = pixmap.tobytes("png")

        document.close()

        return image_bytes

    except Exception:
        return None


# ============================================================
# PRÉPARATION FICHIER
# ============================================================

def prepare_uploaded_file(uploaded_file):

    if uploaded_file is None:
        return None, None, None

    if not file_size_ok(uploaded_file):

        st.error(
            f"Le fichier dépasse {MAX_IMAGE_SIZE_MB} MB."
        )

        return None, None, None

    original_name = uploaded_file.name.lower()

    if original_name.endswith(".pdf"):

        pdf_bytes = uploaded_file.getvalue()

        image_bytes = pdf_first_page_to_image(
            pdf_bytes
        )

        if image_bytes is None:

            st.error(
                "Impossible de lire ce PDF."
            )

            return None, None, None

        return (
            image_bytes,
            "image/png",
            uploaded_file.name,
        )

    image_bytes = uploaded_file.getvalue()

    mime_type = uploaded_file.type

    if not mime_type:
        mime_type = "image/jpeg"

    return (
        image_bytes,
        mime_type,
        uploaded_file.name,
    )


# ============================================================
# LOCAL STORAGE - PRÉPARATION V1
# ============================================================

def export_history_json():
    data = json.dumps(
        st.session_state.history,
        ensure_ascii=False,
        indent=2,
    )

    return data


def history_download_button():

    if not st.session_state.history:
        return

    data = export_history_json()

    st.download_button(
        label="💾 Exporter mon historique",
        data=data,
        file_name="hintai_history.json",
        mime="application/json",
        use_container_width=True,
    )


# ============================================================
# HEADER
# ============================================================

def render_header():

    col1, col2, col3 = st.columns(
        [2, 5, 2]
    )

    with col1:

        st.markdown(
            "<div class='plan-badge'>"
            f"{st.session_state.plan}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            "<div class='hintai-logo'>🧠 HintAI</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            "<div class='credits-box'>"
            f"⚡ {st.session_state.credits} crédits"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown("## 🧠 HintAI")

        st.caption(
            f"Version {APP_VERSION}"
        )

        st.divider()

        if st.button(
            "🏠 Accueil",
            use_container_width=True,
        ):
            st.session_state.page = "Accueil"
            st.rerun()

        if st.button(
            "🆘 Help Me",
            use_container_width=True,
        ):
            st.session_state.page = "Help Me"
            st.rerun()

        if st.button(
            "🧠 Learn a Concept",
            use_container_width=True,
        ):
            st.session_state.page = "Learn"
            st.rerun()

        if st.button(
            "📚 Historique",
            use_container_width=True,
        ):
            st.session_state.page = "Historique"
            st.rerun()

        if st.button(
            "💎 Pro",
            use_container_width=True,
        ):
            st.session_state.page = "Pro"
            st.rerun()

        st.divider()

        st.markdown(
            f"### ⚡ {st.session_state.credits} crédits"
        )

        if ADS_ENABLED:

            st.markdown(
                """
                <div class="ad-placeholder">
                📺 Emplacement publicité
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "🎁 Simuler une publicité récompensée",
                use_container_width=True,
            ):

                add_credits(
                    REWARDED_AD_CREDIT_REWARD
                )

                st.success(
                    f"+{REWARDED_AD_CREDIT_REWARD} crédits !"
                )

        st.divider()

        st.caption(
            "🔐 Connexion Google : préparée pour la V2"
        )


# ============================================================
# PAGE ACCUEIL
# ============================================================

def page_home():

    st.markdown(
        """
        <div class="hintai-subtitle">
        Ton professeur IA ne te donne pas simplement la réponse.
        Il t'aide à trouver la méthode.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hintai-card">
        <h3>🆘 Help Me</h3>
        <p>
        Bloqué sur un exercice ? Envoie l'énoncé,
        ajoute ton travail si tu en as un,
        puis avance avec des indices progressifs.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 Commencer Help Me",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.page = "Help Me"
        st.rerun()

    st.markdown("")

    st.markdown(
        """
        <div class="hintai-card">
        <h3>🧠 Learn a Concept</h3>
        <p>
        Choisis une notion et ton niveau.
        HintAI t'explique, te fait pratiquer,
        puis vérifie ta compréhension.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "📖 Apprendre une notion",
        use_container_width=True,
    ):

        st.session_state.page = "Learn"
        st.rerun()


# ============================================================
# PAGE HELP ME
# ============================================================

def page_help_me():

    st.title("🆘 Help Me")

    st.caption(
        "Résous ton exercice avec un accompagnement progressif."
    )

    # --------------------------------------------------------
    # ÉTAPE 1
    # --------------------------------------------------------

    st.markdown(
        "<div class='step-box'>"
        "<span class='step-number'>Étape 1</span>"
        "<br>Ajoute ton exercice"
        "</div>",
        unsafe_allow_html=True,
    )

    subject = st.selectbox(
        "Matière",
        SUBJECTS,
        key="help_subject",
    )

    level = st.selectbox(
        "Classe",
        CLASS_LEVELS,
        key="help_level",
    )

    exercise_file = st.file_uploader(
        "📷 Image ou 📄 PDF de l'exercice",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
            "pdf",
        ],
        key="exercise_upload",
    )

    if exercise_file is not None:

        prepared = prepare_uploaded_file(
            exercise_file
        )

        if prepared[0] is not None:

            exercise_bytes = prepared[0]
            exercise_mime = prepared[1]

            st.session_state.exercise_bytes = (
                exercise_bytes
            )

            st.session_state.exercise_mime = (
                exercise_mime
            )

            st.image(
                exercise_bytes,
                caption="Aperçu de l'exercice",
                use_container_width=True,
            )

            # ---------------------------------------------
            # CONTRÔLE QUALITÉ LOCAL
            # ---------------------------------------------

            quality_ok, quality_message = (
                quality_check_image(
                    exercise_bytes
                )
            )

            if quality_ok:

                st.markdown(
                    f"""
                    <div class="quality-success">
                    ✅ Contrôle qualité réussi<br>
                    {quality_message}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="quality-error">
                    ❌ Contrôle qualité échoué<br>
                    {quality_message}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.session_state.exercise_bytes = None

    st.divider()

    # --------------------------------------------------------
    # ÉTAPE 2
    # --------------------------------------------------------

    st.markdown(
        "<div class='step-box'>"
        "<span class='step-number'>Étape 2</span>"
        "<br>Ajoute ton travail"
        "</div>",
        unsafe_allow_html=True,
    )

    student_file = st.file_uploader(
        "📷 Ton travail (optionnel)",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
            "pdf",
        ],
        key="student_upload",
    )

    if student_file is not None:

        prepared = prepare_uploaded_file(
            student_file
        )

        if prepared[0] is not None:

            student_bytes = prepared[0]
            student_mime = prepared[1]

            quality_ok, quality_message = (
                quality_check_image(
                    student_bytes
                )
            )

            if quality_ok:

                st.session_state.student_bytes = (
                    student_bytes
                )

                st.session_state.student_mime = (
                    student_mime
                )

                st.image(
                    student_bytes,
                    caption="Aperçu de ton travail",
                    use_container_width=True,
                )

                st.markdown(
                    f"""
                    <div class="quality-success">
                    ✅ Ton travail est lisible.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="quality-error">
                    ❌ {quality_message}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.session_state.student_bytes = None

    else:

        st.info(
            "Tu peux passer cette étape si tu n'as pas encore essayé."
        )

    st.divider()

    # --------------------------------------------------------
    # LANCEMENT
    # --------------------------------------------------------

    if st.session_state.exercise_bytes is None:

        st.warning(
            "Ajoute d'abord un exercice lisible."
        )

        return

    if not can_spend(HELP_ME_COST):

        st.error(
            f"Il te faut {HELP_ME_COST} crédits "
            f"pour utiliser Help Me."
        )

        st.info(
            "Regarde une publicité récompensée "
            "ou passe à une formule Pro."
        )

        return

    if st.button(
        f"🚀 Lancer Help Me ({HELP_ME_COST} crédits)",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "HintAI analyse ton exercice..."
        ):

            try:

                spend_credits(
                    HELP_ME_COST
                )

                response = help_me_image(
                    exercise_image=(
                        st.session_state.exercise_bytes
                    ),
                    exercise_mime=(
                        st.session_state.exercise_mime
                    ),
                    student_image=(
                        st.session_state.student_bytes
                    ),
                    student_mime=(
                        st.session_state.student_mime
                    ),
                    subject=subject,
                    level=level,
                )

                st.session_state.subject = subject
                st.session_state.level = level

                st.session_state.current_response = (
                    response
                )

                st.session_state.exercise_context = (
                    f"Matière : {subject}\n"
                    f"Niveau : {level}\n"
                    f"Exercice fourni en image."
                )

                st.session_state.hint_level = 1
                st.session_state.help_step = 3

                add_history(
                    "Help Me",
                    response,
                    "help_me",
                )

                st.success(
                    "Indice 1 prêt !"
                )

            except Exception as error:

                st.error(
                    "Une erreur est survenue avec Gemini."
                )

                st.code(
                    str(error)
                )

    # --------------------------------------------------------
    # RÉPONSE
    # --------------------------------------------------------

    if st.session_state.current_response:

        st.divider()

        st.markdown(
            """
            <div class="hint-box">
            <div class="hint-title">
            💡 Indice / accompagnement
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            st.session_state.current_response
        )

        st.divider()

        st.markdown("### Que veux-tu faire ?")

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "💬 Poser une question",
                use_container_width=True,
            ):

                st.session_state.help_action = (
                    "question"
                )

        with col2:

            if st.button(
                "➡️ Indice suivant",
                use_container_width=True,
            ):

                if st.session_state.hint_level < 3:

                    if not can_spend(
                        EXTRA_QUESTION_COST
                    ):

                        st.error(
                            "Pas assez de crédits."
                        )

                    else:

                        spend_credits(
                            EXTRA_QUESTION_COST
                        )

                        with st.spinner(
                            "Préparation de l'indice..."
                        ):

                            try:

                                st.session_state.hint_level += 1

                                response = next_hint(
                                    exercise_context=(
                                        st.session_state.exercise_context
                                    ),
                                    previous_response=(
                                        st.session_state.current_response
                                    ),
                                    hint_level=(
                                        st.session_state.hint_level
                                    ),
                                )

                                st.session_state.current_response = (
                                    response
                                )

                                add_history(
                                    f"Indice {st.session_state.hint_level}",
                                    response,
                                    "hint",
                                )

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    "Erreur Gemini."
                                )

                                st.code(
                                    str(error)
                                )

                else:

                    st.session_state.hint_level = 4

                    with st.spinner(
                        "Préparation de la résolution..."
                    ):

                        try:

                            response = next_hint(
                                exercise_context=(
                                    st.session_state.exercise_context
                                ),
                                previous_response=(
                                    st.session_state.current_response
                                ),
                                hint_level=4,
                            )

                            st.session_state.current_response = (
                                response
                            )

                            add_history(
                                "Résolution complète",
                                response,
                                "solution",
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                "Erreur Gemini."
                            )

                            st.code(
                                str(error)
                            )

        with col3:

            if st.button(
                "✅ Valider",
                use_container_width=True,
            ):

                st.session_state.help_action = (
                    "validate"
                )

        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        if st.session_state.get(
            "help_action"
        ) == "question":

            question = st.text_area(
                "Ta question",
                placeholder=(
                    "Exemple : "
                    "je ne comprends pas pourquoi..."
                ),
            )

            if st.button(
                "Envoyer ma question",
                type="primary",
            ):

                if not can_spend(
                    EXTRA_QUESTION_COST
                ):

                    st.error(
                        "Pas assez de crédits."
                    )

                else:

                    spend_credits(
                        EXTRA_QUESTION_COST
                    )

                    with st.spinner(
                        "HintAI réfléchit..."
                    ):

                        try:

                            answer = (
                                ask_student_question(
                                    st.session_state.exercise_context,
                                    question,
                                )
                            )

                            st.session_state.current_response = (
                                answer
                            )

                            add_history(
                                "Question",
                                answer,
                                "question",
                            )

                            st.session_state.help_action = (
                                None
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                "Erreur Gemini."
                            )

                            st.code(
                                str(error)
                            )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if st.session_state.get(
            "help_action"
        ) == "validate":

            st.markdown(
                "### 🎯 Validation de ta compétence"
            )

            answer = st.text_area(
                "Écris ta réponse ou ta démarche",
                placeholder=(
                    "Écris ici ce que tu as trouvé..."
                ),
            )

            if st.button(
                "🎯 Évaluer ma compétence",
                type="primary",
            ):

                if not answer.strip():

                    st.warning(
                        "Écris d'abord ta démarche."
                    )

                else:

                    with st.spinner(
                        "Évaluation..."
                    ):

                        try:

                            result = validate_skill(
                                exercise_context=(
                                    st.session_state.exercise_context
                                ),
                                student_answer=answer,
                                subject=(
                                    st.session_state.subject
                                ),
                                level=(
                                    st.session_state.level
                                ),
                            )

                            st.markdown(
                                result
                            )

                            add_history(
                                "Validation",
                                result,
                                "validation",
                            )

                        except Exception as error:

                            st.error(
                                "Erreur Gemini."
                            )

                            st.code(
                                str(error)
                            )


# ============================================================
# PAGE LEARN
# ============================================================

def page_learn():

    st.title("🧠 Learn a Concept")

    st.write(
        "Choisis une notion et laisse HintAI "
        "t'accompagner comme un professeur."
    )

    concept = st.text_input(
        "Concept à apprendre",
        placeholder=(
            "Exemple : équations du second degré"
        ),
    )

    subject = st.selectbox(
        "Matière",
        SUBJECTS,
        key="learn_subject",
    )

    level = st.selectbox(
        "Classe",
        CLASS_LEVELS,
        key="learn_level",
    )

    st.markdown(
        """
        <div class="hintai-card">
        📎 Tu pourras ajouter des exercices
        et ton travail dans une évolution future
        de cette V1.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_spend(
        LEARN_CONCEPT_COST
    ):

        st.error(
            "Pas assez de crédits."
        )

        return

    if st.button(
        f"🚀 Commencer ({LEARN_CONCEPT_COST} crédits)",
        type="primary",
        use_container_width=True,
    ):

        if not concept.strip():

            st.warning(
                "Entre d'abord une notion."
            )

            return

        spend_credits(
            LEARN_CONCEPT_COST
        )

        with st.spinner(
            "Préparation du cours..."
        ):

            try:

                response = learn_concept(
                    concept=concept,
                    level=level,
                    subject=subject,
                )

                st.markdown(
                    response
                )

                add_history(
                    concept,
                    response,
                    "learn",
                )

            except Exception as error:

                st.error(
                    "Erreur Gemini."
                )

                st.code(
                    str(error)
                )


# ============================================================
# HISTORIQUE
# ============================================================

def page_history():

    st.title("📚 Mon historique")

    if not st.session_state.history:

        st.info(
            "Ton historique est encore vide."
        )

        return

    history_download_button()

    st.divider()

    for item in st.session_state.history:

        with st.expander(
            f"{item['title']} • {item['date']}"
        ):

            st.caption(
                f"Mode : {item['mode']}"
            )

            st.markdown(
                item["content"]
            )


# ============================================================
# PAGE PRO
# ============================================================

def page_pro():

    st.title("💎 HintAI Pro")

    st.write(
        "Plus de crédits pour apprendre davantage."
    )

    for plan_name, plan_data in PLANS.items():

        if plan_name == "Free":
            continue

        st.markdown(
            f"""
            <div class="pro-card">
                <h3>💎 {plan_name}</h3>
                <div class="pro-price">
                    ${plan_data['price']}
                </div>
                <p>
                    {plan_data['credits']} crédits
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"Choisir {plan_name}",
            key=f"plan_{plan_name}",
            use_container_width=True,
        ):

            st.info(
                "Paiement à connecter dans la prochaine phase."
            )

    st.divider()

    st.markdown(
        """
        ### 🔐 Compte

        Connexion Google prévue pour la version
        avec authentification complète.

        ### 📺 Publicités

        Les utilisateurs Free pourront gagner
        des crédits grâce aux publicités récompensées.
        """,
    )


# ============================================================
# PAGE ERREURS CONFIG
# ============================================================

def config_error_page(errors):

    st.error(
        "⚠️ Configuration HintAI incomplète"
    )

    for error in errors:

        st.warning(error)

    st.info(
        "Vérifie les Secrets Streamlit."
    )


# ============================================================
# ROUTEUR PRINCIPAL
# ============================================================

errors = validate_config()

if errors:

    config_error_page(errors)

else:

    render_header()
    render_sidebar()

    if st.session_state.page == "Accueil":

        page_home()

    elif st.session_state.page == "Help Me":

        page_help_me()

    elif st.session_state.page == "Learn":

        page_learn()

    elif st.session_state.page == "Historique":

        page_history()

    elif st.session_state.page == "Pro":

        page_pro()

    else:

        st.session_state.page = "Accueil"

        page_home()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"HintAI {APP_VERSION} • "
    f"Gemini {GEMINI_MODEL}"
)