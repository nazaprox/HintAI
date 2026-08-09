

import uuid
import json
import os


FILE="HintAI/storage/users.json"



def load_users():

    if not os.path.exists(FILE):

        return []


    with open(
        FILE,
        "r",
        encoding="utf8"
    ) as f:

        return json.load(f)




def save_users(users):

    os.makedirs(
        os.path.dirname(FILE),
        exist_ok=True
    )


    with open(
        FILE,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            users,
            f,
            indent=4,
            ensure_ascii=False
        )




def create_user(
    name,
    class_level
):


    users=load_users()


    user={

        "user_id":str(uuid.uuid4()),

        "name":name,

        "class":class_level,

        "plan":"free",

        "created_at":str(datetime.now()),

        "credits":30,

        "xp":0

    }


    users.append(user)


    save_users(users)


    return user





def get_user(user_id):


    users=load_users()


    for user in users:

        if user["user_id"]==user_id:

            return user


    return None




def update_plan(
    user_id,
    plan
):


    users=load_users()


    for user in users:

        if user["user_id"]==user_id:

            user["plan"]=plan



    save_users(users)

