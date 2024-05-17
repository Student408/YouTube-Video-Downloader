from flask import Flask, render_template, request, jsonify, send_file
from pytube import YouTube
import os
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    url = request.form['url']
    yt = YouTube(url)
    
    video_info = {
        'title': yt.title,
        'thumbnail_url': yt.thumbnail_url,
        'streams': {
            'video': [{'resolution': stream.resolution, 'itag': stream.itag} for stream in yt.streams.filter(progressive=True).order_by('resolution')],
            'audio': [{'abr': stream.abr, 'itag': stream.itag} for stream in yt.streams.filter(only_audio=True).order_by('abr')]
        }
    }
    return jsonify(video_info)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    itag = request.form['itag']
    
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    
    buffer = BytesIO()
    stream.stream_to_buffer(buffer)
    buffer.seek(0)
    
    if stream.type == 'audio':
        mime_type = "audio/mp3"
        file_extension = "mp3"
    else:
        mime_type = "video/mp4"
        file_extension = "mp4"
    
    return send_file(buffer, as_attachment=True, download_name=f"{yt.title}.{file_extension}", mimetype=mime_type)

if __name__ == '__main__':
    app.run()
