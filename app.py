"""
Emotion Identifier - Instagram Sentiment Analyzer with Google Gemini
Flask Backend API
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from transformers import pipeline
import json
from datetime import datetime
from dotenv import load_dotenv
import os
from data_processor import preprocess_text
from database import init_db, save_sentiment, get_history, clear_history

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

# Get API key from .env
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully!")
    USE_GEMINI = True
else:
    print("⚠️  Gemini API key not found in .env")
    USE_GEMINI = False

# Initialize database
init_db()

# Load pre-trained models
print("Loading sentiment analysis models...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
print("✓ Models loaded successfully!")

# GEMINI ANALYSIS FUNCTION
def analyze_with_gemini(text):
    """Use Gemini AI to analyze sentiment"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Analyze sentiment and emotion of this text:
        
Text: "{text}"

Respond ONLY in JSON format (no markdown, no extra text):
{{
    "sentiment": "Positive/Negative/Neutral",
    "sentiment_score": 0.85,
    "confidence": 0.95,
    "emotion": "happy/angry/sad/excited/fearful/surprised/disgusted/neutral",
    "emotion_confidence": 0.88,
    "intensity": "Low/Medium/High",
    "explanation": "Why this sentiment was detected"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        json_str = result_text[json_start:json_end]
        result = json.loads(json_str)
        return result
    except Exception as e:
        print(f"Gemini error: {str(e)}")
        return None

# TRANSFORMER ANALYSIS FUNCTION
def analyze_with_transformers(text):
    """Fallback sentiment analysis using transformers"""
    try:
        sentiment_result = sentiment_pipeline(text[:512])[0]
        sentiment_label = sentiment_result['label']
        sentiment_score = sentiment_result['score']
        
        if sentiment_label == 'POSITIVE':
            normalized_score = sentiment_score
            emotional_tone = 'Positive'
        else:
            normalized_score = -sentiment_score
            emotional_tone = 'Negative'
        
        try:
            emotion_result = emotion_pipeline(text[:512])[0]
            emotion_label = emotion_result['label'].capitalize()
            emotion_confidence = emotion_result['score']
        except:
            emotion_label = 'Neutral'
            emotion_confidence = 0.5
        
        return {
            'sentiment': emotional_tone,
            'sentiment_score': normalized_score,
            'confidence': sentiment_score,
            'emotion': emotion_label,
            'emotion_confidence': emotion_confidence,
            'intensity': 'High' if abs(normalized_score) > 0.7 else 'Medium' if abs(normalized_score) > 0.4 else 'Low',
            'explanation': f"This text shows {emotional_tone.lower()} sentiment.",
        }
    except Exception as e:
        print(f"Transformer error: {str(e)}")
        return None

# ROUTES
@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment using Gemini or Transformers"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        content_type = data.get('content_type', 'comment')
        use_gemini = data.get('use_gemini', USE_GEMINI)
        
        if not text:
            return jsonify({'error': 'Text input is required'}), 400
        
        cleaned_text = preprocess_text(text)
        
        # TRY GEMINI FIRST
        if use_gemini and USE_GEMINI:
            print("Using Gemini API...")
            gemini_result = analyze_with_gemini(cleaned_text[:1000])
            
            if gemini_result:
                analysis_result = gemini_result
                model_used = "gemini"
            else:
                print("Gemini failed, falling back to transformers...")
                analysis_result = analyze_with_transformers(cleaned_text)
                model_used = "transformers (fallback)"
        else:
            print("Using Transformer models...")
            analysis_result = analyze_with_transformers(cleaned_text)
            model_used = "transformers"
        
        if analysis_result is None:
            return jsonify({'error': 'Analysis failed'}), 500
        
        # Prepare response
        response = {
            'original_text': text,
            'cleaned_text': cleaned_text,
            'sentiment': analysis_result.get('sentiment', 'Neutral'),
            'sentiment_score': float(analysis_result.get('sentiment_score', 0)),
            'confidence': float(analysis_result.get('confidence', 0)),
            'emotion': analysis_result.get('emotion', 'Neutral'),
            'emotion_confidence': float(analysis_result.get('emotion_confidence', 0)),
            'content_type': content_type,
            'timestamp': datetime.now().isoformat(),
            'explanation': analysis_result.get('explanation', ''),
            'intensity': analysis_result.get('intensity', 'Medium'),
            'model_used': model_used,
            'analysis_details': {
                'positive_indicators': count_positive_words(cleaned_text),
                'negative_indicators': count_negative_words(cleaned_text),
                'intensity': analysis_result.get('intensity', 'Medium')
            }
        }
        
        # Save to database
        save_sentiment(response)
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple texts at once"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Texts list is required'}), 400
        
        results = []
        for text in texts[:20]:
            cleaned_text = preprocess_text(text)
            analysis_result = analyze_with_transformers(cleaned_text)
            
            if analysis_result:
                results.append({
                    'text': text[:100],
                    'sentiment': analysis_result.get('sentiment', 'Neutral'),
                    'sentiment_score': float(analysis_result.get('sentiment_score', 0)),
                    'confidence': float(analysis_result.get('confidence', 0)),
                    'emotion': analysis_result.get('emotion', 'Neutral')
                })
        
        total = len(results)
        positive_count = sum(1 for r in results if r['sentiment'] == 'Positive')
        negative_count = sum(1 for r in results if r['sentiment'] == 'Negative')
        avg_score = sum(r['sentiment_score'] for r in results) / total if total > 0 else 0
        
        return jsonify({
            'results': results,
            'statistics': {
                'total_texts': total,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'positive_percentage': round((positive_count / total * 100), 2) if total > 0 else 0,
                'negative_percentage': round((negative_count / total * 100), 2) if total > 0 else 0,
                'average_sentiment_score': round(avg_score, 3)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_sentiment_history():
    """Get analysis history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_history(limit)
        return jsonify({'history': history, 'count': len(history)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get sentiment statistics"""
    try:
        history = get_history(1000)
        
        if not history:
            return jsonify({
                'total_analyses': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'average_confidence': 0,
                'top_emotions': [],
                'api_status': 'Gemini' if USE_GEMINI else 'Transformers'
            }), 200
        
        total = len(history)
        positive_count = sum(1 for item in history if item['sentiment'] == 'Positive')
        negative_count = sum(1 for item in history if item['sentiment'] == 'Negative')
        neutral_count = total - positive_count - negative_count
        
        emotions = {}
        for item in history:
            emotion = item.get('emotion', 'Unknown')
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:5]
        avg_confidence = sum(float(item.get('confidence', 0)) for item in history) / total if total > 0 else 0
        
        return jsonify({
            'total_analyses': total,
            'positive_percentage': round((positive_count / total * 100), 2),
            'negative_percentage': round((negative_count / total * 100), 2),
            'neutral_percentage': round((neutral_count / total * 100), 2),
            'average_confidence': round(avg_confidence, 3),
            'top_emotions': [{'emotion': e[0], 'count': e[1]} for e in top_emotions],
            'api_status': 'Gemini' if USE_GEMINI else 'Transformers'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_sentiment_history():
    """Clear all history"""
    try:
        clear_history()
        return jsonify({'message': 'History cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Emotion Identifier',
        'gemini_available': USE_GEMINI
    }), 200

def count_positive_words(text):
    """Count positive sentiment indicators"""
    positive_words = ['good', 'great', 'amazing', 'excellent', 'wonderful', 'fantastic', 
                     'awesome', 'love', 'best', 'perfect', 'beautiful', 'happy', 'glad']
    return sum(1 for word in positive_words if word in text.lower())

def count_negative_words(text):
    """Count negative sentiment indicators"""
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'poor', 
                     'useless', 'angry', 'sad', 'disappointed', 'disgusting', 'ugly']
    return sum(1 for word in negative_words if word in text.lower())

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎯 EMOTION IDENTIFIER - Sentiment Analyzer")
    print("="*60)
    print("📊 Starting server...")
    
    if USE_GEMINI:
        print("🔮 Using: Google Gemini API (Advanced)")
    else:
        print("🤖 Using: Transformer Models (Fallback)")
    
    print("🌐 Open: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)