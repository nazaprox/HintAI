"""
HintAI — User & Credits
=======================

Gestion des utilisateurs et du système de crédits.

Plans mensuels :
free   = 20 crédits
basic  = 40 crédits
plus   = 80 crédits
pro    = 150 crédits
ultra  = 200 crédits
max    = 300 crédits

Règles :

* Les actions gratuites coûtent 0 crédit.
* Les actions IA consomment des crédits.
* Les uploads consomment 0,5 crédit par upload.
* 10 crédits peuvent être achetés pour 1 USD.
* Les crédits achetés utilisent les mêmes règles de
  consommation que les crédits Free.
* Une publicité simple ne rapporte aucun crédit.
* Une rewarded ad peut rapporter des crédits.
* Série de 3 jours = 6 crédits.
* Série de 6 jours = 12 crédits.
* Une journée de série ne compte que si l'utilisateur
  réalise réellement une action.

Ce fichier ne communique pas directement avec Gemini.
"""

from **future** import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Optional

import storage

# ============================================================

# PLANS

# ============================================================

PLAN_CREDITS = {
"free": 20,
"basic": 40,
"plus": 80,
"pro": 150,
"ultra": 200,
"max": 300,
}

# ============================================================

# COÛTS DES ACTIONS

# ============================================================

CREDIT_COSTS = {

```
# --------------------------------------------------------
# GRATUIT
# --------------------------------------------------------

"open_help_me": 0,
"text_input": 0,
"camera": 0,
"opencv_quality": 0,
"local_crop": 0,
"local_enhancement": 0,

"open_learn_concept": 0,

"local_history": 0,
"authentication": 0,
"view_history": 0,
"display_cached_response": 0,

# --------------------------------------------------------
# UPLOADS
# --------------------------------------------------------

"upload_image": 0.5,
"upload_pdf": 0.5,

# --------------------------------------------------------
# HELP ME
# --------------------------------------------------------

"help_me_analysis": 2,

"hint_1": 1,
"hint_2": 1,
"hint_3": 1,

"help_me_question": 1,

"help_me_solution": 2,

"evaluation_exercise": 1,
"evaluation_correction": 1,
"evaluation_question": 1,
"evaluation_hint": 1,

# --------------------------------------------------------
# LEARN A CONCEPT
# --------------------------------------------------------

"concept_explanation": 2,

"concept_question": 1,
"concept_hint": 1,

"easy_exercise": 1,
"difficult_exercise": 2,

"concept_correction": 1,
"new_explanation": 1,

# --------------------------------------------------------
# DOCUMENT
# --------------------------------------------------------

"document_analysis": 1,
```

}

# ============================================================

# REWARDED ADS

# ============================================================

REWARDED_AD_DURATION_SECONDS = 15

REWARDED_AD_REWARD = 1

# ============================================================

# PUBLICITÉ SIMPLE

# ============================================================

SIMPLE_AD_DURATION_SECONDS = 5

SIMPLE_AD_REWARD = 0

# ============================================================

# ACHAT DE CRÉDITS

# ============================================================

CREDITS_PER_USD = 10

CREDIT_PACK_USD = 1

CREDIT_PACK_AMOUNT = 10

# ============================================================

# SÉRIES

# ============================================================

STREAK_3_DAYS = 6
STREAK_6_DAYS = 12

# ============================================================

# UTILITAIRES

# ============================================================

def utc_today() -> date:
"""
Date UTC actuelle.
"""

```
return datetime.now(
    timezone.utc
).date()
```

def normalize_plan(
plan: Optional[str],
) -> str:
"""
Normalise le nom d'un plan.
"""

```
value = (
    str(plan or "free")
    .strip()
    .lower()
)

if value not in PLAN_CREDITS:
    return "free"

return value
```

def action_cost(
action: str,
) -> float:
"""
Retourne le coût d'une action.
"""

```
if action not in CREDIT_COSTS:
    raise ValueError(
        f"Action de crédit inconnue : {action}"
    )

return float(
    CREDIT_COSTS[action]
)
```

