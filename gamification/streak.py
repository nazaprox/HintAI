
import json
import os
from datetime import date



FILE="HintAI/storage/streak.json"



def load():

    if not os.path.exists(FILE):

        return {

            "last_login":None,

            "streak":0

        }


    with open(FILE,"r") as f:

        return json.load(f)





def update_daily_streak():


    data=load()


    today=str(date.today())


    if data["last_login"] == today:

        return data



    data["streak"] += 1

    data["last_login"]=today



    with open(
        FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


    return data
