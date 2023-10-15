import re
import requests
from app import db
import time
from google.cloud import translate_v2 as translate
import os

from app.PostModel import Post

# Your OpenAI API key
api_key = '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'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "app/rahpax-74bd5d61fd29.json"

# Instantiate a translation client
translate_client = translate.Client()



def translate_content(post_id, content):
    paragraphs = re.split(r'\n\n+', content)  # Split content into paragraphs at two or more newlines
    translated_paragraphs = []
    max_retries = 5
    retry_delay = 60  # Wait for 60 seconds before retrying

    for paragraph in paragraphs:
        if not re.search(r'<script|<link|<style', paragraph, re.I):  # Ignore scripts, links, and styles
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {"role": "system", "content": "You are a helpful assistant."
                                                  "Translate the following English text to Persian, but do not "
                                                  "translate"
                                                  "anything enclosed within <code> and </code> tags."},

                    {"role": "user", "content": f"{re.sub(r'(```|```)', '<code>', paragraph)}"}
                ]
            }

            for attempt in range(max_retries):
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
                if response.status_code == 200:
                    response_json = response.json()
                    translated_paragraph = response_json['choices'][0]['message']['content'].strip()
                    translated_paragraphs.append(translated_paragraph)
                    break  # Break out of the retry loop if the request is successful
                elif response.status_code == 429:  # Rate limit error
                    print(
                        f'Rate limit error. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})')
                    time.sleep(retry_delay)  # Wait for the specified delay before retrying
                else:
                    print(f'Error: {response.status_code}')
                    print(response.text)
                    translated_paragraphs.append(paragraph)  # Keep the original paragraph on error
                    break  # Break out of the retry loop if an error other than rate limit error occurs
        else:
            translated_paragraphs.append(paragraph)  # Keep original paragraph if it contains script, link, or style

    translated_content = '\n\n'.join(translated_paragraphs)

    post = Post.query.filter_by(post_id=post_id).first()
    if post:
        post.translated_content = translated_content
        post.status = 'Translated'
        db.session.commit()


def translate_content_google(post_id, content):
    # Translate the content
    result = translate_client.translate(content, target_language='fa')
    translated_content = result['translatedText']

    post = Post.query.filter_by(post_id=post_id).first()
    if post:
        post.translated_content = translated_content
        post.status = 'Translated'
        db.session.commit()
