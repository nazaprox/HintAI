

import json
import os
from datetime import datetime



FILE="HintAI/storage/logs.json"



def log_event(
    event,
    data=None
):


    logs=[]


    if os.path.exists(FILE):

        with open(
            FILE,
            "r",
            encoding="utf8"
        ) as f:

            logs=json.load(f)



    logs.append({

        "time":
        str(datetime.now()),

        "event":
        event,

        "data":
        data

    })



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
            logs,
            f,
            indent=4,
            ensure_ascii=False
        )

