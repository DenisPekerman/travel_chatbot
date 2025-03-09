import os
import openai
import gradio as gr
import json
import random
from dotenv import load_dotenv

# Import the ad injection utility functions
from AdInjector import load_ads, get_ad

# Load environment variables from the .env file (ensure this file is secure)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load ads JSON using the ad_injector utility
ads = load_ads()

def travel_agent_chat(user_message, history):
    if history is None:
        history = []
    
    # Use the ad injector utility to get an ad message based on the user message
    ad_message = get_ad(user_message, ads)
    
    # System prompt to set the travel agent personality and guidelines
    system_message = (
        "You are a knowledgeable and friendly travel agent. "
        "Provide expert travel advice, including recommendations on destinations, itineraries, flights, hotels, and local experiences. "
        "If the user asks questions unrelated to travel, politely state that you only provide travel-related information."
    )

    # Build the conversation messages for OpenAI
    messages = [{"role": "system", "content": system_message}]
    for user_text, bot_text in history:
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": bot_text})
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Error during API call: {str(e)}"

    # Update the conversation history (the travel agent's answer does not include the ad)
    history.append((user_message, bot_message))
    return ad_message, bot_message, history

def respond(user_message, history):
    # Process the user message to get the separate ad and travel agent answer
    ad_message, bot_message, history = travel_agent_chat(user_message, history)
    # Return an empty input to clear the textbox, the ad output, the updated conversation history, and the state
    return "", ad_message, history, history



with gr.Blocks() as demo:
    gr.Markdown("# Travel Agent Chatbot Demo")
    gr.Markdown(
        "Chat with our travel specialist! Ask for travel advice, destination recommendations, and itinerary ideas. "
        "If your message references Italy or France, an HTML ad will be shown above the travel agent's answer."
    )
    
    # HTML component to display the ad output separately
    ad_html = gr.HTML(label="Advertisement")
    # Chatbot component displays the conversation history
    chatbot = gr.Chatbot(label="Conversation History")
    # Textbox for user input
    msg = gr.Textbox(placeholder="Type your message here...", label="Your Message")
    # State component to hold conversation history
    state = gr.State([])

    # When the user submits a message, update the ad output and the conversation history
    msg.submit(respond, inputs=[msg, state], outputs=[msg, ad_html, chatbot, state])

demo.launch(share=True)
