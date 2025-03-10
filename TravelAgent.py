import os
from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv
from AddHandling import choose_ad

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

def travel_agent_chat(user_message, history=None):
    if history is None:
        history = []

    targeted_ad = choose_ad(user_message)
    
    system_message = f"""
        You are a knowledgeable and friendly travel agent. 
        Provide expert travel advice, including recommendations on destinations, itineraries, flights, hotels, and local experiences. 
        If the user asks questions unrelated to travel, politely state that you only provide travel-related information.

        You should answer the question based on your own knowledge. 

        You should also use this information and integrate it seamlessly: 
        ---
        {targeted_ad}
        ---
        Do not add anything to targeted_ad.
        Surrond everything that tangeted_ad returns with <div class="sponsored-content"></div> tags.
        """
    
    # Build the conversation messages for OpenAI
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Error during API call: {str(e)}"

    # Update the conversation history (the travel agent's answer does not include the ad)
    # history.append({"role": "assistant", "content": bot_message})
    return bot_message


def predict(user_message, history):
    msg = travel_agent_chat(user_message, history)
    return msg


with gr.Blocks(css=".sponsored-content { font-style: italic; color: red; }") as demo:
        chat = gr.ChatInterface(
            predict,
            type="messages"
        )

demo.launch(share=True)


# if __name__ == "__main__":
#     tra   el_agent_chat("I want to go to Paris");