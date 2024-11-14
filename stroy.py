from flask import Flask, request, jsonify, send_file
import requests
from gtts import gTTS
import requests
import os
from uuid import uuid4
from moviepy.editor import *
import tempfile

app=Flask(__name__)

STABILITY_API_KEY = os.getenv("sk-2CgR8FBOAAzl2csLP6MGeWilQE6d7SgrYzW3UFJ22J82bwHS")
STABILITY_API_URL = "https://api.stability.ai/v1alpha/generate"

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

# Text-to-Image 
@app.route('/generate_images', methods=['POST'])
def generate_images():
    story_text = request.json.get('story_text')
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "text_prompts": [{"text": story_text}],
        "cfg_scale": 7.0,  #image controlbetween 5-10
        "width": 512,      
        "height": 512,     
        "samples": 2       
    }
    response =requests.post(STABILITY_API_URL, headers=headers, json=data)
    if response.status_code==200:
        image_urls=[image["url"]for image in response.json().get("artifacats",[])]
        return jsonify({'image_urls':image_urls})
    else:
        return jsonify({'error': 'Failed to generate images','details':response.text}),500

#video generation
@app.route('/generate_video', methods=['POST'])
def generate_video():
    narration_url = request.json.get('narration_url')
    image_urls = request.json.get('image_urls')
    music_url = request.json.get('music_url')
    # narration
    narration_file = download_file(narration_url)
    # images
    image_files = [download_file(url) for url in image_urls]
    # bgm
    music_file = download_file(music_url)
    video = create_video_from_images_and_narration(image_files, narration_file, music_file)
    # video to temp
    video_output_path = f"video_{uuid4()}.mp4"
    video.write_videofile(video_output_path, codec='libx264')
    
    return send_file(video_output_path, mimetype="video/mp4")

def download_file(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"Failed to download file from {url}")


def create_video_from_images_and_narration(image_files, narration_file, music_file):
    clips = [ImageClip(img).set_duration(3) for img in image_files]  # image lasts 3 seconds
    
    video = concatenate_videoclips(clips, method="compose")
    # narration as audio to the video
    audio = AudioFileClip(narration_file)
    video = video.set_audio(audio)
    # background music add
    music = AudioFileClip(music_file).volumex(0.3)  
    final_audio = CompositeAudioClip([audio, music])  #  narration&music
    video = video.set_audio(final_audio)
    
    return video


if __name__ == '__main__':
    app.run(debug=True)