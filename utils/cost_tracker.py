

import json
import os
from datetime import datetime



FILE="HintAI/storage/usage.json"



def load_usage():


    if not os.path.exists(FILE):

        return []


    with open(
        FILE,
        "r",
        encoding="utf8"
    ) as f:

        return json.load(f)





def save_usage(data):


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
            indent=4
        )





def register_usage(

    model,

    input_tokens,

    output_tokens

):


    usage=load_usage()



    item={

        "date":
        str(datetime.now()),

        "model":
        model,

        "input_tokens":
        input_tokens,

        "output_tokens":
        output_tokens

    }



    usage.append(item)


    save_usage(usage)


    return item

