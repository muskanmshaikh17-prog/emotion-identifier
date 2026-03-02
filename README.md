# 🎯 Emotion Identifier

Instagram Sentiment Analyzer powered by Google Gemini API

**Created by Muskan Shaikh**

## ✨ Features

- 🔮 Google Gemini AI Sentiment Analysis
- 😊 Emotion Detection (Happy, Angry, Sad, etc.)
- 📊 Real-time Analytics
- 💾 Analysis History
- 🎨 Beautiful Dashboard
- 🌐 Web & Streamlit Interface

## 🚀 Quick Start

### Local Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy .env.example to .env
# Add your Gemini API key

# Run Flask version
python app.py

# OR Run Streamlit version
streamlit run streamlit_app.py
```

### Get Gemini API Key

1. Go to: https://aistudio.google.com/apikey
2. Click: "Get API Key"
3. Create API Key in new project
4. Copy the key

### Setup .env File

1. Copy `.env.example` to `.env`
2. Replace `your_api_key_here` with your actual Gemini API key
3. Keep `.env` file SECRET (never commit it)

## 🛠️ Tech Stack

- **Backend**: Flask, Python
- **AI/ML**: Google Gemini API, Transformers
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Deployment**: Streamlit Cloud

## 📝 Usage

### Web Version (Flask)
```bash
python app.py
# Open: http://localhost:5000
```

### Streamlit Version
```bash
streamlit run streamlit_app.py
```

## 🎯 Analyze Your Content

1. Paste Instagram content (comments, captions, hashtags, etc.)
2. Click "Analyze Now"
3. Get sentiment + emotion + explanation
4. View history and statistics

## 🌐 Live Demo

Visit the live app: https://emotion-identifier-xxx.streamlit.app

## 📂 Project Structure
```
emotion_identifier/
├── app.py                 # Flask backend
├── streamlit_app.py       # Streamlit frontend
├── data_processor.py      # Text preprocessing
├── database.py            # SQLite management
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── static/
│   └── index.html        # Web dashboard
└── README.md             # This file
```

## 🔐 Security

- ⚠️ Never commit `.env` file
- ✅ Use `.env.example` as template
- ✅ Add `.env` to `.gitignore`
- ✅ Keep API keys private

## 📦 Dependencies

See `requirements.txt` for all dependencies:
- Flask
- Transformers
- Google Generative AI
- Python-dotenv
- And more...

## 🚀 Deployment

### Deploy on Streamlit Cloud

1. Push to GitHub
2. Go to: https://streamlit.io/cloud
3. Create new app
4. Connect GitHub repo
5. Select `streamlit_app.py`
6. Add secrets:
   - GOOGLE_API_KEY: your_actual_key
7. Deploy!

## 📊 Sample Results

**Input**: "I absolutely love this amazing product! 😍"

**Output**:
```
Sentiment: Positive (0.95)
Emotion: happy (0.92)
Intensity: High
Explanation: This text shows positive sentiment with enthusiastic language
```

## 🤝 Contributing

Feel free to fork and improve!

## 📄 License

MIT License

## 👤 Author

**Muskan Shaikh**

---

Made with ❤️ using Gemini AI
```