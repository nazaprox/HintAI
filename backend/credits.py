from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from threading import RLock
from .config import STREAK_3_DAYS_REWARD, STREAK_6_DAYS_REWARD, get_action_cost, get_plan_credits, is_streak_action
_LOCK=RLock()
_ACCOUNTS={}

def _account(user_id):
    if user_id not in _ACCOUNTS:
        _ACCOUNTS[user_id]={"userId":user_id,"plan":"free","balance":Decimal(get_plan_credits("free")),"streak":0,"lastActionDate":None,"reward3Claimed":False,"reward6Claimed":False,"transactions":[]}
    return _ACCOUNTS[user_id]

def get_account(user_id):
    a=_account(user_id)
    return {**a,"balance":float(a["balance"]),"transactions":list(a["transactions"])}

def set_plan(user_id,plan):
    if plan not in {"free","basic","pro","pro_plus","super","heavy"}: raise ValueError("Plan invalide.")
    a=_account(user_id); a["plan"]=plan; a["balance"]=Decimal(get_plan_credits(plan)); return get_account(user_id)

def consume(user_id,action):
    amount=Decimal(get_action_cost(action)); a=_account(user_id)
    if a["balance"]<amount: raise ValueError("Crédits insuffisants.")
    a["balance"]-=amount; a["transactions"].append({"type":"spend","action":action,"amount":-float(amount)}); return get_account(user_id)

def reward(user_id,amount,reason="reward"):
    a=_account(user_id); a["balance"]+=Decimal(amount); a["transactions"].append({"type":"reward","reason":reason,"amount":float(amount)}); return get_account(user_id)

def register_action(user_id,action): return get_account(user_id)

def initialize_user(user_id): return _account(user_id)
def get_balance(user_id): return int(_account(user_id)["balance"])
def is_premium(user_id): return _account(user_id)["plan"]!="free"
def can_spend(user_id,amount): return _account(user_id)["balance"]>=Decimal(amount)
def spend(user_id,amount): return int(consume(user_id,"hint_1")["balance"] if int(amount)==1 else consume(user_id,"help_me_analysis")["balance"])
def add(user_id,amount): return int(reward(user_id,amount)["balance"])
def add_history(user_id,item): _account(user_id)["transactions"].append({"type":"history",**item})
def get_user_data(user_id):
    a=_account(user_id)
    return {"credits":int(a["balance"]),"is_premium":a["plan"]!="free","xp":len(a["transactions"])*10,"level":1,"streak_days":a["streak"],"history":[x for x in a["transactions"] if x.get("type")=="history"]}
