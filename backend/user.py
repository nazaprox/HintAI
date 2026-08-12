import hashlib, uuid
from . import credits
_USERS={}

def _hash(password): return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(email,password,name='Élève',anon_user_id=None):
    email=email.strip().lower()
    if any(u['email']==email for u in _USERS.values()): raise ValueError('EMAIL_ALREADY_EXISTS')
    uid='usr_'+uuid.uuid4().hex[:12]
    _USERS[uid]={'user_id':uid,'email':email,'password_hash':_hash(password),'name':name,'is_anonymous':False}
    if anon_user_id and anon_user_id in credits._ACCOUNTS:
        credits._ACCOUNTS[uid]=credits._ACCOUNTS.pop(anon_user_id)
        credits._ACCOUNTS[uid]['userId']=uid
    else: credits.initialize_user(uid)
    return {'user_id':uid,'email':email,'name':name,'is_anonymous':False,'credits':credits.get_balance(uid),'token':f'token_{uid}'}

def login_user(email,password):
    email=email.strip().lower(); h=_hash(password)
    for uid,u in _USERS.items():
        if u['email']==email and u['password_hash']==h:
            d=credits.get_user_data(uid)
            return {'user_id':uid,'email':email,'name':u['name'],'is_anonymous':False,'token':f'token_{uid}',**d}
    raise ValueError('INVALID_CREDENTIALS')

def get_profile(user_id):
    if user_id in _USERS:
        u=_USERS[user_id]; return {'user_id':user_id,'email':u['email'],'name':u['name'],'is_anonymous':False,**credits.get_user_data(user_id)}
    return {'user_id':user_id,'email':None,'name':'Utilisateur Anonyme','is_anonymous':True,**credits.get_user_data(user_id)}
