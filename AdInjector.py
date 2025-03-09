import os
import json
import random
import openai
import gradio as gr
from dotenv import load_dotenv

# Load environment variables from the .env file (ensure this file is secure)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load ads JSON from an external file located in the TravelAgent directory
ads_file_path = os.path.join(os.path.dirname(__file__), "ads.json")
with open(ads_file_path, "r") as file:
    ads = json.load(file)

def detect_country(user_message):
    """
    Process the user's input through OpenAI to determine if it references a geographical location
    related to Italy or France. If so, return the country name exactly as either "Italy" or "France".
    """
    prompt = f"""
Given the following text, identify if it contains a reference to a geographical location related to Italy or France.
If it does, return only the country name ("Italy" or "France") without any additional text.
If both are referenced, return one of them arbitrarily.
Examples:
- Input: "food in paris" -> Output: "France"
- Input: "places to go in {{french district}}" -> Output: "France"
Text: {user_message}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a text analysis assistant specialized in geographical location identification."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        # Normalize and return the detected country if present
        if "italy" in result.lower():
            return "Italy"
        elif "france" in result.lower():
            return "France"
        else:
            return ""
    except Exception as e:
        # In case of any error, return an empty string so no ad is selected
        return ""

def travel_agent_chat(user_message, history):
    if history is None:
        history = []
    
    # Use the reasoning endpoint to detect a geographical reference from the user's message
    detected_country = detect_country(user_message)
    ad_message = ""
    if detected_country and detected_country in ads:
        ad_keys = list(ads[detected_country].keys())
        chosen_ad_key = random.choice(ad_keys)
        ad_values = ads[detected_country][chosen_ad_key]
        ad_message = (
            f"Ad Suggestion from {detected_country}:\n"
            f"Heading: {ad_values['heading']}\n"
            f"Body: {ad_values['body']}\n"
            f"Publisher: {ad_values['publisher']}\n"
            f"Link: {ad_values['link']}\n\n"
        )

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

    # Prepend the ad message (if any) before the agent's response
    if ad_message:
        bot_message = ad_message + bot_message

    history.append((user_message, bot_message))
    return history

def respond(user_message, history):
    # Update conversation history with the latest user message and response
    history = travel_agent_chat(user_message, history)
    # Return an empty string to clear the input and the updated conversation history
    return "", history, history

with gr.Blocks() as demo:
    gr.Markdown("# Travel Agent Chatbot Demo")
    gr.Markdown(
        "Chat with our travel specialist! Ask for travel advice, destination recommendations, and itinerary ideas. "
        "The conversation history will display both your messages and the agent's responses."
    )
    
    # Chatbot component displays the conversation history
    chatbot = gr.Chatbot(label="Conversation History")
    # Textbox for user input
    msg = gr.Textbox(placeholder="Type your message here...", label="Your Message")
    # State component to hold conversation history
    state = gr.State([])

    # When the user submits a message, update the conversation history
    msg.submit(respond, inputs=[msg, state], outputs=[msg, chatbot, state])

demo.launch(share=True)
