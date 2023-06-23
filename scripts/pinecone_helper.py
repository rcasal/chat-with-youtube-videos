
import argparse
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pinecone
import os
import csv
import json


load_dotenv()


def store_transcript(transcript, video_url, video_title):
    """Stores a transcript in the Pinecone vector database.

    Args:
      transcript: The transcript to store.
      video_url: The URL of the video associated with the transcript.
      video_title: The title of the video associated with the transcript.

    Returns:
      A list of documents that were stored in the Pinecone vector database.
    """

    pinecone.init(
        api_key=os.environ.get("PINECONE_API_KEY"),
        environment=os.environ.get("PINECONE_ENVIRONMENT"),
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
    )

    metadatas = [{
        "video_url": video_url,
        "video_title": video_title,
    }]

    docs = splitter.create_documents([transcript], metadatas=metadatas)
    # model='text-embedding-ada-002' by default
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY"), )
    Pinecone.from_documents(
        docs, embeddings, index_name=os.environ.get("PINECONE_INDEX")
    )


def main(transcriptions_directory):
    for filename in os.listdir(transcriptions_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(transcriptions_directory, filename)
        
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
            # Extract the required values from the JSON data
            video_url = data.get('url')
            video_title = data.get('title')
            transcript = data.get('concat_srt')
            
            # Call the store_transcript() function with the extracted values
            store_transcript(transcript, video_url, video_title)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Save transcriptions in Pinecone')
    parser.add_argument('transcriptions_directory', type=str,
                        help='Transcription output folder path')
    args = parser.parse_args()

    main(args.transcriptions_directory)
