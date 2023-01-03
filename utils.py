from random import randint

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

import settings


def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)  # noqa: S311
    if user_number > bot_number:
        message = f'Ваше число {user_number}, моё {bot_number}. Вы выиграли!'
    elif user_number == bot_number:
        message = f'Ваше число {user_number}, моё {bot_number}. Ничья!'
    else:
        message = f'Ваше число {user_number}, моё {bot_number}. Вы проиграли!'
    return message


def has_object_on_image(file_name, obj_name):
    chanel = ClarifaiChannel.get_grpc_channel()
    app = service_pb2_grpc.V2Stub(chanel)
    metadata = (('authorization', f'Key {settings.CLARIFAI_API_KEY}'),)

    with open(file_name, 'rb') as f:
        file_data = f.read()
        image = resources_pb2.Image(base64=file_data)

    request = service_pb2.PostModelOutputsRequest(
        model_id='aaa03c23b3724a16a56b629203edc62c',
        inputs=[resources_pb2.Input(data=resources_pb2.Data(image=image))],
    )
    response = app.PostModelOutputs(request, metadata=metadata)

    return check_resp_for_obj(response, obj_name)


def check_resp_for_obj(response, obj_name):
    if response.status.code == status_code_pb2.SUCCESS:
        for concept in response.outputs[0].data.concepts:
            if concept.name == obj_name and concept.value >= 0.9:  # noqa: WPS432, WPS459
                return True
    else:
        print(f'Recognition error {response.outputs[0].status.details}')
    return False
