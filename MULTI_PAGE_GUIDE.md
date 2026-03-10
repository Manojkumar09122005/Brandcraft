# BrandCraft AI - Multi-Page Structure

## 🌐 Website Pages

### Main Pages

1. **Home Page** (`/home` or `/`)
   - Modern SaaS landing page
   - Feature cards grid
   - Navigation to all features
   - File: `templates/home.html`

2. **Brand Generator** (`/brand`)
   - Complete brand identity generator
   - Brand names, taglines, descriptions
   - Logo generation
   - Color palettes
   - Marketing tips
   - File: `templates/index.html` (original main app)

3. **Logo Generator** (`/logo`)
   - AI-powered logo creation
   - Uses Stable Diffusion
   - Download as PNG
   - Accessible from brand page

4. **Marketing Content** (`/marketing`)
   - Social media post generator
   - Multiple platform support
   - Tone customization
   - File: `templates/social-post.html`

5. **Sentiment Analysis** (`/sentiment`)
   - Analyze brand feedback
   - Powered by Hugging Face
   - Accessible from brand page

6. **AI Assistant** (`/assistant`)
   - Chat with branding expert
   - Get strategy advice
   - Accessible from brand page

### New Feature Pages

7. **Brand Score Analyzer** (`/brand-score`)
   - AI-powered brand evaluation
   - Overall score (0-100)
   - Detailed metrics:
     - Memorability
     - Uniqueness
     - Market Fit
   - Copy results feature
   - File: `templates/brand-score.html`

8. **Domain Checker** (`/domain-checker`)
   - Check domain availability
   - Multiple TLD support (.com, .ai, .tech, etc.)
   - Real-time checking (simulated)
   - Registration links
   - File: `templates/domain-checker.html`

9. **Social Media Post Generator** (`/social-post`)
   - Platform-specific content
   - Multiple tones
   - Hashtag suggestions
   - Copy & regenerate features
   - File: `templates/social-post.html`

## 🎨 Design Features

### Shared Styling
- Animated gradient backgrounds
- Glassmorphism effects
- Gradient buttons with hover animations
- Custom scrollbars
- Micro-animations
- Responsive design

### Color Scheme
- Dark theme with vibrant accents
- Blue, purple, cyan gradients
- Emerald for success states
- Rose/pink for alerts

## 🔧 Technical Details

### Backend Routes
```python
/ → home.html
/home → home.html
/brand → index.html
/logo → index.html
/marketing → social-post.html
/sentiment → index.html
/assistant → index.html
/brand-score → brand-score.html
/domain-checker → domain-checker.html
/social-post → social-post.html
```

### API Endpoints (Existing)
- POST `/generate-brand` - Generate brand identity
- POST `/generate-logo` - Generate logo
- POST `/analyze-sentiment` - Analyze sentiment
- POST `/chat-assistant` - Chat with AI

### Static Files
- CSS: `/static/css/styles.css`
- JavaScript: `/static/js/main.js`

## 🚀 Usage

### Starting the Server
```bash
# Set SSL environment variables (Windows PowerShell)
$env:SSL_CERT_FILE="C:\Users\manoj\AppData\Roaming\Python\Python313\site-packages\certifi\cacert.pem"
$env:REQUESTS_CA_BUNDLE="C:\Users\manoj\AppData\Roaming\Python\Python313\site-packages\certifi\cacert.pem"

# Run the application
python app.py
```

Server will be available at: `http://127.0.0.1:5000`

### Navigation
- Start at `/home` for the landing page
- Click feature cards to access different tools
- Use top navigation to switch between pages
- Language selector available on all pages

## ✨ Key Features

### Brand Score
- Mock AI evaluation algorithm
- Animated score circles
- Detailed breakdowns
- Insights generation

### Domain Checker
- Simulated availability checking
- Multiple extension support
- Visual availability indicators
- Registration links

### Social Post Generator
- Platform templates (Instagram, Twitter, LinkedIn, Facebook)
- Tone variations (Professional, Casual, Exciting, Inspiring)
- Hashtag suggestions
- Copy functionality

## 📱 Responsive Design
- Desktop optimized (primary)
- Tablet compatible
- Mobile responsive
- Flexible grid layouts

## 🎯 Future Enhancements
- Real backend integration for new features
- User authentication
- Save/export functionality
- More social media platforms
- Advanced analytics
- Team collaboration features
