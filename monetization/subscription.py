

PLANS={


"free":{

    "name":"Free",

    "daily_credits":20,

    "ads":True,

    "premium_exam":False

},


"premium":{

    "name":"Premium",

    "daily_credits":200,

    "ads":False,

    "premium_exam":True

},


"pro":{

    "name":"Pro",

    "daily_credits":999,

    "ads":False,

    "premium_exam":True

}


}



def get_plan(plan):

    return PLANS.get(
        plan,
        PLANS["free"]
    )





def can_access_exam(
    plan,
    premium
):


    if premium:

        return plan!="free"


    return True

