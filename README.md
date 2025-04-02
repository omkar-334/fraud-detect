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


Here are the assets:
frautect-applied-ai