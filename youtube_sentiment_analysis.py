import os
import pandas as pd
from googleapiclient.discovery import build
from textblob import TextBlob
import nltk

# Download NLTK data files
nltk.download('punkt')

# YouTube Data API v3 setup
API_KEY = 'AIzaSyD93JMqMxyeKmykIki-vUxbyttl2U9oQeE'  # Replace with your actual API key
VIDEO_URL = 'https://youtu.be/EWvsIS4y1ro?si=CAbRJo-nU8m0u-wc'

# Extract video ID from the URL
VIDEO_ID = VIDEO_URL.split('/')[-1].split('?')[0]

# Function to get comments from YouTube
def get_comments(video_id, api_key, max_comments=500):
    comments = []
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100  # Fetch 100 comments at a time
    )
    
    while request and len(comments) < max_comments:
        response = request.execute()
        
        # Process the comments in this response
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        
        # Check if there is a next page of comments
        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                pageToken=response['nextPageToken']
            )
        else:
            break  # Exit the loop if there are no more pages

    return comments

# Function to perform sentiment analysis
def sentiment_analysis(comments):
    sentiments = []
    for comment in comments:
        analysis = TextBlob(comment)
        sentiments.append(analysis.sentiment.polarity)
    
    df = pd.DataFrame({
        'Comment': comments,
        'Sentiment': sentiments
    })
    
    return df

# Main execution
if __name__ == '__main__':
    comments = get_comments(VIDEO_ID, API_KEY, max_comments=500)  # Get up to 500 comments
    df = sentiment_analysis(comments)

    # Save the results to a CSV file with utf-8 encoding
    df.to_csv('youtube_comments_sentiment.csv', index=False, encoding='utf-8')

    # Optional: Indicate to the user that the results have been saved
    print("Sentiment analysis results saved to 'youtube_comments_sentiment.csv'.")
