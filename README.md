Project Objective:

Develop a system that can identify potentially fraudulent or harmful applications on the Google Play Store through automated analysis and machine learning.

Your key responsibilities will include:

1. Data Collection
  - Implement API integration to fetch Google Play Store app details (metadata, reviews, permissions, developer information)


2. LLM Integration
  - Connect to Large Language Models like Google's Gemini or OpenAI's ChatGPT
  - Configure the LLM to analyze app data for suspicious patterns


3. Fraud Detection Framework
  - Develop analysis methods based on suspicious permissions, review authenticity, misleading descriptions, etc.

4. Structured Output Generation
  - Configure the LLM to produce consistent outputs in this format:
    { "type": "fraud"|"genuine"|"suspected", "reason": "Concise explanation (300 char max)" }
  - Note that 'type' is an enum with only these three possible values


5. Testing & Validation
  - Test your system against the labeled datasets we'll provide
  - Document accuracy rates and performance metrics

Resources:

- Google Gemini API Documentation: https://ai.google.dev/gemini-api/docs/structured-output?lang=python

Expected Deliverables:

- Working prototype with complete data pipeline

- Documentation of your implementation and results

- Performance analysis with our labeled datasets

- Recommendations for further development

# Implementation

## Data collection

Used google-play-scraper along with firecrawl-py and mailboxlayer for google play app details, developer website content and developer email validation.  
Also included descriptions of screenshots using Gemini.  
Expanded the given dataset with permissions, reviews, image descriptions, website content and email validation.  

## Fraud Detection

Implemented using Google Gemini.  
Multiple analyses are performed and then an overall analysis is performed in this order.  
Developer Analysis > Image Analysis > Review Analysis > Description Analysis > Permissions Analysis ---> Overall Analysis.  

## Recommendations

Could've handled rate-limits better, added more features that were missing.
For the fraud detection, I could've used DsPy for the prompt optimization and fraud classification but could'nt do due to time constraint.  
I originally used OpenAI GPT4o but switched to Gemini because I didn't monitor it and I lost $3....  

Also could've extracted deeper insights like timestamps of reviews, check sudden spikes in rating. The permissions function was failing due to some error (could debug it properly.)  

A better way of classifying fraud would be to assign confidence scores for each analysis and maybe identifying fake reviews/patterns using NLP.  

