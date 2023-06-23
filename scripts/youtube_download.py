import argparse
import csv
import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import parse_qs, urlparse
import json

def preprocess_type(type_param):
    type_mapping = {
        'transcription': 'transcription',
        'transcr': 'transcription',
        't': 'transcription',
        'audio': 'audio',
        'a': 'audio',
        'text': 'transcription',
        'transcript': 'transcription',
        'aud': 'audio',
        'auditory': 'audio',
        'sound': 'audio',
        'voice': 'audio',
        # Add more mappings as needed
    }

    lowercase_type = type_param.lower()

    # Check if the exact type exists in the mapping
    if lowercase_type in type_mapping:
        return type_mapping[lowercase_type]
    else:
        # Check for potential misspelled words
        for key in type_mapping:
            if key.startswith(lowercase_type):
                return type_mapping[key]

        # Handle unrecognized type
        return "transcription"
    

def download_transcriptions(url, video_id, title, output_path):
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    concat_srt = ' '.join(item['text'] for item in srt)

    data = {
        'url': url,
        'video_id': video_id,
        'title': title,
        'concat_srt': concat_srt
    }

    # Use the video_id as the filename
    filename = f"{video_id}.json"
    with open(output_path + "/" + filename, 'w') as json_file:
        json.dump(data, json_file)
        
def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'SponsorBlock': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def extract_video_id(url):
    video_id = url.split('v=')[1]
    return video_id


def main(csv_file, output_folder, type):
    preprocessed_type = preprocess_type(type)
    print("Downloading", preprocessed_type + "s")

    # Create the folder structure
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        
    # with open(csv_file, 'r') as f:
    #     youtube_urls = f.read().splitlines()
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
    
        for row in reader:
            url = row['url'] 
            title = row['title'] 
            if not url or not url.startswith("http"):
                print(f"Skipping invalid URL: '{url}'")
                continue
            video_id = extract_video_id(url)
            print("url", url)
            print("video_id", video_id)
            if video_id is None:
                print(f"Couldn't extract video ID from URL: '{url}'")
                continue
            if preprocessed_type == "audio":
                output_path = os.path.join(output_folder, video_id)
                download_audio(url, output_path)
            if preprocessed_type == "transcription":
                download_transcriptions(url, video_id, title, output_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download audio from YouTube URLs in a CSV file')
    parser.add_argument('csv_file', type=str,
                        help='Path to the CSV file containing YouTube URLs')
    parser.add_argument('output_folder', type=str,
                        help='Output folder path')
    parser.add_argument('type', type=str, default='transcription',
                    help='Select Audio or Transcription type. Default is Transcription.')

    args = parser.parse_args()

    main(args.csv_file, args.output_folder, args.type)
