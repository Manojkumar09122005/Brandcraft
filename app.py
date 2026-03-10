import os

# Fix SSL certificate issues - MUST be before importing requests
os.environ.setdefault("SSL_CERT_FILE", r"C:\Users\manoj\AppData\Roaming\Python\Python313\site-packages\certifi\cacert.pem")
os.environ.setdefault("REQUESTS_CA_BUNDLE", r"C:\Users\manoj\AppData\Roaming\Python\Python313\site-packages\certifi\cacert.pem")

# Additional SSL fix for Windows with PostgreSQL conflicts
try:
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
except ImportError:
    pass

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, g
import requests
from dotenv import load_dotenv

# Groq Cloud API integration
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ Groq library not installed. Run: pip install groq")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

load_dotenv()

# Groq Cloud API Configuration (FREE & FAST!)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Initialize Groq client
if GROQ_AVAILABLE and GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    print(f"✅ Groq Cloud initialized with model: {GROQ_MODEL}")
else:
    groq_client = None
    print("❌ Groq API key not configured. Get free key at https://console.groq.com/keys")

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

REPLICATE_SDXL_VERSION = os.getenv(
    "REPLICATE_SDXL_VERSION",
    "7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    register_routes(app)
    init_db()

    return app


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not DB_PATH.exists():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS branding_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_idea TEXT NOT NULL,
                industry TEXT NOT NULL,
                target_audience TEXT,
                brand_tone TEXT,
                brand_name TEXT,
                tagline TEXT,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()


def hf_generate_text(prompt, max_new_tokens=256, temperature=0.8):
    """
    Generate text using Groq Cloud API ONLY
    """
    
    if not groq_client or not GROQ_API_KEY:
        return "❌ Groq API key not configured. Please add your GROQ_API_KEY to .env file. Get free key at https://console.groq.com/keys"
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
        )
        
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return "No response from Groq."
            
    except Exception as e:
        return f"Error calling Groq API: {e}"


def generate_brand_names(business_idea, industry, target_audience, brand_tone):
    
    prompt = f"""
You are a branding expert.

Business idea: {business_idea}
Industry: {industry}
Target audience: {target_audience}
Tone: {brand_tone}

Generate 5 creative brand names.

Return ONLY a JSON array of strings like this: ["Name1", "Name2", "Name3", "Name4", "Name5"]
No explanations, just the JSON array.
"""

    text = hf_generate_text(prompt, temperature=0.9)
    
    # Debug: print what we got from Groq
    print(f"Groq response for brand names: {text[:200]}")

    try:
        # Try to parse as JSON
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return {"brand_names": parsed}
        else:
            # If not a list, try to extract names
            return {"brand_names": [text.split()[0][:20]]}  # Take first word
    except Exception as e:
        print(f"JSON parse error: {e}")
        # Fallback: split by newlines or commas
        names = [line.strip().strip('"[],') for line in text.split('\n') if line.strip() and not line.startswith('[') and not line.startswith(']')]
        names = [name for name in names if name][:5]
        return {"brand_names": names if names else ["BrandName"]}


def generate_taglines(brand_name, business_idea, industry, brand_tone):
    
    prompt = f"""
Create 3 short taglines for brand {brand_name}

Industry: {industry}
Tone: {brand_tone}

Return ONLY a JSON array of strings like this: ["Tagline1", "Tagline2", "Tagline3"]
No explanations, just the JSON array.
"""

    text = hf_generate_text(prompt, temperature=0.8)
    
    print(f"🏷️ Tagline response: {text[:200]}")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return {"taglines": parsed}
        else:
            return {"taglines": [text.split('\n')[0][:50]]}
    except Exception as e:
        print(f"Tagline JSON parse error: {e}")
        # Fallback: split by newlines
        lines = [line.strip().strip('"[],') for line in text.split('\n') if line.strip() and not line.startswith('[') and not line.startswith(']')]
        lines = [line for line in lines if line][:3]
        return {"taglines": lines if lines else ["Great Brand", "Quality First", "Choose Excellence"]}


def generate_description(brand_name, business_idea, industry, audience, tone):

    prompt = f"""
Write a short brand description.

Brand: {brand_name}
Business: {business_idea}
Industry: {industry}
Audience: {audience}
Tone: {tone}
"""

    desc = hf_generate_text(prompt)

    return {"description": desc}


def generate_domains(brand_name):

    base = "".join(ch for ch in brand_name.lower() if ch.isalnum())

    domains = [
        f"{base}.com",
        f"{base}.ai",
        f"get{base}.com",
        f"{base}hq.com"
    ]

    return domains


