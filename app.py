from flask import Flask, render_template, jsonify, request, current_app as app
# from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from bardapi import Bard
import os
import requests
import webbrowser
import json
import time
import replicate
UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, template_folder='templateFiles',
            static_folder='staticFiles')

CORS(app, resources={
     r"/*": {"origins": "http://localhost:3000/Chatbot_interface"}})
# CORS(app, support_credentials=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        description = request.form['description']
        print(description)
        if len(description) != 0 and 'describe' in description:
            ss = ""
            for i in range(len(description)):
                if (description[i] == ","):
                    break
                ss += description[i]
            PAT = '8bfa59e06bfc455dbb1b4f3d9ba19456'
            USER_ID = 'clarifai'
            APP_ID = 'main'
            MODEL_ID = 'apparel-classification-v2'
            MODEL_VERSION_ID = '651c5412d53c408fa3b4fe3dcc060be7'
            IMAGE_URL = ss
            from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
            from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
            from clarifai_grpc.grpc.api.status import status_code_pb2
            channel = ClarifaiChannel.get_grpc_channel()
            stub = service_pb2_grpc.V2Stub(channel)

            metadata = (('authorization', 'Key ' + PAT),)

            userDataObject = resources_pb2.UserAppIDSet(
                user_id=USER_ID, app_id=APP_ID)

            post_model_outputs_response = stub.PostModelOutputs(
                service_pb2.PostModelOutputsRequest(
                    user_app_id=userDataObject,
                    model_id=MODEL_ID,
                    version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
                    inputs=[
                        resources_pb2.Input(
                            data=resources_pb2.Data(
                                image=resources_pb2.Image(
                                    url=IMAGE_URL
                                )
                            )
                        )
                    ]
                ),
                metadata=metadata
            )
            if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
                print(post_model_outputs_response.status)
                raise Exception("Post model outputs failed, status: " +
                                post_model_outputs_response.status.description)

