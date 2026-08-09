

import os



def check_environment():


    errors=[]



    if not os.getenv(
        "GEMINI_API_KEY"
    ):

        errors.append(
            "GEMINI_API_KEY absente"
        )



    return {

        "secure":
        len(errors)==0,

        "errors":
        errors

    }

