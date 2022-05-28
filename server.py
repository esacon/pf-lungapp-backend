import threading
from flask import Flask
from flask_cors import CORS, cross_origin
from waitress import serve
from src.routes.user import user as user_routes
from src.routes.audio import audio as audio_routes
from logging import getLogger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.after_request 
@cross_origin(supports_credentials=True)
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    # Other headers can be added here if needed
    return response

# Routes
app.register_blueprint(user_routes, url_prefix='/user')
app.register_blueprint(audio_routes, url_prefix='/audio')

# get instance of logger and set log severity as defined by the cli parameter
gunicorn_logger = getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    serve(app, port=5000)
    #app.run(port=5000, threaded=True, debug=True)