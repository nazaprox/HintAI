
import json
import os



FILE = "HintAI/storage/user_progress.json"



def load_progress():


    if not os.path.exists(FILE):

        return {

            "credits":30,

            "xp":0,

            "level":1

        }


    with open(
        FILE,
        "r",
        encoding="utf8"
    ) as f:

        return json.load(f)





def save_progress(data):


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
            data,
            f,
            indent=4,
            ensure_ascii=False
        )





def add_credits(amount):


    data = load_progress()


    data["credits"] += amount


    save_progress(data)


    return data





def spend_credits(amount):


    data = load_progress()


    if data["credits"] < amount:

        return False


    data["credits"] -= amount


    save_progress(data)


    return True





def add_xp(amount):


    data = load_progress()


    data["xp"] += amount


    data["level"] = (
        data["xp"] // 500
    ) + 1


    save_progress(data)


    return data
