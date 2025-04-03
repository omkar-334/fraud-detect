import json

from google_play_scraper import Sort, app, permissions, reviews, search

from llm import describe_screenshots
from utils import scrape, validate_email


def search_apps(query, country="us"):
    results = search(query, n_hits=10, country=country)
    package_names = [app["appId"] for app in results]
    return package_names


def get_reviews(app_id, num=100):
    new_reviews, _ = reviews(
        app_id,
        count=num // 4,
        sort=Sort.NEWEST,
        filter_score_with=None,
        lang="en",
        country="us",
    )
    relevant_reviews, _ = reviews(
        app_id,
        count=num // 4,
        sort=Sort.MOST_RELEVANT,
        filter_score_with=None,
        lang="en",
        country="us",
    )
    balanced_reviews = get_balanced_reviews(app_id, num_per_rating=num // 10)
    all_reviews = [*new_reviews, *relevant_reviews, *balanced_reviews]
    keys = ("userName", "content", "score", "thumbsUpCount")
    all_reviews = [{k: review.get(k) for k in keys} for review in all_reviews]

    return all_reviews


def get_balanced_reviews(app_id, num_per_rating=10):
    all_reviews = []

    for rating in range(1, 6):  # Loop through ratings 1 to 5
        rating_reviews, _ = reviews(
            app_id,
            count=num_per_rating,
            sort=Sort.NEWEST,
            filter_score_with=rating,
            lang="en",
            country="us",
        )
        all_reviews.extend(rating_reviews)

    return all_reviews


def get_app_details(app_id):
    details = app(app_id)
    ads1 = details.pop("containsAds")
    ads2 = details.pop("adSupported")
    app_info = {
        "appId": details.pop("appId"),
        "categories": details.pop("categories"),
        "category": details.pop("genre"),
        "categoryId": details.pop("genreId"),
        "contentRating": details.pop("contentRating"),
        "contentRatingDescription": details.pop("contentRatingDescription", "N/A"),
        "currency": details.pop("currency", "N/A"),
        "description": details.pop("description"),
        "developer": {
            "name": (name := details.pop("developer")),
            "id": details.pop("developerId"),
            "email": (email := details.pop("developerEmail", "N/A")),
            "privacyPolicy": details.pop("privacyPolicy", "N/A"),
            "website": details.pop("developerWebsite", "N/A"),
            "legalName": name,
            "legalEmail": email,
            "legalAddress": details.pop("developerAddress", "N/A"),
        },
        "features": {
            #     "isEditorChoice": details.pop("editorChoice"),
            "hasAds": ads1 and ads2,
            # "isPreregister": details.pop("preRegister", False),
            # "isEarlyAccess": details.pop("earlyAccess", False),
            # "isPlayPassAvailable": details.pop("playPass", False),
            # "requiredFeatures": details.pop("requiredFeatures", []),
        },
        "hasInAppPurchases": details.pop("offersIAP"),
        "inAppProductPrice": details.pop("inAppProductPrice", "N/A"),
        "headerImage": details.pop("headerImage", ""),
        "icon": details.pop("icon"),
        "isFree": details.pop("free"),
        "media": {
            "screenshots": details.pop("screenshots", []),
            "video": details.pop("video", None),
            "videoImage": details.pop("videoImage", None),
            # "previewVideo": details.pop("video", None),
            # "ipadScreenshots": [],
            # "appletvScreenshots": [],
        },
        "metrics": {
            "ratings": {
                "average": (score := details.pop("score")),
                "averageText": str(score),
                "total": details.pop("ratings"),
                "distribution": dict(zip(range(1, 6), details.pop("histogram"))),
            },
            "reviews": details.pop("reviews"),
            "installs": {
                "text": details.pop("installs"),
                "min": details.pop("minInstalls"),
                "max": details.pop("realInstalls"),
            },
        },
        "price": details.pop("price"),
        "priceText": details.pop("priceText", "Free"),
        "summary": details.pop("summary"),
        "title": details.pop("title"),
        "url": details.pop("url"),
        "version": {
            "number": details.pop("version", "N/A"),
            "released": details.pop("released", "N/A"),
            "updated": details.pop("updated", "N/A"),
            "lastUpdated": details.pop("lastUpdatedOn", "N/A"),
            # "minimumOsVersion": details.pop("androidVersion", "N/A"),
            # "maximumOsVersion": "VARY",
        },
        "comments": details.pop("comments", []),
        "extra": details,
    }

    with open("app_details.json", "w", encoding="utf-8") as f:
        json.dump(app_info, f, indent=4, ensure_ascii=False, default=str)

    return app_info


def add_info(details):
    details = describe_screenshots(details)
    try:
        perms = permissions(details["appId"])
    except Exception:
        perms = {}
    new = {
        "permissions": perms,
        "reviews": get_reviews(details["appId"]),
    }
    if valid_email := validate_email(details["developer"]["email"]):
        new["emailValid"] = valid_email
    if details["developer"].get("website", "N/A") != "N/A":
        new["websiteContent"] = scrape(details["developer"]["website"])
    return details | new


if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv

    load_dotenv()
    apps = [
        "com.google.android.apps.dynamite",
        "com.openai.chatgpt",
        "ai.socialapps.speakmaster",
        "org.telegram.messenger",
        "com.facebook.orca",
        "com.snapchat.android",
        "com.discord",
        "com.whatsapp",
        "com.google.android.apps.messaging",
        "ai.character.app",
    ]
    get_app_details(apps[-1])
