
import hashlib



from ai.vision_analyzer import (
    analyze_image,
    analyze_text
)


from ai.tutor_engine import (
    TutorSession,
    generate_hint
)


from vision.quality_check import (
    check_image_quality
)


from vision.pdf_processor import (
    process_pdf
)


from cache.response_cache import (
    get_response,
    save_response
)





# ==========================================
# HASH FICHIER
# ==========================================


def create_file_hash(file_bytes):

    return hashlib.sha256(
        file_bytes
    ).hexdigest()





# ==========================================
# CACHE
# ==========================================


def get_cached_analysis(file_hash):

    return get_response(
        file_hash
    )





def save_cached_analysis(
    file_hash,
    analysis
):

    save_response(

        file_hash,

        analysis

    )







# ==========================================
# IMAGE
# ==========================================


def process_image(file):


    file_bytes = file.read()



    file_hash = create_file_hash(
        file_bytes
    )



    cached = get_cached_analysis(
        file_hash
    )



    if cached:


        analysis = cached



    else:


        quality = check_image_quality(
            file_bytes
        )



        if not quality["valid"]:


            return {

                "success":False,

                "error":
                quality["message"]

            }





        analysis = analyze_image(

            file_bytes,

            getattr(
                file,
                "type",
                "image/jpeg"
            )

        )



        save_cached_analysis(

            file_hash,

            analysis

        )






    session = TutorSession()



    session.exercise = analysis




    hint = generate_hint(
        session
    )




    return {


        "success":True,


        "analysis":analysis,


        "session":session,


        "first_hint":hint


    }






# ==========================================
# PDF / DOCUMENT
# ==========================================


def process_document(file):


    extension = file.name.split(".")[-1].lower()



    if extension == "pdf":


        result = process_pdf(
            file
        )


        analysis = analyze_text(
            result["text"]
        )



    else:


        return process_image(
            file
        )





    session = TutorSession()



    session.exercise = analysis



    hint = generate_hint(
        session
    )



    return {


        "success":True,


        "analysis":analysis,


        "session":session,


        "first_hint":hint


    }






# ==========================================
# ROUTEUR PRINCIPAL
# ==========================================


def process_exercise(file):


    filename = file.name.lower()



    if filename.endswith(
        ".pdf"
    ):


        return process_document(
            file
        )



    else:


        return process_image(
            file
        )