# Since we have one input, one output will exist here
            output = post_model_outputs_response.outputs[0]

            # print("Predicted concepts:")
            str = ""
            for concept in output.data.concepts:
                str += concept.name
                str += " , "
            str = "The image contains "+str
            return jsonify({"text": str,
                            "ig": ss})
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']
        description = request.form['description']
        print(description)
        image_path = image.filename
        image.save(image_path)
        # print(image_path)x``
        REPLICATE_API_TOKEN = 'r8_1y4futHBfBGxAqQ4DkCMpjXPHG91J9s126pFK'
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        if '1' in description:
            descript_1 = ""
            for i in range(len(description)):
                if (description[i] == ","):
                    break
                descript_1 += description[i]
            output = replicate.run(
                "naklecha/clothing-segmentation:501aa8488496fffc6bbee9544729dc28654649f2e3c80de0bf08fb9fe71898f8",
                input={"image": open(image_path, "rb"), "clothing": "topwear"}
            )
            img1 = output[0]
            img_mask = output[1]
            # print(img_mask)
            # prev=descript_1
            print(img1)
            print(img_mask)
            text = descript_1
            text += "detailed skin texture, (blush:0.2), (goosebumps:0.3), subsurface scattering"
            text += "Photorealistic, Hyperrealistic, Hyperdetailed, analog style, soft lighting, subsurface scattering, realistic, heavy shadow, masterpiece, best quality, ultra realistic, 8k, golden ratio, Intricate, High Detail, film photography, soft focus"
            text += "big depth of field, Masterpiece, Vivid colors, Simplified style"

            url = "https://stablediffusionapi.com/api/v3/inpaint"
            payload = json.dumps({
                "key": "z9oUu7B1cIipBnKPObOliEFjTJGLBu7Lr6KqFPnElquHp4wUZ6tmqoaYZapX",
                "prompt": text,
                "negative_prompt": "deformed face, defromed legs, deformed body",
                "init_image": img1,
                "mask_image": img_mask,
                "width": "512",
                "height": "512",
                "samples": "1",
                "num_inference_steps": "30",
                "safety_checker": "no",
                "enhance_prompt": "yes",
                "guidance_scale": 2,
                "strength": 1,
                "seed": None,
                "webhook": None,
                "track_id": None
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response2 = requests.request(
                "POST", url, headers=headers, data=payload)
            # print(response2)
            pic_url = response2.json()["output"]
            
            if (len(pic_url) > 0):
                return jsonify({"text": "Generated image",
                                "ig": pic_url[0]})
            else:
                extracted_id = response2.json()["id"]
                time_val = response2.json()["eta"]
                wait_n_seconds(time_val)
                fetch_url = "https://stablediffusionapi.com/api/v4/dreambooth/fetch"

                payload2 = json.dumps({
                    "key": "hGhPb69N7qQRUMjmiirwEpo1qvbM6Ny7Ca5za7fJ3IjlNe6vooc34vaO9SMW",
                    "request_id": extracted_id
                })

                headers2 = {
                    'Content-Type': 'application/json'
                }

                response2 = requests.request(
                    "POST", url, headers=headers2, data=payload2)
                # print(response2.text)
                pic_url2 = response2.json()["output"]
                return jsonify({"text": "Generated image",
                                "ig": pic_url2[0]})

        elif '2' in description:
            descript_2 = ""
            print("hello")
            for i in range(len(description)):
                if (description[i] == ","):
                    break
                descript_2 += description[i]
            print(descript_2)
            output = replicate.run(
                "philz1337/controlnet-deliberate:57d86bd78018d138449fda45bfcafb8b10888379a600034cc2c7186faab98c66",
                input={"image": open(image_path, "rb"), "prompt":  descript_2, "ddim_steps": 40, "a_prompt": "best quality, extremely detailed",
                       "n_prompt": "deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4, text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"}
            )

            return jsonify({"text": "Generated image with deliberate",
                            "ig": output[1]})
        else:
            return jsonify({"text": "Invalid description",
                            "ig": "no"})

    except Exception as e:
        return jsonify({'text': str(e)}), 500


# @app.route('/')
def wait_n_seconds(n):
    """Waits n seconds."""
    time.sleep(n)


os.environ["_BARD_API_KEY"] = "dQj8xm1lQT3xBc0uxlAyWU6K5FLgDQK1GOjnoxjT9BOGlCrBnlcQN5xu7N1xSetUXeXRAw."

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.route('/description', methods=["POST"])
def description():
    try:
        data = request.json
        response_key = data.get('response_key')
        user_responses = {}
        with open('user_responses.json', 'r') as file:
            user_responses = json.load(file)
        content = ""
        for key, value in user_responses.items():
            if key == "age":
                content += f'{key} is ({value}:2) ,'
            else:
                content += f'{key} is {value} ,'
        content = content.rstrip(', ')
        print(content)
        text = "fashion clothes for"+content + "footwear"
        text += str("detailed skin texture, (blush:0.2), (goosebumps:0.3), subsurface scattering")
        text += str("Photorealistic, Hyperrealistic, Hyperdetailed, analog style, soft lighting, subsurface scattering, realistic, heavy shadow, masterpiece, best quality, ultra realistic, 8k, golden ratio, Intricate, High Detail, film photography, soft focus")
        text += str("Vivid colors")
        REPLICATE_API_TOKEN = 'r8_5SG6TgMGwQ1Fl4Ez8kMqr9hvwOQKfln2P5M2U'
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        output = replicate.run(
            "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input={"prompt": text,
                   "scheduler": "DDIM",
                   "negative_prompt": "anime, cartoon, comic, half face,poorly Rendered face, poorly drawn face,poor facial details,poorly drawn hands,poorly rendered hands,low resolution,Images cut out at the top, left, right, bottom,bad composition,mutated body parts,blurry image,disfigured,oversaturated,bad anatomy,deformed body features",
                   "num_inference_steps": 250,
                   "guidance_scale": 8,
                   }
        )
        # print(output[0])
        return jsonify({
            "text": "Recommended image for your special occasion",
            "ig": output[0]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cross_origin(supports_credentials=True)
@app.route('/answer/<string:prompt>')
def get_answer(prompt):
    global prev
    response = Bard().get_answer(str(prompt))
    content = response["content"]
    end_index = content.find(".", 100)
    res = content
    if end_index != -1:
        res = content[:end_index + 1]
    result = {
        "text": res,
        "ig": "no"
    }
    if 'suggest me some spicy packed food retail mrp items' in prompt.lower():
        result={
            "text":res,
            "ig":"yes.jpg"
        }
    if 'retaining' in prompt.lower() or 'remember' in prompt.lower():
        result = {
            "text": "What should I remember?",
            "ig": "no"
        }
    elif 'recommend me' in prompt.lower():
        # prompt = scraped data from insta, previous buy history etc.
        with open(r'd:\FLIPKART GRID final2.0\FLIPKART GRID\codes\final_prompt.txt', 'r') as file:
            file_contents = file.read()
        print(file_contents)
        REPLICATE_API_TOKEN = 'r8_5SG6TgMGwQ1Fl4Ez8kMqr9hvwOQKfln2P5M2U'
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
                # text = "Latest fashion trends", 
        prev = file_contents
        output = replicate.run(
            # "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
            "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input={"prompt": file_contents,
                   "scheduler": "DDIM",
                   "negative_prompt": "anime, cartoon, comic, half face, deformed face, extra legs, extra arms, deforemed legs, deformed arms",
                   "num_inference_steps": 250,
                   "guidance_scale": 8,
                   }
        )
        result = {
            "text": "An image generated according to your preference and ongoing social media trends",
            "ig": output[0],
        }
    elif any(place_keyword in prompt.lower() for place_keyword in ['generate dress', 'make','want','looking for']):
        result = {
            "text": "Could you kindly share some information about your body shape?",
            "ig": "https://www.bodybuildingmealplan.com/wp-content/uploads/body-types-chart.jpg",
            "response_key": "body_shape"}
    elif 'endomorph' in prompt.lower() or 'ectomorph' in prompt.lower() or 'mesomorph' in prompt.lower():
        result = {
            "text": "Could you please provide your age and gender so that I could recommend more personalized clothes?",
            "ig": "no",
            "response_key": "body_shape"
        }
    elif any(char.isdigit() for char in prompt):
        result = {
            "text": "Please provide a brief explanation of the location or special occasion for which you intend to wear your dress.",
            "ig": "no",
            "response_key": "age"
        }

    elif any(place_keyword in prompt.lower() for place_keyword in ['location', 'place', 'city', 'special occasion', 'occasion','wedding']):
        result = {
            "text": "Please wait while the image is being generated...",
            "ig": "no",
            "response_key": "place"
        }
    elif "please wait the image is being generated..." in prompt.lower():
        result = {
            "text": "Generating......",
            "ig": "no",
        }
    elif "don't like" in prompt.lower():
        new = Bard().get_answer("rephrase "+prev +
                                " and don't include the colours in the sentence which are mentioned next"+prompt)
        c = new["content"]
        e = c.find(".", 30)
        f = e
        r = c[:e + 1]
        print(r)

        REPLICATE_API_TOKEN = 'r8_5SG6TgMGwQ1Fl4Ez8kMqr9hvwOQKfln2P5M2U'
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        output = replicate.run(
            "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input={"prompt": r,
                   "scheduler": "DDIM",
                   "negative_prompt": "anime, cartoon, comic, half face, deformed face, extra legs, extra arms, deforemed legs, deformed arms",
                   "num_inference_steps": 250,
                   "guidance_scale": 8,
                   }
        )
        result = {
            "text": "An image generated according to your liking",
            "ig": output[0],
        }

    elif "look on me" in prompt.lower() or "celebrity" in prompt.lower() or "influencer" in prompt.lower():
        result = {
            "text": "Upload an image with a short dress description, including the desired generation style(1 or 2).\n1.Background retention increased and fashion remodeled\n2.Both background and fashion remodeled",
            "ig": "no"
        }
    elif "clothing choices" in prompt.lower() or "desciption in image" in prompt.lower():
        result = {
            "text": "Please share the image link for which you need a description. You can upload it below.",
            "ig": "no"
        }

    
    return jsonify(result)


@app.route('/write_to_file', methods=['POST'])
def write_to_file():
    try:
        data = request.json.get('data')
        with open('data.txt', 'w') as file:
            file.write(data)
        result = {
            'text': "Remembered"
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/read_file')
def read_file():
    try:
        with open('data.txt', 'r') as file:
            file_contents = file.read()
            remember_index = file_contents.find("remember that")
            after_remember = file_contents[remember_index +
                                           len("remember"):].strip()
            modified_text = after_remember.replace("I", "you")
            return jsonify({'text': modified_text})
    except Exception as e:
        return jsonify({'text': str(e)}), 500


@app.route('/save_response', methods=['POST'])
def save_response():
    try:
        data = request.json
        response_key = data.get('response_key')
        user_responses = {}
        try:
            with open('user_responses.json', 'r') as file:
                user_responses = json.load(file)
        except FileNotFoundError:
            pass
        user_responses[response_key] = data.get('data')
        with open('user_responses.json', 'w') as file:
            json.dump(user_responses, file)

        result = {
            'text': "Response saved"
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def hello_world():
    return "Hello_world"


if __name__ == "__main__":
    app.run(debug=True)
