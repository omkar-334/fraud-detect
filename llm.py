import enum
import json
import os
import time

import openai
import requests
from google import genai
from google.genai import types

from utils import truncate_text

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class App(enum.Enum):
    FRAUD: str = "fraud"
    GENUINE: str = "genuine"
    SUSPECTED: str = "suspected"


def load_json(response):
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        print("Error: GPT response is not valid JSON. Using fallback.")
        response = None
    return response


def get_base(details):
    title = details["title"]
    summary = details["summary"]
    description = details["description"]
    prompt = f"""
    Provide a single structured JSON output in this format:
    {{ "type": "fraud"|"genuine"|"suspected", "reason": "Concise explanation (300 char max)" }}

    App details:
    Title: {title}
    Summary: {summary}
    Description: {description}
    """
    return prompt


def extract_image(url):
    image = requests.get(url)
    mime = image.headers["content-type"]

    response = client.models.generate_content(
        # model="gemini-2.0-flash-001",
        model="gemini-2.0-flash-lite",
        contents=["What is this image?", types.Part.from_bytes(data=image.content, mime_type=mime)],
    )
    return response.text


def describe_screenshots(details, num=5):
    urls = list(details["media"]["screenshots"])
    ssdict = {}
    # to respect rate limits, only process 5 images for each app
    for url in urls[:num]:
        time.sleep(1)
        try:
            text = extract_image(url)
            print(text)
            ssdict[url] = text
        except Exception as e:
            print(f"Error extracting image: {e}")

    details["media"]["screenshots"] = ssdict
    details["media"]["other_screenshots"] = urls[num:]
    return details


def analyze_fraud(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "You are an AI expert in fraud detection for mobile apps. "
                            + "Respond with valid JSON only in this format: "
                            + '{"type": "fraud"|"genuine"|"suspected", "reason": "Concise explanation (300 char max)"}\n\n'
                            + prompt
                        }
                    ],
                }
            ],
            config={
                "temperature": 0.5,
                "response_mime_type": "application/json",
            },
        )

        response_text = response.text
        return json.loads(response_text)

    except Exception as e:
        print(f"Error in analyze_fraud: {e}")
        return None


# def analyze_fraud(prompt):
#     # response = gpt.chat.completions.create(
#     #     model="gpt-4",
#     #     messages=[{"role": "system", "content": "You are an AI expert in fraud detection for mobile apps."}, {"role": "user", "content": prompt}],
#     #     temperature=0.5,
#     #     # response_format={type: "json_schema"},
#     # )
#     response = response.model_dump()["choices"][0]["message"]["content"]
#     response = load_json(response)
#     print(response)
#     return response


def analyze_developer(app_data):
    dev_details = app_data["developer"]

    prompt = f"""
    Analyze the following app developer information for potential fraud and provide your reasoning.
    Guidelines -
    1. You are given the developer's website content and the app description.
    2. Check if the developer's website contains any suspicious or fraudulent elements.

    {get_base(app_data)}
    Developer Information:
    {json.dumps(dev_details, indent=2)}
    
    Website Content: {app_data.get("websiteContent", "N/A")}
    """
    prompt = truncate_text(prompt)
    return analyze_fraud(prompt)


def analyze_images(app_data):
    content = list(app_data["media"]["screenshots"].values())
    prompt = f"""
    Analyze the following app screenshots descriptions for potential fraud and provide your reasoning.
    Guidelines -
    1. Identify any discrepancies or suspicious elements that may indicate fraudulent activity.
    2. Check if the screenshots match the app's description and functionality.
    3. Check if the screenshots are fake, spam, misleading, or irrelevant. (Check if the image descriptions are related to the app description)

    {get_base(app_data)}
    App Screenshot Descriptions:
    {json.dumps(content, indent=2)}
    """

    return analyze_fraud(prompt)


def analyze_reviews(app_data):
    content = app_data["reviews"]
    prompt = f"""
    Analyze the following app reviews for potential fraud and provide your reasoning.
    Guidelines -
    1. Identify any discrepancies or suspicious elements that may indicate fraudulent activity.
    2. Check if the reviews match the app's description and functionality.
    3. Check if reviews are fake, spam, misleading, or irrelevant.
    4. Check if the reviews are from verified users or bots.
    5. Check if the reviews contain repeated phrases or words or emojis.

    {get_base(app_data)}
    Reviews:
    {json.dumps(content, indent=2)}
    """
    prompt = truncate_text(prompt)
    return analyze_fraud(prompt)


def analyze_basic(app_data):
    # app_data.pop("media")
    app_data.pop("extra")
    app_data.pop("reviews")
    # app_data.pop("permissions")
    app_data.pop("emailValid", None)
    app_data.pop("websiteContent")
    prompt = f"""
    Analyze the following app description and basic details for potential fraud and provide your reasoning.
    Guidelines -
    1. Identify any discrepancies or suspicious elements that may indicate fraudulent activity.
    2. Check if the description matches the app's functionality and features.
    3. Check if the description is misleading or irrelevant.
    4. Check if the app description aligns with the app's title, summary and screenshot descriptions, and permissions.

    {get_base(app_data)}

    App Description:
    {json.dumps(app_data, indent=2)}

    """
    return analyze_fraud(prompt)


def analyze_permissions(app_data):
    content = app_data["permissions"]
    prompt = f"""
    Analyze the following app permissions for potential fraud and provide your reasoning accordingly.
    Guidelines -
    1. Identify any discrepancies or suspicious elements that may indicate fraudulent activity.
    2. Check if the permissions are necessary for the app's functionality.
    3. Check if the permissions are excessive or intrusive.
    4. Check if the permissions are related to sensitive data or device features.

    {get_base(app_data)}
    Permissions:
    {json.dumps(content, indent=2)}
    """
    return analyze_fraud(prompt)


def analyze_overall(results, app_data):
    # Your priorities are - Developer Analysis > Image Analysis > Review Analysis > Description Analysis > Permissions Analysis.
    prompt = f"""
    Analyze the following fraud detection results for the app and provide your reasoning accordingly.
    
    Instructions:
    1. Review all five analysis results provided for the app.
    2. Give equal weight to each analysis—do not prioritize one over the others.
    3. Based on the collective findings, summarize the key insights from each analysis.
    4. Provide a thoughtful final assessment of the app's potential fraud status.
    5. If the app is suspected of fraud, critically re-evaluate the evidence and try to resolve the suspicion—either confirm it as fraudulent or clear it as genuine.
    6. Consider the app's details (such as metadata, description, and behavior) in your reasoning.
    {get_base(app_data)}
    Results:
    {json.dumps(results, indent=2)}

    """
    return analyze_fraud(prompt)


def analyze(app_data, filename=None, print=False):
    results = {
        "image_analysis": analyze_images(app_data),
        "review_analysis": analyze_reviews(app_data),
        "developer_analysis": analyze_developer(app_data),
        "description_analysis": analyze_basic(app_data),
        "permissions_analysis": analyze_permissions(app_data),
    }
    results["overall_analysis"] = analyze_overall(results, app_data)
    if filename:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
    if print:
        print(json.dumps(results, indent=2))
    return results


# Example usage:
if __name__ == "__main__":
    with open("sample/app_details.json", encoding="utf-8") as file:
        app_data = json.load(file)

    analyze(app_data)
