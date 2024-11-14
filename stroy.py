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
    
    
