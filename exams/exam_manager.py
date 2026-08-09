

import json
import os



FILE="HintAI/storage/exams.json"



def load_exams():


    if not os.path.exists(FILE):

        return {

            "BEPC":[],

            "BAC":[]

        }


    with open(
        FILE,
        "r",
        encoding="utf8"
    ) as f:

        return json.load(f)





def add_exam(
    level,
    subject,
    title,
    premium=False
):


    exams=load_exams()


    exam={

        "title":title,

        "subject":subject,

        "premium":premium

    }


    exams[level].append(exam)


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
            exams,
            f,
            indent=4,
            ensure_ascii=False
        )





def list_exams(level):

    exams=load_exams()

    return exams.get(
        level,
        []
    )

