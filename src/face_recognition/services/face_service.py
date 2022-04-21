import random
import time

from face_recognition.modules.Controller import Controller


async def __get_gender_and_age(face_properties: dict):
    try:
        # print(face_properties)
        __features = random.choice(face_properties['faces'])
        features = __features['features']
        gender = 1 if features['gender']['gender'].lower() == 'male' else 2
        age = features['age']

        return age, gender

    except Exception as e:
        return False


async def get_gender_and_age(url, controller: Controller):
    photo = await controller.get_photo(url)
    if photo is None:
        return False

    # while True:
    # try:
    try:
        face_properties = await controller.get_face_properties(photo)
    except Exception as e:
        print(e, 'face properties', url)
        return False
        #     break
        # except Exception as e:
        #     print(e)
        #     print('sleep')
        #     time.sleep(20)

    result = await __get_gender_and_age(face_properties)
    return result
