

from PIL import Image
import io



def check_image_quality(file):


    try:

        image = Image.open(file)


        width,height=image.size



        if width < 500 or height < 500:

            return {

                "ok":False,

                "reason":
                "Image trop petite"

            }



        return {

            "ok":True,

            "width":width,

            "height":height

        }



    except Exception as e:


        return {

            "ok":False,

            "reason":str(e)

        }

