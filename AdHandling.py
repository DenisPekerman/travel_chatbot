import os
import openai
import json

def extract_question_metadata(user_message):
    system_prompt = """
    1. You're an assistant designed to detect if the user's message explicitly or implicitly references any city or country. 
    2. If mentioned, extract and clearly indicate the city or country. 
    3. Return a JSON object with keys 'country' and 'city'. 
    4. If nothing is detected, set the values to null.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
    except Exception as e:
        raise Exception({f"Error during extract_question_metadata API call: {str(e)}"})
    
    # Extract the message content, which is expected to be a JSON string
    metadata_json = json.loads(response.choices[0].message.content)

    return metadata_json


def load_ads():
    """
    Load ads JSON from an external file located in the TravelAgent directory.
    """
    ads_file_path = os.path.join(os.path.dirname(__file__), "ads.json")
    with open(ads_file_path, "r") as file:
        ads = json.load(file)
    return ads

    
def choose_ad(user_message):
    ads = load_ads()
    metadata_json = None
    try:
        metadata_json = extract_question_metadata(user_message)
        print(metadata_json)
    except Exception as e:
        return None
    
    country = metadata_json["country"]
    city = metadata_json["city"]
    chosen_ad = None
    
    if country:
        for ad in ads:
            if country.lower() == ad["country"].lower():
                chosen_ad = ad
                break
    
    if city and not chosen_ad:
        for ad in ads:
            for value in ad.values():
                if city.lower() in value.lower():
                    chosen_ad = ad
                    break
                
    if not chosen_ad:
        return None

    targeted_ad = format_ad(chosen_ad)
    return targeted_ad


def format_ad(ad):
    return f"{ad['title']}\n{ad['content']}\n{ad['publisher']}"


