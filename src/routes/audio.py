import json
import boto3
import wave
import numpy as np
import src.routes.error as error
import src.database.schemas as schemas
from datetime import date
from os import environ as env
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Blueprint, request, Response, make_response
from bson import json_util
from bson.objectid import ObjectId
from src.database.connection import db
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from src.audio_analysis.Hilbert import envelope
from src.audio_analysis.Butterworth import filter_audio
from flask import current_app
from flask_cors import CORS, cross_origin
from scipy.signal import find_peaks

audio = Blueprint("audio", __name__)
cors = CORS(audio, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

load_dotenv()

BUCKET_NAME = env.get('BUCKET_NAME')
ACCESS_KEY_ID = env.get('ACCESS_KEY_ID')
ACCESS_SECRET_KEY = env.get('ACCESS_SECRET_KEY')
THRESHOLD = 0.4
CUT_FREQ = [250, 2500] # From 250 to 2500 Hz.
SRC_FOLDER = 'src/files/audios'

s3 = boto3.client('s3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
)


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@audio.after_request 
@cross_origin(supports_credentials=True)
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

    
@audio.route('/upload', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def upload_file():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    current_app.logger.info(request.form)
    data = request.form
    
    if db.users.find_one({'_id': ObjectId(data['user_id'])}):
        if data['audio_filename'] and data['audio_filename'] != "":
            try:                  
                audio_data = {
                    "audio_name": data['audio_filename'],
                    "upload_date": date.today().strftime(r"%d/%m/%Y"),
                    "user_id": data['user_id']
                }
               
                # Validating mongodb schema.
                audio_schema = schemas.get_audios_schema()
                validate(instance=audio_data, schema=audio_schema)

                result = db.audios.insert_one(audio_data)
                response = json_util.dumps({'_id': str(result.inserted_id), 'status': 200})   
                current_app.logger.error("Audio results uploaded")
                return Response(response, mimetype="application/json")       
            except ValidationError as e:
                current_app.logger.error(e)
                return error.validation()
        current_app.logger.error("Data do not match")
        return error.data_not_match()
    current_app.logger.error("User not found")
    return error.not_found()


@audio.route('/results/<audio_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_results(audio_id):
    # Retrieving user data by id.
    data = db.audios.find_one({ '_id': ObjectId(audio_id) })
    if data:
        try:          
            download_file(data['audio_name'])
            # Open audio file and extract fs and amplitude.
            audio = wave.open(f'{SRC_FOLDER}/audio.wav','r')
            amp = audio.readframes(-1)
            amp = np.frombuffer(amp, np.int16).astype(int).tolist()
            fs = audio.getframerate()
            duration = len(amp)/fs
            time = np.arange(0, duration, 1/fs)

            # Audio Filter
            bf_amp = filter_audio(amp, fs, cut_freq=CUT_FREQ, ftype='band')
            # Hilbert envelope.
            hilb_amp_norm = envelope(bf_amp, fs=CUT_FREQ[1])
            # Lowpass filter
            lp_amp = filter_audio(hilb_amp_norm, fs=CUT_FREQ[1], cut_freq=CUT_FREQ[0], ftype='low')

            audio_length = round(max(time))
            peaks, _ = find_peaks(lp_amp, height=THRESHOLD, distance=len(time)/audio_length)
            n_peaks = len(lp_amp[peaks])
            bps = n_peaks/audio_length
            bpm = bps*60
            print(audio_length, n_peaks, bps, bpm)

            result_data = {
                "audio_name": data['audio_name'],
                "frame_rate": int(fs),
                "num_channels": int(audio.getnchannels()),
                "time": time,
                "audio_amp": amp,
                "filter_amp": bf_amp,
                "envelope_amp": lp_amp,
                "n_peaks": n_peaks,
                "bpm": bpm
            }    
            response = json_util.dumps(result_data)
            return Response(response, mimetype="application/json")
        except ClientError as e:
            current_app.logger.error(e)
            return error.file_not_found()
    current_app.logger.error("User not found")
    return error.not_found()


@audio.route('/<user_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user_audios(user_id):
    data = db.audios.find({'user_id': user_id})
    if data:
        response = json_util.dumps(data)
        return Response(response, mimetype="application/json")
    return error.not_found()


@audio.route('/<id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_audio(id):
    # Deleting user data.
    data = db.audios.delete_one({'_id': ObjectId(id)})
    if data:
        response = json_util.dumps({'message': f'Audio {id} deleted successfully.', 'delete': 'True'})
        return Response(response, mimetype="application/json")
    return error.not_found()
    

def upload_file(filename):
    with open(filename, "rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, filename)


def download_file(filename):
    with open(f'{SRC_FOLDER}/audio.wav', 'wb') as f:
        s3.download_fileobj(BUCKET_NAME, f'public/{filename}', f)


def save_results(time, amp, fig_name):
    audio_length = round(max(time))
    peaks, _ = find_peaks(amp, height=THRESHOLD, distance=len(time)/audio_length)
    n_peaks = len(amp[peaks])
    bps = n_peaks/audio_length
    bpm = bps*60
    print(audio_length, n_peaks, bps, bpm)
    """    
    plt.figure(figsize=(10,7))
    plt.plot(time, amp, color='#595959')
    plt.plot(time, [THRESHOLD]*len(amp), color='#98050c', linestyle='dashed', linewidth=2)
    plt.plot(time[peaks], amp[peaks], 'h', color='#c92200', markersize=8)
    plt.title(f'Estimated Respiratory Rate From Breath Audio: {bpm} bpm')
    plt.xlabel('Time [s]')
    plt.ylabel('Normalized Amplitude')
    plt.legend(['Signal envelope', f'Threshold={THRESHOLD}', f'{n_peaks} Peaks'], loc='upper right')
    plt.grid()
    plt.savefig(f'src/files/{fig_name}')  
    """