# ============================================================

# CRÉATION UTILISATEUR

# ============================================================

def create_user(
*,
user_id: Optional[str] = None,
email: Optional[str] = None,
plan: str = "free",
) -> Dict[str, Any]:
"""
Crée un utilisateur avec son allocation mensuelle.
"""

```
plan = normalize_plan(
    plan
)

user = storage.create_user(
    user_id=user_id,
    email=email,
    plan=plan,
)

user["credits"] = float(
    PLAN_CREDITS[plan]
)

user[
    "monthlyCredits"
] = float(
    PLAN_CREDITS[plan]
)

user[
    "creditsResetAt"
] = next_month_date().isoformat()

user[
    "streak"
] = 0

user[
    "lastActionDate"
] = None

user[
    "streakReward3"
] = False

user[
    "streakReward6"
] = False

return storage.update_user(
    user["id"],
    user,
) or user
```

# ============================================================

# MOIS SUIVANT

# ============================================================

def next_month_date() -> date:
"""
Retourne le premier jour du mois suivant.
"""

```
today = utc_today()

if today.month == 12:
    return date(
        today.year + 1,
        1,
        1,
    )

return date(
    today.year,
    today.month + 1,
    1,
)
```

# ============================================================

# RÉINITIALISATION MENSUELLE

# ============================================================

def ensure_monthly_credits(
user: Dict[str, Any],
) -> Dict[str, Any]:
"""
Vérifie si les crédits mensuels doivent être réinitialisés.
"""

```
reset_value = user.get(
    "creditsResetAt"
)

if not reset_value:
    return user

try:
    reset_date = date.fromisoformat(
        str(reset_value)
    )

except ValueError:
    reset_date = utc_today()

if utc_today() < reset_date:
    return user

plan = normalize_plan(
    user.get("plan")
)

monthly = float(
    PLAN_CREDITS[plan]
)

user[
    "credits"
] = monthly

user[
    "monthlyCredits"
] = monthly

user[
    "creditsResetAt"
] = next_month_date().isoformat()

updated = storage.update_user(
    user["id"],
    user,
)

return updated or user
```

# ============================================================

# RÉCUPÉRATION UTILISATEUR

# ============================================================

def get_user(
user_id: str,
) -> Optional[Dict[str, Any]]:
"""
Récupère un utilisateur et vérifie son reset mensuel.
"""

```
user = storage.get_user(
    user_id
)

if user is None:
    return None

return ensure_monthly_credits(
    user
)
```

# ============================================================

# SOLDE

# ============================================================

def get_balance(
user_id: str,
) -> float:
"""
Retourne le nombre de crédits disponibles.
"""

```
user = get_user(
    user_id
)

if user is None:
    raise ValueError(
        "Utilisateur introuvable."
    )

return float(
    user.get(
        "credits",
        0,
    )
)
```

# ============================================================

# AJOUT DE CRÉDITS

# ============================================================