def analyze_sentiment(text):
    """
    Analyze sentiment using Groq API (since we removed HuggingFace)
    """
    
    if not groq_client or not GROQ_API_KEY:
        return {"label": "unknown", "error": "Groq API not configured"}
    
    prompt = f"""Analyze the sentiment of this text and respond with ONLY one word: Positive, Negative, or Neutral.

Text: {text}

Sentiment:"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.3,
        )
        
        label = response.choices[0].message.content.strip().capitalize()
        
        # Map to standard labels
        if "POSITIV" in label.upper():
            label = "Positive"
        elif "NEGAT" in label.upper():
            label = "Negative"
        else:
            label = "Neutral"
        
        return {"label": label, "score": 0.85}  # Mock confidence score
        
    except Exception as e:
        return {"label": "unknown", "error": str(e)}


def register_routes(app):

    @app.route("/")
    def index():
        return render_template("home.html")
    
    @app.route("/home")
    def home():
        return render_template("home.html")
    
    @app.route("/brand")
    def brand():
        return render_template("index.html")
    
    @app.route("/brand-score")
    def brand_score():
        return render_template("brand-score.html")
    
    @app.route("/domain-checker")
    def domain_checker():
        return render_template("domain-checker.html")
    
    @app.route("/social-post")
    def social_post():
        return render_template("social-post.html")
    
    @app.route("/logo")
    def logo():
        # For now, redirect to main brand page where logo can be generated
        return render_template("index.html")
    
    @app.route("/marketing")
    def marketing():
        # Redirect to social post generator
        return render_template("social-post.html")
    
    @app.route("/sentiment")
    def sentiment_page():
        return render_template("index.html")
    
    @app.route("/assistant")
    def assistant():
        return render_template("index.html")

    @app.route("/generate-brand", methods=["POST"])
    def generate_brand():

        data = request.json

        idea = data.get("business_idea")
        industry = data.get("industry")
        audience = data.get("target_audience")
        tone = data.get("brand_tone")

        names = generate_brand_names(idea, industry, audience, tone)["brand_names"]

        brand_name = names[0] if names else "MyBrand"

        taglines = generate_taglines(
            brand_name, idea, industry, tone)["taglines"]

        description = generate_description(
            brand_name, idea, industry, audience, tone)["description"]

        domains = generate_domains(brand_name)

        response = {
            "brand_names": names,
            "taglines": taglines,
            "description": description,
            "domains": domains
        }

        return jsonify(response)

    @app.route("/analyze-sentiment", methods=["POST"])
    def sentiment():
        text = request.json.get("text")
        result = analyze_sentiment(text)
        return jsonify(result)
    
    @app.route("/generate-logo", methods=["POST"])
    def generate_logo():
        """Generate logo using FREE Logo APIs with fallback"""
        
        data = request.json or {}
        brand_name = data.get("brand_name", "Brand")
        industry = data.get("industry", "Technology")
        
        print(f"🎨 Generating logo via API for: {brand_name} ({industry})")
        
        try:
            # Method 1: Try Pollinations AI (primary)
            # Create varied prompts to get different results
            import random
            styles = [
                "professional minimalist logo design",
                "modern geometric logo with clean lines",
                "elegant typography-based logo",
                "abstract artistic logo symbol",
                "bold contemporary brand mark"
            ]
            
            backgrounds = [
                "white background",
                "clean white backdrop",
                "pure white background, high contrast"
            ]
            
            style = random.choice(styles)
            background = random.choice(backgrounds)
            
            prompt = f"{style} for {brand_name}, {background}, modern typography, vector style, high quality, professional branding"
            
            encoded_prompt = requests.utils.quote(prompt)
            # Use timestamp + random for unique seed each time
            seed = int(time.time() * 1000) % 1000000 + random.randint(0, 999)
            
            logo_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
            
            print(f"📡 Generated logo URL (seed={seed}): {logo_url[:100]}...")
            
            # Test the URL with longer timeout
            head_response = requests.head(logo_url, timeout=30, allow_redirects=True)
            print(f"✅ Logo URL status: {head_response.status_code}")
            
            if head_response.status_code == 200:
                return jsonify({
                    "logo_url": logo_url,
                    "concept": f"Professional logo for {brand_name}",
                    "colors": ["#3B82F6", "#8B5CF6", "#06B6D4"]
                })
            elif head_response.status_code == 429:
                # Rate limited - use fallback
                print("⚠️ Rate limited, using fallback API...")
                
        except Exception as e:
            print(f"💥 Pollinations error: {e}")
            print("🔄 Switching to fallback method...")
        
        # Fallback: Generate SVG logo locally with variety
        print("🎨 Using SVG fallback...")
        svg_logo = generate_fallback_svg_variety(brand_name, industry)
        
        return jsonify({
            "logo_url": f"data:image/svg+xml;base64,{svg_logo}",
            "concept": f"Custom logo for {brand_name}",
            "colors": ["#3B82F6", "#8B5CF6", "#06B6D4"]
        })


def generate_fallback_svg_variety(brand_name, industry):
    """Generate varied SVG logos with different designs"""
    
    import random
    
    first_letter = brand_name[0].upper() if brand_name else "B"
    
    # Color schemes based on industry
    color_schemes = {
        "food": ["#F59E0B", "#EF4444", "#FCD34D"],
        "fitness": ["#EF4444", "#F97316", "#F59E0B"],
        "health": ["#10B981", "#34D399", "#6EE7B7"],
        "technology": ["#3B82F6", "#8B5CF6", "#06B6D4"],
        "fashion": ["#EC4899", "#F472B6", "#A855F7"],
        "finance": ["#1E40AF", "#3B82F6", "#60A5FA"],
        "education": ["#7C3AED", "#A78BFA", "#C4B5FD"],
    }
    
    colors = color_schemes.get(industry.lower(), color_schemes["technology"])
    
    # Random design type
    design_types = ["circle", "hexagon", "square", "triangle"]
    design = random.choice(design_types)
    
    if design == "circle":
        svg_content = f"""
        <circle cx="150" cy="150" r="120" fill="url(#grad1)" opacity="0.15"/>
        <circle cx="150" cy="150" r="100" fill="none" stroke="url(#grad1)" stroke-width="5"/>
        <circle cx="150" cy="150" r="85" fill="none" stroke="{colors[2]}" stroke-width="3" stroke-dasharray="10,5"/>
        <text x="150" y="170" font-family="Arial, sans-serif" font-size="85" font-weight="bold" fill="url(#grad1)" text-anchor="middle">{first_letter}</text>
        """
    elif design == "hexagon":
        svg_content = f"""
        <polygon points="150,40 235,90 235,190 150,240 65,190 65,90" fill="url(#grad1)" opacity="0.12"/>
        <polygon points="150,55 220,95 220,185 150,225 80,185 80,95" fill="none" stroke="url(#grad1)" stroke-width="5"/>
        <polygon points="150,70 205,100 205,180 150,210 95,180 95,100" fill="none" stroke="{colors[2]}" stroke-width="3"/>
        <text x="150" y="165" font-family="Arial, sans-serif" font-size="75" font-weight="bold" fill="url(#grad1)" text-anchor="middle">{first_letter}</text>
        """
    elif design == "square":
        svg_content = f"""
        <rect x="50" y="50" width="200" height="200" rx="25" fill="url(#grad1)" opacity="0.15"/>
        <rect x="65" y="65" width="170" height="170" rx="20" fill="none" stroke="url(#grad1)" stroke-width="5"/>
        <rect x="80" y="80" width="140" height="140" rx="15" fill="none" stroke="{colors[2]}" stroke-width="3"/>
        <text x="150" y="160" font-family="Arial, sans-serif" font-size="80" font-weight="bold" fill="url(#grad1)" text-anchor="middle">{first_letter}</text>
        """
    else:  # triangle
        svg_content = f"""
        <polygon points="150,50 240,230 60,230" fill="url(#grad1)" opacity="0.12"/>
        <polygon points="150,70 220,210 80,210" fill="none" stroke="url(#grad1)" stroke-width="5"/>
        <polygon points="150,90 200,190 100,190" fill="none" stroke="{colors[2]}" stroke-width="3"/>
        <text x="150" y="175" font-family="Arial, sans-serif" font-size="75" font-weight="bold" fill="url(#grad1)" text-anchor="middle">{first_letter}</text>
        """
    
    # Build complete SVG
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{colors[0]};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{colors[1]};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="300" height="300" fill="#0f172a"/>
        {svg_content}
        <text x="150" y="255" font-family="Arial, sans-serif" font-size="22" fill="#ffffff" text-anchor="middle" letter-spacing="3">{brand_name.upper()}</text>
    </svg>"""
    
    import base64
    return base64.b64encode(svg.encode()).decode()

    @app.route("/chat-assistant", methods=["POST"])
    def chat_assistant():
        """AI branding assistant chat using Groq"""
        
        if not groq_client or not GROQ_API_KEY:
            return jsonify({"error": "Groq API not configured"}), 500
        
        data = request.json or {}
        question = data.get("question", "")
        context = data.get("context", {})
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Build prompt with context
        system_prompt = """You are an expert AI branding assistant. Help users with branding strategy, marketing, positioning, and business advice. Be concise, practical, and actionable."""
        
        context_text = ""
        if context:
            if context.get("primary_brand_name"):
                context_text += f"\nBrand Name: {context['primary_brand_name']}"
            if context.get("business_idea"):
                context_text += f"\nBusiness: {context['business_idea']}"
            if context.get("industry"):
                context_text += f"\nIndustry: {context['industry']}"
            if context.get("target_audience"):
                context_text += f"\nAudience: {context['target_audience']}"
        
        full_prompt = f"{system_prompt}\n\n{context_text}\n\nUser Question: {question}\n\nYour helpful answer:"
        
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content.strip()
            return jsonify({"answer": answer})
            
        except Exception as e:
            print(f"Chat assistant error: {e}")
            return jsonify({"error": str(e)}), 500


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")