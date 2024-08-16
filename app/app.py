from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from PIL import Image
import numpy as np
from googletrans import Translator
import cv2
import base64
from gtts import gTTS
from io import BytesIO
import logging

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Load the trained model to classify signs
model = load_model('model30.h5')

# Dictionary to label all traffic signs class
classes = {1: 'Speed limit (20km/h)', 2: 'Speed limit (30km/h)', 3: 'Speed limit (50km/h)',
           4: 'Speed limit (60km/h)', 5: 'Speed limit (70km/h)', 6: 'Speed limit (80km/h)',
           7: 'End of speed limit (80km/h)', 8: 'Speed limit (100km/h)', 9: 'Speed limit (120km/h)',
           10: 'No passing', 11: 'No passing veh over 3.5 tons', 12: 'Right-of-way at intersection',
           13: 'Priority road', 14: 'Yield', 15: 'Stop', 16: 'No vehicles', 17: 'Veh > 3.5 tons prohibited',
           18: 'No entry', 19: 'General caution', 20: 'Dangerous curve left', 21: 'Dangerous curve right',
           22: 'Double curve', 23: 'Bumpy road', 24: 'Slippery road', 25: 'Road narrows on the right',
           26: 'Road work', 27: 'Traffic signals', 28: 'Pedestrians', 29: 'Children crossing',
           30: 'Bicycles crossing', 31: 'Beware of ice/snow', 32: 'Wild animals crossing',
           33: 'End speed + passing limits', 34: 'Turn right ahead', 35: 'Turn left ahead',
           36: 'Ahead only', 37: 'Go straight or right', 38: 'Go straight or left', 39: 'Keep right',
           40: 'Keep left', 41: 'Roundabout mandatory', 42: 'End of no passing',
           43: 'End no passing veh > 3.5 tons'}

translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    file = request.files['file']
    image = Image.open(file.stream)
    image = image.resize((30, 30))
    image = np.expand_dims(image, axis=0)
    image = np.array(image)

    pred = np.argmax(model.predict(image), axis=1)[0]
    classified_sign_text = classes[pred + 1]
    return jsonify({'classified_sign': classified_sign_text})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data['text']
    dest_lang = data['lang']
    try:
        translation = translator.translate(text, dest=dest_lang)
        return jsonify({'translated_text': translation.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data['text']
    logging.debug(f"Received text for TTS: {text}")

    try:
        # Convert text to speech using gTTS
        tts = gTTS(text=text, lang='en')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        # Convert BytesIO to base64 to send as a response
        audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        audio_fp.close()

        logging.debug("TTS conversion successful")
        return jsonify({'audio': audio_base64})
    except Exception as e:
        logging.error(f"Error during TTS conversion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/camera')
def camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert color from BGR to RGB
        frame_pil = Image.fromarray(frame)  # Convert array to PIL Image
        frame_pil = frame_pil.resize((30, 30))  # Resize to match model input
        frame_array = np.expand_dims(np.array(frame_pil), axis=0)  # Expand dims for model input

        pred = np.argmax(model.predict(frame_array), axis=1)[0]
        classified_sign_text = classes[pred + 1]

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({'frame': frame_b64, 'classified_sign': classified_sign_text})
    else:
        return jsonify({'error': 'Failed to capture image'}), 500


if __name__ == '__main__':
    app.run(debug=True)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0',port=5000)