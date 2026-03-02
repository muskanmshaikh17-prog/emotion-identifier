import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from data_processor import preprocess_text
from database import init_db, get_history, get_statistics
import json

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize
init_db()

# PAGE SETUP
st.set_page_config(
    page_title="Emotion Identifier",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TITLE
st.markdown("# 🎯 Emotion Identifier")
st.markdown("**Created by Muskan Shaikh**")
st.markdown("Analyze Instagram content sentiment with AI")
st.divider()

# SIDEBAR
with st.sidebar:
    st.header("About")
    st.write("Powered by Google Gemini API")
    st.write("Analyze sentiment and emotions in text")

# MAIN CONTENT
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Analyze Text")
    
    # Input
    text_input = st.text_area("Paste Instagram content here:", height=150)
    content_type = st.selectbox("Content Type:", 
        ["comment", "caption", "hashtag", "review", "reply", "mention"])
    
    # Analyze button
    if st.button("🔮 Analyze Now", use_container_width=True):
        if text_input.strip():
            with st.spinner("Analyzing with Gemini..."):
                try:
                    # Preprocess
                    cleaned_text = preprocess_text(text_input)
                    
                    # Use Gemini
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"""Analyze sentiment and emotion of: "{cleaned_text}"
                    
Respond ONLY in JSON:
{{
    "sentiment": "Positive/Negative/Neutral",
    "sentiment_score": 0.85,
    "confidence": 0.95,
    "emotion": "happy/angry/sad/excited/fearful/surprised/disgusted/neutral",
    "emotion_confidence": 0.88,
    "intensity": "Low/Medium/High",
    "explanation": "Brief explanation"
}}"""
                    
                    response = model.generate_content(prompt)
                    result_text = response.text.strip()
                    
                    # Extract JSON
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    json_str = result_text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        sentiment = result.get('sentiment', 'Neutral')
                        st.metric("Sentiment", sentiment, 
                                 delta=f"{result.get('sentiment_score', 0):.2f}")
                    with col_b:
                        st.metric("Emotion", result.get('emotion', 'Unknown'),
                                 delta=f"{result.get('emotion_confidence', 0):.2%}")
                    with col_c:
                        st.metric("Intensity", result.get('intensity', 'Medium'))
                    
                    st.info(f"**Explanation:** {result.get('explanation', 'N/A')}")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter some text!")

with col2:
    st.subheader("📊 Statistics")
    
    if st.button("Refresh Stats"):
        stats = get_statistics()
        
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("Total Analyses", stats.get('total_analyses', 0))
        with col_y:
            st.metric("Positive %", f"{stats.get('positive_percentage', 0):.1f}%")
        with col_z:
            st.metric("Negative %", f"{stats.get('negative_percentage', 0):.1f}%")
        
        # Chart
        if stats.get('total_analyses', 0) > 0:
            import pandas as pd
            data = {
                'Sentiment': ['Positive', 'Negative', 'Neutral'],
                'Count': [
                    int(stats.get('positive_percentage', 0) * stats.get('total_analyses', 0) / 100),
                    int(stats.get('negative_percentage', 0) * stats.get('total_analyses', 0) / 100),
                    int(stats.get('neutral_percentage', 0) * stats.get('total_analyses', 0) / 100)
                ]
            }
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index('Sentiment'))

# HISTORY TAB
st.divider()
if st.checkbox("📜 Show History"):
    history = get_history(10)
    if history:
        for item in history:
            with st.expander(f"📌 {item['original_text'][:50]}..."):
                st.write(f"**Sentiment:** {item['sentiment']}")
                st.write(f"**Emotion:** {item['emotion']}")
                st.write(f"**Score:** {item['sentiment_score']:.2f}")
                st.write(f"**Time:** {item['created_at']}")
    else:
        st.info("No history yet")