

import json
import os



DATABASE_FILE="HintAI/storage/database.json"



def load_database():


    if not os.path.exists(
        DATABASE_FILE
    ):

        return {

            "sessions":[],

            "skills":[],

            "payments":[],

            "messages":[]

        }


    with open(
        DATABASE_FILE,
        "r",
        encoding="utf8"
    ) as f:

        return json.load(f)




def save_database(data):


    os.makedirs(
        os.path.dirname(DATABASE_FILE),
        exist_ok=True
    )


    with open(
        DATABASE_FILE,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )





def add_item(
    category,
    item
):

    db=load_database()


    db[category].append(item)


    save_database(db)

