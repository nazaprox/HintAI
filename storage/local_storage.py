
import os
import json


HISTORY_DIR = "HintAI/storage/history"


os.makedirs(
    HISTORY_DIR,
    exist_ok=True
)


# ==========================================
# SAUVEGARDER UNE SESSION
# ==========================================

def save_session(session):

    data = session.to_dict()

    session_id = data[
        "session_id"
    ]

    file_path = os.path.join(
        HISTORY_DIR,
        f"{session_id}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    return file_path


# ==========================================
# CHARGER UNE SESSION
# ==========================================

def load_session(
    session_id
):

    file_path = os.path.join(
        HISTORY_DIR,
        f"{session_id}.json"
    )

    if not os.path.exists(
        file_path
    ):

        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================================
# HISTORIQUE
# ==========================================

def list_sessions():

    sessions = []

    if not os.path.exists(
        HISTORY_DIR
    ):

        return sessions

    for filename in os.listdir(
        HISTORY_DIR
    ):

        if not filename.endswith(
            ".json"
        ):

            continue

        file_path = os.path.join(
            HISTORY_DIR,
            filename
        )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            sessions.append(
                data
            )

        except Exception:

            continue

    sessions.sort(
        key=lambda x:
        x.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return sessions


# ==========================================
# SUPPRIMER UNE SESSION
# ==========================================

def delete_session(
    session_id
):

    file_path = os.path.join(
        HISTORY_DIR,
        f"{session_id}.json"
    )

    if os.path.exists(
        file_path
    ):

        os.remove(
            file_path
        )

        return True

    return False


# ==========================================
# TOUT SUPPRIMER
# ==========================================

def clear_history():

    if not os.path.exists(
        HISTORY_DIR
    ):

        return

    for filename in os.listdir(
        HISTORY_DIR
    ):

        if filename.endswith(
            ".json"
        ):

            os.remove(
                os.path.join(
                    HISTORY_DIR,
                    filename
                )
            )
