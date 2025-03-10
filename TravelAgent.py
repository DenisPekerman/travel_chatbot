import os
import openai
import math
from random import randint, choice
import gradio as gr
from dotenv import load_dotenv

# Import the ad injection utility functions
from AdInjector import load_ads, get_ad

# Load environment variables from the .env file (ensure this file is secure)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load ads JSON using the ad_injector utility
ads = load_ads()

def choose_ad():
    # return a random ad
    ad = ads[0]
    print(ad)
    return ad

def format_ad(ad):
    return f"""
        {ad["title"]}
        {ad["content"]}
        {ad["country"]}
        {ad["publisher"]}
    """

def travel_agent_chat(user_message, history=None):
    if history is None:
        history = []

    ad = choose_ad()
    
    # System prompt to set the travel agent personality and guidelines
    system_message = f"""
        You are a knowledgeable and friendly travel agent. 
        Provide expert travel advice, including recommendations on destinations, itineraries, flights, hotels, and local experiences. 
        If the user asks questions unrelated to travel, politely state that you only provide travel-related information.

        You should answer the question based on your own knowledge. 

        You should also use this information and integrate it seamlessly: 
        ---
        {format_ad(ad)}
        ---
        Surrond the entire mention with <div class="sponsored-content"></div> tags.
        """
    

    # Build the conversation messages for OpenAI
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Error during API call: {str(e)}"

    # Update the conversation history (the travel agent's answer does not include the ad)
    history.append({"role": "assistant", "content": bot_message})
    return bot_message

def predict(user_message, history):
    msg = travel_agent_chat(user_message, history)
    return msg

with gr.Blocks(css=".sponsored-content {font-style: italic; color: red;}") as demo:

    chat = gr.ChatInterface(
        predict,
        type="messages"
    )

demo.launch()