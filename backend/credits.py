```python
"""
HintAI — Credits & Usage
========================

Gestion des crédits et limites d'utilisation de HintAI.

Plans :
    free
    basic
    pro
    proplus
    super
    heavy

Principes :
- les crédits sont consommés côté serveur
- le frontend ne décide jamais combien de crédits
  l'utilisateur possède
- les rewarded ads peuvent donner un crédit bonus
- les limites mensuelles sont vérifiées côté backend
- protection basique contre les abus
- les opérations critiques sont conçues pour être
  compatibles avec un stockage atomique dans storage.py

IMPORTANT :
Ce fichier ne gère PAS :
- authentification
- Gemini
- paiement
- stockage permanent
- contrôle qualité

Il contient uniquement les règles métier des crédits.
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


# ============================================================
# PLANS
# ============================================================

@dataclass(frozen=True)
class Plan:
    """
    Configuration d'un abonnement.
    """

    id: str

    name: str

    monthly_price: float

    monthly_credits: int

    help_me_limit: int

    learn_concept_limit: int

    rewarded_ads: bool

    ads_enabled: bool

    priority: int


PLANS: Dict[str, Plan] = {

    "free": Plan(
        id="free",
        name="Free",
        monthly_price=0.0,
        monthly_credits=2,
        help_me_limit=1,
        learn_concept_limit=2,
        rewarded_ads=True,
        ads_enabled=True,
        priority=0,
    ),

    "basic": Plan(
        id="basic",
        name="Basic",
        monthly_price=5.0,
        monthly_credits=20,
        help_me_limit=20,
        learn_concept_limit=10,
        rewarded_ads=True,
        ads_enabled=True,
        priority=1,
    ),

    "pro": Plan(
        id="pro",
        name="Pro",
        monthly_price=10.0,
        monthly_credits=60,
        help_me_limit=60,
        learn_concept_limit=30,
        rewarded_ads=True,
        ads_enabled=True,
        priority=2,
    ),

    "proplus": Plan(
        id="proplus",
        name="ProPlus",
        monthly_price=15.0,
        monthly_credits=100,
        help_me_limit=100,
        learn_concept_limit=50,
        rewarded_ads=True,
        ads_enabled=True,
        priority=3,
    ),

    "super": Plan(
        id="super",
        name="Super",
        monthly_price=20.0,
        monthly_credits=160,
        help_me_limit=160,
        learn_concept_limit=80,
        rewarded_ads=True,
        ads_enabled=True,
        priority=4,
    ),

    "heavy": Plan(
        id="heavy",
        name="Heavy",
        monthly_price=30.0,
        monthly_credits=300,
        help_me_limit=300,
        learn_concept_limit=150,
        rewarded_ads=True,
        ads_enabled=True,
        priority=5,
    ),
}


# ============================================================
# CONFIGURATION
# ============================================================

FREE_MONTHLY_HELP_ME = 1

FREE_MONTHLY_LEARN_CONCEPT = 2

REWARDED_AD_CREDIT_AMOUNT = 1

MAX_REWARDED_AD_CREDITS_PER_DAY = int(
    os.getenv(
        "HINTAI_MAX_REWARDED_ADS_PER_DAY",
        "3",
    )
)

MAX_BONUS_CREDITS = int(
    os.getenv(
        "HINTAI_MAX_BONUS_CREDITS",
        "10",
    )
)

# Délai minimal entre deux validations de rewarded ads.
REWARDED_AD_COOLDOWN_SECONDS = int(
    os.getenv(
        "HINTAI_REWARDED_AD_COOLDOWN",
        "30",
    )
)


# ============================================================
# TYPES D'UTILISATION
# ============================================================

USAGE_HELP_ME = "help_me"

USAGE_LEARN_CONCEPT = "learn_concept"

USAGE_SOLUTION = "solution"

USAGE_QUESTION = "question"

USAGE_VERIFICATION = "verification"


VALID_USAGE_TYPES = {
    USAGE_HELP_ME,
    USAGE_LEARN_CONCEPT,
    USAGE_SOLUTION,
    USAGE_QUESTION,
    USAGE_VERIFICATION,
}


# ============================================================
# OUTILS
# ============================================================

def get_plan(
    plan_id: Optional[str],
) -> Plan:
    """
    Retourne la configuration d'un plan.

    Tout plan inconnu retombe sur Free.
    """

    if not plan_id:
        return PLANS["free"]

    return PLANS.get(
        plan_id.lower(),
        PLANS["free"],
    )


def get_plan_data(
    plan_id: Optional[str],
) -> Dict[str, Any]:
    """
    Version JSON du plan pour l'API.
    """

    plan = get_plan(
        plan_id
    )

    return {
        "id": plan.id,
        "name": plan.name,
        "monthlyPrice": plan.monthly_price,
        "monthlyCredits":
            plan.monthly_credits,
        "helpMeLimit":
            plan.help_me_limit,
        "learnConceptLimit":
            plan.learn_concept_limit,
        "rewardedAds":
            plan.rewarded_ads,
        "adsEnabled":
            plan.ads_enabled,
    }


def month_key(
    timestamp: Optional[int] = None,
) -> str:
    """
    Retourne la période mensuelle UTC.

    Exemple :
        2026-08
    """

    timestamp = (
        timestamp
        if timestamp is not None
        else int(time.time())
    )

    current = time.gmtime(
        timestamp
    )

    return (
        f"{current.tm_year:04d}-"
        f"{current.tm_mon:02d}"
    )


def day_key(
    timestamp: Optional[int] = None,
) -> str:
    """
    Retourne la journée UTC.
    """

    timestamp = (
        timestamp
        if timestamp is not None
        else int(time.time())
    )

    current = time.gmtime(
        timestamp
    )

    return (
        f"{current.tm_year:04d}-"
        f"{current.tm_mon:02d}-"
        f"{current.tm_mday:02d}"
    )


# ============================================================
# STRUCTURE DU COMPTE CRÉDIT
# ============================================================

def create_credit_account(
    user_id: str,
    plan_id: str = "free",
) -> Dict[str, Any]:
    """
    Crée la structure initiale du compte de crédits.

    Le stockage permanent sera effectué dans storage.py.
    """

    plan = get_plan(
        plan_id
    )

    return {
        "userId": user_id,

        "plan": plan.id,

        "period": month_key(),

        "monthlyCredits":
            plan.monthly_credits,

        "usedCredits": 0,

        "bonusCredits": 0,

        "helpMeUsed": 0,

        "learnConceptUsed": 0,

        "rewardedAdsToday": 0,

        "rewardedAdsDay":
            day_key(),

        "lastRewardedAdAt": None,

        "createdAt":
            int(time.time()),

        "updatedAt":
            int(time.time()),
    }


def reset_period_if_needed(
    account: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Réinitialise les compteurs mensuels lorsque le mois change.

    Cette fonction ne doit pas être utilisée seule pour
    une opération critique : storage.py devra effectuer
    la modification de façon atomique.
    """

    current_period = month_key()

    if account.get(
        "period"
    ) != current_period:

        plan = get_plan(
            account.get(
                "plan",
                "free",
            )
        )

        account[
            "period"
        ] = current_period

        account[
            "monthlyCredits"
        ] = plan.monthly_credits

        account[
            "usedCredits"
        ] = 0

        account[
            "helpMeUsed"
        ] = 0

        account[
            "learnConceptUsed"
        ] = 0

    current_day = day_key()

    if account.get(
        "rewardedAdsDay"
    ) != current_day:

        account[
            "rewardedAdsDay"
        ] = current_day

        account[
            "rewardedAdsToday"
        ] = 0

    account[
        "updatedAt"
    ] = int(
        time.time()
    )

    return account


# ============================================================
# CRÉDITS DISPONIBLES
# ============================================================

def get_available_credits(
    account: Dict[str, Any],
) -> int:
    """
    Retourne le nombre de crédits utilisables.

    Crédits mensuels restants
    +
    crédits bonus.
    """

    account = reset_period_if_needed(
        account
    )

    monthly_remaining = max(
        0,
        int(
            account.get(
                "monthlyCredits",
                0,
            )
        )
        - int(
            account.get(
                "usedCredits",
                0,
            )
        ),
    )

    bonus = max(
        0,
        int(
            account.get(
                "bonusCredits",
                0,
            )
        ),
    )

    return (
        monthly_remaining
        + bonus
    )


# ============================================================
# LIMITES PAR FONCTIONNALITÉ
# ============================================================

def get_usage_limit(
    account: Dict[str, Any],
    usage_type: str,
) -> Optional[int]:
    """
    Retourne la limite mensuelle correspondant
    à une fonctionnalité.

    None signifie qu'il n'y a pas de limite spécifique
    autre que les crédits.
    """

    if usage_type not in VALID_USAGE_TYPES:
        raise ValueError(
            "Type d'utilisation invalide."
        )

    plan = get_plan(
        account.get(
            "plan",
            "free",
        )
    )

    if usage_type == USAGE_HELP_ME:
        return plan.help_me_limit

    if usage_type == USAGE_LEARN_CONCEPT:
        return plan.learn_concept_limit

    return None


def get_usage_count(
    account: Dict[str, Any],
    usage_type: str,
) -> int:
    """
    Retourne le nombre d'utilisations dans la période.
    """

    if usage_type == USAGE_HELP_ME:
        return int(
            account.get(
                "helpMeUsed",
                0,
            )
        )

    if usage_type == USAGE_LEARN_CONCEPT:
        return int(
            account.get(
                "learnConceptUsed",
                0,
            )
        )

    return 0


def has_usage_remaining(
    account: Dict[str, Any],
    usage_type: str,
) -> bool:
    """
    Vérifie si l'utilisateur peut encore utiliser
    une fonctionnalité selon sa limite mensuelle.
    """

    account = reset_period_if_needed(
        account
    )

    limit = get_usage_limit(
        account,
        usage_type,
    )

    if limit is None:
        return True

    count = get_usage_count(
        account,
        usage_type,
    )

    return count < limit


# ============================================================
# CONSOMMATION
# ============================================================

def can_consume_credit(
    account: Dict[str, Any],
    usage_type: str,
    amount: int = 1,
) -> bool:
    """
    Vérifie si une opération peut être effectuée.
    """

    if amount <= 0:
        return False

    if usage_type not in VALID_USAGE_TYPES:
        return False

    account = reset_period_if_needed(
        account
    )

    if not has_usage_remaining(
        account,
        usage_type,
    ):
        return False

    return (
        get_available_credits(
            account
        )
        >= amount
    )


def consume_credit(
    account: Dict[str, Any],
    usage_type: str,
    amount: int = 1,
) -> Dict[str, Any]:
    """
    Consomme un ou plusieurs crédits.

    IMPORTANT :
    Cette fonction modifie uniquement la structure mémoire.

    storage.py devra effectuer l'opération de façon atomique
    afin d'empêcher deux requêtes simultanées de dépenser
    le même crédit.
    """

    if not can_consume_credit(
        account,
        usage_type,
        amount,
    ):
        raise RuntimeError(
            "Crédits insuffisants ou limite atteinte."
        )

    account = reset_period_if_needed(
        account
    )

    monthly_remaining = max(
        0,
        int(
            account.get(
                "monthlyCredits",
                0,
            )
        )
        - int(
            account.get(
                "usedCredits",
                0,
            )
        ),
    )

    remaining_amount = amount

    # --------------------------------------------------------
    # On utilise d'abord les crédits mensuels.
    # --------------------------------------------------------

    monthly_used = min(
        monthly_remaining,
        remaining_amount,
    )

    account[
        "usedCredits"
    ] = (
        int(
            account.get(
                "usedCredits",
                0,
            )
        )
        + monthly_used
    )

    remaining_amount -= (
        monthly_used
    )

    # --------------------------------------------------------
    # Puis les crédits bonus.
    # --------------------------------------------------------

    if remaining_amount > 0:

        bonus = int(
            account.get(
                "bonusCredits",
                0,
            )
        )

        if bonus < remaining_amount:
            raise RuntimeError(
                "Crédits bonus insuffisants."
            )

        account[
            "bonusCredits"
        ] = (
            bonus
            - remaining_amount
        )

    # --------------------------------------------------------
    # Compteur spécifique.
    # --------------------------------------------------------

    if usage_type == USAGE_HELP_ME:

        account[
            "helpMeUsed"
        ] = (
            int(
                account.get(
                    "helpMeUsed",
                    0,
                )
            )
            + 1
        )

    elif usage_type == USAGE_LEARN_CONCEPT:

        account[
            "learnConceptUsed"
        ] = (
            int(
                account.get(
                    "learnConceptUsed",
                    0,
                )
            )
            + 1
        )

    account[
        "updatedAt"
    ] = int(
        time.time()
    )

    return account


# ============================================================
# REWARDED ADS
# ============================================================

def can_watch_rewarded_ad(
    account: Dict[str, Any],
) -> bool:
    """
    Vérifie si l'utilisateur peut recevoir une récompense
    après une publicité récompensée.
    """

    account = reset_period_if_needed(
        account
    )

    plan = get_plan(
        account.get(
            "plan",
            "free",
        )
    )

    if not plan.rewarded_ads:
        return False

    ads_today = int(
        account.get(
            "rewardedAdsToday",
            0,
        )
    )

    if (
        ads_today
        >= MAX_REWARDED_AD_CREDITS_PER_DAY
    ):
        return False

    last_ad = account.get(
        "lastRewardedAdAt"
    )

    if last_ad is not None:

        elapsed = (
            int(time.time())
            - int(last_ad)
        )

        if (
            elapsed
            < REWARDED_AD_COOLDOWN_SECONDS
        ):
            return False

    bonus = int(
        account.get(
            "bonusCredits",
            0,
        )
    )

    if bonus >= MAX_BONUS_CREDITS:
        return False

    return True


def reward_rewarded_ad(
    account: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ajoute un crédit après une rewarded ad validée.

    ATTENTION :

    Le frontend ne doit jamais pouvoir appeler cette fonction
    en disant simplement :

        "j'ai regardé une publicité".

    Une vraie validation du reward publicitaire devra être
    effectuée côté serveur avec le fournisseur publicitaire.
    """

    if not can_watch_rewarded_ad(
        account
    ):
        raise RuntimeError(
            "Rewarded ad non disponible."
        )

    account = reset_period_if_needed(
        account
    )

    account[
        "bonusCredits"
    ] = (
        int(
            account.get(
                "bonusCredits",
                0,
            )
        )
        + REWARDED_AD_CREDIT_AMOUNT
    )

    account[
        "rewardedAdsToday"
    ] = (
        int(
            account.get(
                "rewardedAdsToday",
                0,
            )
        )
        + 1
    )

    account[
        "lastRewardedAdAt"
    ] = int(
        time.time()
    )

    account[
        "updatedAt"
    ] = int(
        time.time()
    )

    return account


# ============================================================
# ANTI-ABUS
# ============================================================

def build_usage_fingerprint(
    user_id: str,
    usage_type: str,
    timestamp: Optional[int] = None,
) -> str:
    """
    Crée une empreinte temporelle permettant au stockage
    de détecter des utilisations anormalement rapprochées.
    """

    timestamp = (
        timestamp
        if timestamp is not None
        else int(time.time())
    )

    # Fenêtre de 60 secondes.
    window = (
        timestamp // 60
    )

    raw = (
        f"{user_id}:"
        f"{usage_type}:"
        f"{window}"
    )

    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


def is_suspicious_usage(
    recent_operations: int,
    *,
    maximum_operations: int = 10,
) -> bool:
    """
    Détection très basique d'activité anormale.

    Le système complet sera effectué avec storage.py
    et éventuellement un rate limiter externe.
    """

    return (
        recent_operations
        > maximum_operations
    )


def get_rate_limit(
    plan_id: str,
) -> int:
    """
    Nombre maximal approximatif de requêtes IA
    par fenêtre courte.

    Ce n'est pas une limite mensuelle.
    """

    limits = {
        "free": 3,
        "basic": 8,
        "pro": 15,
        "proplus": 20,
        "super": 30,
        "heavy": 45,
    }

    return limits.get(
        plan_id,
        limits["free"],
    )


# ============================================================
# RÉSUMÉ COMPTE
# ============================================================

def get_credit_summary(
    account: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Retourne les informations nécessaires au frontend.
    """

    account = reset_period_if_needed(
        account
    )

    plan = get_plan(
        account.get(
            "plan",
            "free",
        )
    )

    monthly_remaining = max(
        0,
        int(
            account.get(
                "monthlyCredits",
                0,
            )
        )
        - int(
            account.get(
                "usedCredits",
                0,
            )
        ),
    )

    bonus = max(
        0,
        int(
            account.get(
                "bonusCredits",
                0,
            )
        ),
    )

    return {
        "plan": plan.id,

        "planName": plan.name,

        "monthlyPrice":
            plan.monthly_price,

        "monthlyCredits":
            plan.monthly_credits,

        "monthlyRemaining":
            monthly_remaining,

        "bonusCredits":
            bonus,

        "availableCredits":
            monthly_remaining + bonus,

        "helpMeUsed":
            int(
                account.get(
                    "helpMeUsed",
                    0,
                )
            ),

        "helpMeLimit":
            plan.help_me_limit,

        "learnConceptUsed":
            int(
                account.get(
                    "learnConceptUsed",
                    0,
                )
            ),

        "learnConceptLimit":
            plan.learn_concept_limit,

        "rewardedAdsToday":
            int(
                account.get(
                    "rewardedAdsToday",
                    0,
                )
            ),

        "rewardedAdsRemaining":
            max(
                0,
                MAX_REWARDED_AD_CREDITS_PER_DAY
                - int(
                    account.get(
                        "rewardedAdsToday",
                        0,
                    )
                ),
            ),

        "adsEnabled":
            plan.ads_enabled,
    }


# ============================================================
# PLANS POUR LE FRONTEND
# ============================================================

def get_all_plans() -> list[Dict[str, Any]]:
    """
    Retourne tous les plans sous forme JSON.
    """

    return [
        get_plan_data(
            plan_id
        )
        for plan_id in PLANS
    ]


# ============================================================
# COÛTS DES OPÉRATIONS
# ============================================================

def get_operation_cost(
    operation: str,
) -> int:
    """
    Coût de base d'une opération.

    On pourra plus tard adapter le coût selon :
    - longueur du prompt
    - image
    - PDF
    - modèle utilisé
    - contexte
    - mode direct
    """

    costs = {

        # Une session Help Me.
        USAGE_HELP_ME: 1,

        # Une séquence Learn a Concept.
        USAGE_LEARN_CONCEPT: 1,

        # Résolution complète.
        USAGE_SOLUTION: 1,

        # Question pendant une session.
        USAGE_QUESTION: 1,

        # Vérification de travail.
        USAGE_VERIFICATION: 1,
    }

    if operation not in costs:
        raise ValueError(
            "Opération inconnue."
        )

    return costs[
        operation
    ]


# ============================================================
# POLITIQUE DE CONSOMMATION
# ============================================================

def should_charge_operation(
    operation: str,
) -> bool:
    """
    Détermine si une opération consomme un crédit.

    Cette fonction est volontairement séparée pour pouvoir
    faire évoluer facilement le modèle économique.

    Exemple futur :

        indice 1 → inclus dans Help Me
        indice 2 → inclus
        indice 3 → inclus
        question → coût supplémentaire éventuel
        solution → coût supplémentaire éventuel
    """

    return operation in {
        USAGE_HELP_ME,
        USAGE_LEARN_CONCEPT,
        USAGE_SOLUTION,
        USAGE_QUESTION,
        USAGE_VERIFICATION,
    }


# ============================================================
# FREE PLAN — RÈGLES INITIALES
# ============================================================

def get_free_plan_rules() -> Dict[str, Any]:
    """
    Règles spécifiques au Free.

    Elles correspondent à la stratégie définie pour HintAI :
    utilisation limitée + publicité + rewarded ads.
    """

    return {
        "monthlyHelpMe":
            FREE_MONTHLY_HELP_ME,

        "monthlyLearnConcept":
            FREE_MONTHLY_LEARN_CONCEPT,

        "adsBetweenHints":
            True,

        "adsBetweenQuestions":
            True,

        "rewardedAds":
            True,

        "rewardedAdCredits":
            REWARDED_AD_CREDIT_AMOUNT,

        "maxRewardedAdsPerDay":
            MAX_REWARDED_AD_CREDITS_PER_DAY,
    }
```
