
import json
import os
from os.path import join, dirname
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from flask import Flask, render_template, request
from flask import send_file

authenticator = IAMAuthenticator('apiKey')
service = TextToSpeechV1(authenticator=authenticator)
service.set_service_url('https://gateway-lon.watsonplatform.net/text-to-speech/api')


file_path = join(dirname(__file__), "audio.wav")
class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.fd = open(file_path, 'ab')

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_content_type(self, content_type):
        print('Content type: {}'.format(content_type))

    def on_timing_information(self, timing_information):
        print(timing_information)

    def on_audio_stream(self, audio_stream):
        self.fd.write(audio_stream)

    def on_close(self):
        self.fd.close()
        print('Done synthesizing. Closing the connection')

app = Flask(__name__)

@app.route('/')
def home():
    if (os.path.exists(file_path)):
        os.remove(file_path)
    return render_template('ui.html')

@app.route("/submit", methods=["GET", "POST"])
def submit():
	if request.method == "POST":
		req = request.form
		text = req.get("audioinput")
		my_callback = MySynthesizeCallback()
		service.synthesize_using_websocket(text,
		                                   my_callback,
		                                   accept='audio/wav',
		                                   voice='en-US_MichaelV3Voice'
		                                  )
		return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

