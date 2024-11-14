from flask import Flask, request, jsonify, send_file
import requests
from gtts import gTTS
import requests
import os
from uuid import uuid4
from moviepy.editor import *
import tempfile

app=Flask(__name__)


# Text-to-Speech 
@app.route('/generate_narration', methods=['POST'])
def generate_narration():
    story_text = request.json.get('story_text')
    voice = request.json.get('voice', 'en')  
     # Generate narration 
    filename = f"{uuid4()}.mp3"  
    tts = gTTS(text=story_text, lang=voice)
    tts.save(filename)

    return jsonify({'narration_url':f"/get_narrration/{filename}"})

@app.route('/get_narration/<filename>', methods=['GET'])  #route to file
def get_narration(filename):
    return send_file(filename, mimetype="audio/mpeg")
    
    
