import os
import json
import random
import openai
import json

def load_ads():
    """
    Load ads JSON from an external file located in the TravelAgent directory.
    """
    ads_file_path = os.path.join(os.path.dirname(__file__), "ads.json")
    with open(ads_file_path, "r") as file:
        ads = json.load(file)
    return ads

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
        if "italy" in result.lower():
            return "Italy"
        elif "france" in result.lower():
            return "France"
        else:
            return ""
    except Exception as e:
        # In case of error, return an empty string so no ad is selected
        return ""

def get_ad(user_message, ads):
    """
    Checks the user's message for a geographical reference and returns an HTML ad snippet
    if the reference is to Italy or France.
    """
    detected_country = detect_country(user_message)
    if detected_country and detected_country in ads:
        ad_keys = list(ads[detected_country].keys())
        chosen_ad_key = random.choice(ad_keys)
        ad_values = ads[detected_country][chosen_ad_key]
        ad_content = (
            f"<strong style='color: red;'>THIS IS AN AD!!</strong><br>"
            f"<strong>Heading:</strong> {ad_values['heading']}<br>"
            f"<strong>Body:</strong> {ad_values['body']}<br>"
            f"<strong>Publisher:</strong> {ad_values['publisher']}<br>"
            f"<strong>Link:</strong> <a href='{ad_values['link']}' target='_blank'>{ad_values['link']}</a><br>"
        )
        return f"<ad>{ad_content}</ad>"
    return ""

