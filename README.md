<<<<<<< HEAD
## BrandCraft AI – Generative AI Powered Branding Automation Platform

BrandCraft AI is a complete multi-page SaaS platform built with Flask + Tailwind CSS that generates professional brand identities using AI — including names, taglines, descriptions, color palettes, logo concepts, social content, domain analysis, and marketing strategies. Features a modern landing page, brand score evaluator, domain checker, and social media post generator.

### Features

- **Brand name generator**: 5 creative brand name options.
- **Tagline generator**: 3 short taglines for the brand.
- **Brand description**: A 2–3 sentence brand summary.
- **Logo generator**: Minimal modern logo via Stable Diffusion–compatible API.
- **Color palette**: Primary, secondary, and accent colors based on tone/industry.
- **Social media post**: Instagram-style post with hashtags.
- **Domain suggestions**: Common domain patterns for the chosen name.
- **Marketing strategy tips**: 3 launch tips.
- **Sentiment analysis**: Hugging Face sentiment model for brand feedback.
- **Branding assistant chatbot**: Ask branding questions in a small chat widget.

### Tech stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML, Tailwind CSS (CDN), vanilla JavaScript
- **AI APIs**:
  - **Groq Cloud** (FREE & FAST - Primary LLM for all text generation)
  - Replicate API with SDXL (for logo generation)

### Local setup

1. **Create a virtual environment (recommended)**:

   ```bash
   cd brandcraft  # or the project root folder
   python -m venv .venv
   source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (create a `.env` file next to `app.py`):

   ```bash
   # Groq Cloud API - FREE & FAST (Required!)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.2-3b-preview
   
   # Replicate API for logo generation (SDXL)
   REPLICATE_API_TOKEN=your_replicate_api_token
   
   # Flask configuration
   SECRET_KEY=change-this-in-production
   PORT=5000
   ```
   
   **Note:** 
   - Get your **FREE Groq API key** from https://console.groq.com/keys
   - Get your Replicate token from https://replicate.com/account/api-tokens

4. **Run the app**:

   ```bash
   python app.py
   ```

5. Open `http://localhost:5000` in your browser.

On first run, a `database.db` SQLite file will be created with a simple `branding_sessions` table to store generated sessions.

### Deployment (Render / Railway style)

- Use `python app.py` as the start command (or `gunicorn app:app` for production).
- Ensure the working directory contains:
  - `app.py`
  - `requirements.txt`
  - `templates/` and `static/` folders
- Set the environment variables listed above in your hosting provider’s dashboard.
- Most platforms will expose `PORT` automatically; the app reads `PORT` and defaults to `5000`.

### Notes

- **Groq Cloud (Primary)**: Uses `llama-3.2-3b-preview` - FREE, extremely fast inference. Get API key at https://console.groq.com/keys
- **Logo Generation**: Uses Replicate API with SDXL model. Expects a JSON response with an `image_url` or `url` field.
- **Sentiment Analysis**: Now powered by Groq AI (no HuggingFace dependency).
- **API Keys**: If any API keys are missing, the app will still render, but the corresponding feature will return a friendly error message or placeholder.
- **Multi-Page Structure**: The app now includes multiple pages:
  - `/home` - Modern SaaS landing page
  - `/brand` - Main brand generator
  - `/brand-score` - AI brand evaluation tool
  - `/domain-checker` - Domain availability checker
  - `/social-post` - Social media post generator

### Free Groq Models Available (2024)

Groq offers these **FREE models** (no credit card required):
- `llama-3.1-8b-instant` - Recommended for this project ✅ (FAST & FREE)
- `llama-3.1-70b-versatile` - More powerful, slightly slower
- `llama-3.2-11b-vision-preview` - Multimodal (text + images)
- `llama-3.2-3b-preview` - Lightweight (when available)
- `gemma2-9b-it` - Google's open model
- `mixtral-8x7b-32768` - High quality, large context

**Current Model Used:** `llama-3.1-8b-instant` ✅
=======
# Brandcraft
>>>>>>> c87b9e2af21a12f9746e9d52ef40bca0534e69fb