def add_credits(
user_id: str,
amount: float,
*,
transaction_type: str,
action: str,
metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
"""
Ajoute des crédits au compte.

```
amount doit être positif.
"""

amount = float(
    amount
)

if amount <= 0:
    raise ValueError(
        "Le nombre de crédits à ajouter doit être positif."
    )

user = get_user(
    user_id
)

if user is None:
    raise ValueError(
        "Utilisateur introuvable."
    )

balance = float(
    user.get(
        "credits",
        0,
    )
)

new_balance = (
    balance + amount
)

updated = storage.update_user(
    user_id,
    {
        "credits": new_balance,
    },
)

storage.save_credit_transaction(
    user_id=user_id,
    amount=amount,
    transaction_type=transaction_type,
    action=action,
    balance_after=new_balance,
    metadata=metadata,
)

return updated or {
    **user,
    "credits": new_balance,
}
```

# ============================================================

# DÉPENSE DE CRÉDITS

# ============================================================

def spend_credits(
user_id: str,
action: str,
*,
metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
"""
Dépense les crédits nécessaires à une action.

```
L'opération est refusée si le solde est insuffisant.
"""

cost = action_cost(
    action
)

user = get_user(
    user_id
)

if user is None:
    raise ValueError(
        "Utilisateur introuvable."
    )

balance = float(
    user.get(
        "credits",
        0,
    )
)

if cost == 0:
    return {
        **user,
        "credits": balance,
        "spent": 0,
        "action": action,
    }

if balance < cost:
    raise ValueError(
        "Crédits insuffisants."
    )

new_balance = (
    balance - cost
)

updated = storage.update_user(
    user_id,
    {
        "credits": new_balance,
    },
)

storage.save_credit_transaction(
    user_id=user_id,
    amount=-cost,
    transaction_type="spend",
    action=action,
    balance_after=new_balance,
    metadata=metadata,
)

return {
    **(
        updated
        or user
    ),
    "credits": new_balance,
    "spent": cost,
    "action": action,
}
```

# ============================================================

# UPLOAD

# ============================================================

def spend_upload(
user_id: str,
*,
file_type: str,
) -> Dict[str, Any]:
"""
Dépense le crédit correspondant à un upload.
"""

```
file_type = (
    file_type
    .strip()
    .lower()
)

if file_type in {
    "image",
    "jpg",
    "jpeg",
    "png",
    "webp",
}:
    action = "upload_image"

elif file_type == "pdf":
    action = "upload_pdf"

else:
    raise ValueError(
        "Type de fichier non supporté."
    )

return spend_credits(
    user_id,
    action,
)
```

# ============================================================

# ACHAT DE CRÉDITS

# ============================================================

def purchase_credit_pack(
user_id: str,
) -> Dict[str, Any]:
"""
Ajoute un pack de 10 crédits.

```
Le paiement réel doit être validé par le système
de paiement avant l'appel de cette fonction.

1 USD = 10 crédits.
"""

return add_credits(
    user_id,
    CREDIT_PACK_AMOUNT,
    transaction_type="purchase",
    action="credit_pack_10",
    metadata={
        "priceUsd": CREDIT_PACK_USD,
        "credits": CREDIT_PACK_AMOUNT,
    },
)
```

# ============================================================

# PUBLICITÉ SIMPLE

# ============================================================

def simple_ad_completed() -> Dict[str, Any]:
"""
Une publicité simple ne donne aucun crédit.
"""

```
return {
    "durationSeconds":
        SIMPLE_AD_DURATION_SECONDS,
    "reward": SIMPLE_AD_REWARD,
}
```

# ============================================================

# REWARDED AD

# ============================================================

def reward_ad(
user_id: str,
ad_id: str,
) -> Dict[str, Any]:
"""
Attribue une récompense après une rewarded ad validée.

```
Protection contre le double crédit du même ad_id.
"""

if not ad_id.strip():
    raise ValueError(
        "ad_id est requis."
    )

if storage.rewarded_ad_exists(
    ad_id
):
    raise ValueError(
        "Cette publicité a déjà été récompensée."
    )

storage.save_rewarded_ad(
    user_id=user_id,
    ad_id=ad_id,
    reward=REWARDED_AD_REWARD,
)

return add_credits(
    user_id,
    REWARDED_AD_REWARD,
    transaction_type="reward",
    action="rewarded_ad",
    metadata={
        "adId": ad_id,
        "durationSeconds":
            REWARDED_AD_DURATION_SECONDS,
    },
)
```

# ============================================================

# SÉRIES

# ============================================================

def register_real_action(
user_id: str,
) -> Dict[str, Any]:
"""
Enregistre une vraie action utilisateur.

```
Une simple ouverture d'écran ne doit pas appeler cette
fonction.

Une action réelle peut être par exemple :
- analyse d'un exercice ;
- demande d'un indice ;
- question ;
- correction ;
- exercice ;
- Learn a Concept.
"""

user = get_user(
    user_id
)

if user is None:
    raise ValueError(
        "Utilisateur introuvable."
    )

today = utc_today()

last_value = user.get(
    "lastActionDate"
)

if last_value:
    try:
        last_date = date.fromisoformat(
            str(last_value)
        )
    except ValueError:
        last_date = None
else:
    last_date = None

current_streak = int(
    user.get(
        "streak",
        0,
    )
)

if last_date == today:
    return {
        **user,
        "streak": current_streak,
        "streakUpdated": False,
    }

if (
    last_date is not None
    and today == last_date + timedelta(days=1)
):
    current_streak += 1

else:
    current_streak = 1

user_updates = {
    "streak": current_streak,
    "lastActionDate": today.isoformat(),
}

updated = storage.update_user(
    user_id,
    user_updates,
)

user = updated or {
    **user,
    **user_updates,
}

reward = 0

# --------------------------------------------------------
# JOUR 3
# --------------------------------------------------------

if (
    current_streak >= 3
    and not user.get(
        "streakReward3",
        False,
    )
):

    add_credits(
        user_id,
        STREAK_3_DAYS,
        transaction_type="streak_reward",
        action="streak_3_days",
        metadata={
            "streak": current_streak,
        },
    )

    storage.update_user(
        user_id,
        {
            "streakReward3": True,
        },
    )

    reward += STREAK_3_DAYS

# --------------------------------------------------------
# JOUR 6
# --------------------------------------------------------

if (
    current_streak >= 6
    and not user.get(
        "streakReward6",
        False,
    )
):

    add_credits(
        user_id,
        STREAK_6_DAYS,
        transaction_type="streak_reward",
        action="streak_6_days",
        metadata={
            "streak": current_streak,
        },
    )

    storage.update_user(
        user_id,
        {
            "streakReward6": True,
        },
    )

    reward += STREAK_6_DAYS

final_user = get_user(
    user_id
)

return {
    **(
        final_user
        or user
    ),
    "streakUpdated": True,
    "streakReward": reward,
}
```

# ============================================================

# RÉSUMÉ DU COMPTE

# ============================================================

def account_summary(
user_id: str,
) -> Dict[str, Any]:
"""
Retourne les informations nécessaires au frontend.
"""

```
user = get_user(
    user_id
)

if user is None:
    raise ValueError(
        "Utilisateur introuvable."
    )

plan = normalize_plan(
    user.get("plan")
)

return {
    "userId": user_id,
    "plan": plan,
    "credits": float(
        user.get(
            "credits",
            0,
        )
    ),
    "monthlyCredits": float(
        PLAN_CREDITS[plan]
    ),
    "creditsResetAt":
        user.get(
            "creditsResetAt"
        ),
    "streak": int(
        user.get(
            "streak",
            0,
        )
    ),
    "rewardedAd": {
        "durationSeconds":
            REWARDED_AD_DURATION_SECONDS,
        "reward":
            REWARDED_AD_REWARD,
    },
    "simpleAd": {
        "durationSeconds":
            SIMPLE_AD_DURATION_SECONDS,
        "reward":
            SIMPLE_AD_REWARD,
    },
}
```

# ============================================================

# INFORMATIONS SYSTÈME

# ============================================================

def credit_system() -> Dict[str, Any]:
"""
Retourne la configuration publique du système de crédits.
"""

```
return {
    "plans": PLAN_CREDITS,
    "costs": CREDIT_COSTS,
    "creditPack": {
        "credits": CREDIT_PACK_AMOUNT,
        "priceUsd": CREDIT_PACK_USD,
    },
    "ads": {
        "simple": {
            "durationSeconds":
                SIMPLE_AD_DURATION_SECONDS,
            "reward":
                SIMPLE_AD_REWARD,
        },
        "rewarded": {
            "durationSeconds":
                REWARDED_AD_DURATION_SECONDS,
            "reward":
                REWARDED_AD_REWARD,
        },
    },
    "streaks": {
        "3Days": STREAK_3_DAYS,
        "6Days": STREAK_6_DAYS,
    },
}
```

"""
FIN user.py
"""
