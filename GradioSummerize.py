import os
import requests
from bs4 import BeautifulSoup
import gradio as gr
from dotenv import load_dotenv
import openai

# Load environment variables from the .env file
load_dotenv()

# The API key is loaded from the environment variable; it is not hard-coded in the script.
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching the URL: {str(e)}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    
    if not text:
        return "No textual content found on the page."
    
    limited_text = text[:2000]
    prompt = f"Summarize in 20 lines the following text:\n\n{limited_text}"
    
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        summary = completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during summarization: {str(e)}"
    
    return summary

demo = gr.Interface(
    fn=summarize_url,
    inputs=gr.Textbox(label="Enter a URL", placeholder="https://example.com"),
    outputs=gr.Textbox(label="Summary"),
    title="Webpage Summarization Demo",
    description="Enter a website URL to fetch its content and summarize it using OpenAI's GPT model."
)

demo.launch()
