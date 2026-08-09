
import cv2



def detect_figures(image_path):

    """
    Détection simple de figures.
    Version V1.
    """

    result = {

        "has_figure": False,
        "objects": []

    }



    try:

        image = cv2.imread(image_path)


        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        edges = cv2.Canny(
            gray,
            50,
            150
        )


        contours,_ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


        if len(contours) > 5:

            result["has_figure"] = True


            result["objects"].append(
                "possible_geometry"
            )


        return result



    except Exception:

        return result

