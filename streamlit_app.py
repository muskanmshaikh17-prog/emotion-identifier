"""
Emotion Identifier - Streamlit App (Lightweight - Gemini Only)
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
else:
    GEMINI_AVAILABLE = False

# PAGE CONFIG
st.set_page_config(
    page_title="Emotion Identifier",
    page_icon="🎯",
    layout="wide",
)

# TITLE
st.markdown("""
<div style="text-align: center;">
    <h1>🎯 Emotion Identifier</h1>
    <p style="font-size: 0.9rem; color: gray;">Created by Muskan Shaikh</p>
    <p>Analyze Instagram content sentiment with Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# SIDEBAR
with st.sidebar:
    st.header("ℹ️ About")
    st.write("**Powered by Google Gemini API**")
    st.write("Analyze sentiment and emotions instantly!")
    st.write("- Comments")
    st.write("- Captions")
    st.write("- Hashtags")
    st.write("- Reviews")
    st.write("- Replies")
    st.write("- Mentions")
    
    st.divider()
    
    if GEMINI_AVAILABLE:
        st.success("✅ Gemini API Connected")
    else:
        st.error("⚠️ Gemini API Not Available")

# MAIN CONTENT
col1, col2 = st.columns([1, 1])

# LEFT COLUMN - ANALYZER
with col1:
    st.subheader("📝 Analyze Text")
    
    # Text input
    text_input = st.text_area(
        "Paste Instagram content here:",
        height=150,
        placeholder="E.g., 'I absolutely love this amazing product! 😍'"
    )
    
    # Content type selector
    content_type = st.selectbox(
        "Content Type:",
        ["comment", "caption", "hashtag", "review", "reply", "mention"]
    )
    
    # Analyze button
    if st.button("🔮 Analyze Now", use_container_width=True, type="primary"):
        if text_input.strip():
            with st.spinner("🔄 Analyzing with Gemini..."):
                try:
                    if GEMINI_AVAILABLE:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        prompt = f"""Analyze sentiment and emotion of this Instagram text:
                        
Text: "{text_input}"

Respond ONLY in valid JSON format (no markdown, no extra text):
{{
    "sentiment": "Positive",
    "sentiment_score": 0.85,
    "confidence": 0.95,
    "emotion": "happy",
    "emotion_confidence": 0.88,
    "intensity": "High",
    "explanation": "Brief explanation of why this sentiment was detected"
}}

IMPORTANT: Return ONLY valid JSON, nothing else."""
                        
                        response = model.generate_content(prompt)
                        result_text = response.text.strip()
                        
                        # Extract JSON
                        json_start = result_text.find('{')
                        json_end = result_text.rfind('}') + 1
                        
                        if json_start == -1 or json_end == 0:
                            st.error("Could not parse response")
                        else:
                            json_str = result_text[json_start:json_end]
                            result = json.loads(json_str)
                            
                            # Display results
                            st.success("✅ Analysis Complete!")
                            
                            # Metrics
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                sentiment = result.get('sentiment', 'Neutral')
                                sentiment_color = "🟢" if sentiment == "Positive" else "🔴" if sentiment == "Negative" else "⚪"
                                st.metric(
                                    f"{sentiment_color} Sentiment", 
                                    sentiment, 
                                    delta=f"{result.get('sentiment_score', 0):.2f}"
                                )
                            with col_b:
                                st.metric(
                                    f"😊 Emotion", 
                                    result.get('emotion', 'Unknown').capitalize(),
                                    delta=f"{result.get('emotion_confidence', 0):.0%}"
                                )
                            with col_c:
                                st.metric("⚡ Intensity", result.get('intensity', 'Medium'))
                            
                            # Explanation
                            st.info(f"**💡 Explanation:** {result.get('explanation', 'N/A')}")
                            
                            # Store in session
                            if 'analysis_history' not in st.session_state:
                                st.session_state.analysis_history = []
                            
                            st.session_state.analysis_history.append({
                                'text': text_input,
                                'sentiment': sentiment,
                                'emotion': result.get('emotion', 'Unknown'),
                                'score': result.get('sentiment_score', 0),
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    
                    else:
                        st.error("❌ Gemini API not configured")
                
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing response: {str(e)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter some text!")

# RIGHT COLUMN - STATS & HISTORY
with col2:
    st.subheader("📊 Quick Stats")
    
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    history = st.session_state.analysis_history
    
    if history:
        total = len(history)
        positive = sum(1 for h in history if h['sentiment'] == 'Positive')
        negative = sum(1 for h in history if h['sentiment'] == 'Negative')
        neutral = total - positive - negative
        
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("📈 Total", total)
        with col_y:
            st.metric("😊 Positive", positive)
        with col_z:
            st.metric("😞 Negative", negative)
        
        # Chart
        if total > 0:
            st.write("**Sentiment Distribution:**")
            data = {
                'Positive': positive,
                'Negative': negative,
                'Neutral': neutral
            }
            st.bar_chart(data)
    else:
        st.info("No analyses yet. Analyze some text to see stats!")

# HISTORY SECTION
st.divider()

st.subheader("📜 Analysis History")

if st.session_state.analysis_history:
    if st.button("📂 Show History", use_container_width=True):
        for idx, item in enumerate(st.session_state.analysis_history[::-1], 1):
            with st.expander(f"#{idx} - {item['text'][:60]}..."):
                col_h1, col_h2, col_h3 = st.columns(3)
                
                with col_h1:
                    st.metric("Sentiment", item['sentiment'])
                
                with col_h2:
                    st.metric("Emotion", item['emotion'].capitalize())
                
                with col_h3:
                    st.metric("Score", f"{item['score']:.2f}")
                
                st.write(f"**Time:** {item['time']}")
                st.write(f"**Text:** {item['text']}")
else:
    st.info("No history yet. Analyze some text first!")

# FOOTER
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.85rem;">
    <p>🎯 Emotion Identifier | Created by Muskan Shaikh</p>
    <p>Powered by Google Gemini API & Streamlit</p>
</div>
""", unsafe_allow_html=True)