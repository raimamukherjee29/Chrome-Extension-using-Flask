from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import traceback

app = Flask(__name__)

@app.route('/summary', methods=['GET'])
def summary_api():
    try:
        url = request.args.get('url', '')
        video_id = url.split('=')[-1]
        transcript = get_transcript(video_id)
        
        if transcript is not None:
            summary = get_summary(transcript)
            return jsonify({'summary': summary}), 200
        else:
            return jsonify({'error': 'Failed to retrieve transcript'}), 500

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([d['text'] for d in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {str(e)}")
        return None

def get_summary(transcript):
    summarizer = pipeline('summarization')
    summary = ''
    for i in range(0, (len(transcript)//1000)+1):
        summary_text = summarizer(transcript[i*1000:(i+1)*1000])[0]['summary_text']
        summary += summary_text + ' '
    return summary.strip()

if __name__ == '__main__':
    app.run(debug=True)
