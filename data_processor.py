"""
Data Processor - Text preprocessing and emotion extraction
"""

import re
import string
from collections import Counter

# Emoji to text mapping
EMOJI_DICT = {
    '😀': 'happy', '😃': 'happy', '😄': 'happy', '😁': 'happy',
    '😆': 'happy', '😅': 'happy', '🤣': 'happy', '😂': 'happy',
    '😊': 'happy', '😇': 'happy', '🙂': 'happy', '🙃': 'happy',
    '😉': 'happy', '😌': 'happy', '😍': 'love', '🥰': 'love',
    '😘': 'love', '😗': 'love', '😚': 'love', '😙': 'love',
    '🥲': 'happy', '😋': 'happy', '😛': 'happy', '😜': 'happy',
    '🤪': 'happy', '😌': 'calm', '🤑': 'happy', '🤗': 'happy',
    '🤩': 'excited', '🤨': 'confused', '😐': 'neutral', '😑': 'neutral',
    '😶': 'shy', '😏': 'sarcasm', '😣': 'pain', '😥': 'sad',
    '😮': 'surprised', '🤐': 'silent', '😯': 'surprised', '😲': 'surprised',
    '😭': 'sad', '😤': 'angry', '😠': 'angry', '😡': 'angry',
    '🤬': 'angry', '😈': 'evil', '👿': 'evil', '💀': 'dead',
    '☠️': 'dead', '💩': 'disgusting', '🤮': 'disgusting', '🤧': 'sick',
    '🤒': 'sick', '🤕': 'pain', '🤑': 'greedy', '😈': 'evil',
    '❤️': 'love', '🧡': 'love', '💛': 'happy', '💚': 'love',
    '💙': 'calm', '💜': 'love', '🖤': 'dark', '🤍': 'pure',
    '🔥': 'hot', '👍': 'good', '👎': 'bad', '💯': 'perfect',
    '✨': 'magic', '🎉': 'celebration', '🎊': 'celebration', '🎈': 'celebration',
}

STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
    'the', 'to', 'was', 'will', 'with', 'the', 'this', 'but', 'not',
    'have', 'i', 'you', 'we', 'they', 'them', 'your', 'what', 'which',
    'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
}

EMOTION_KEYWORDS = {
    'happy': ['happy', 'glad', 'joy', 'delighted', 'thrilled', 'excited', 'wonderful', 'great', 'amazing', 'awesome', 'fantastic', 'good'],
    'sad': ['sad', 'unhappy', 'depressed', 'miserable', 'sorrowful', 'grief', 'down', 'disappointed', 'upset', 'blue'],
    'angry': ['angry', 'furious', 'enraged', 'mad', 'irritated', 'annoyed', 'livid', 'hateful', 'rage'],
    'fear': ['afraid', 'scared', 'terrified', 'frightened', 'anxious', 'nervous', 'worried', 'concerned'],
    'love': ['love', 'adore', 'care', 'affection', 'passionate', 'devoted', 'cherish'],
    'excited': ['excited', 'thrilled', 'eager', 'anticipating', 'enthusiastic', 'pumped'],
    'neutral': ['okay', 'alright', 'fine', 'whatever', 'meh', 'so-so'],
}

def convert_emojis(text):
    """Convert emojis to their textual representation"""
    for emoji, meaning in EMOJI_DICT.items():
        text = text.replace(emoji, f" {meaning} ")
    return text

def remove_urls(text):
    """Remove URLs from text"""
    return re.sub(r'http\S+|www.\S+', '', text)

def remove_mentions(text):
    """Remove @ mentions but keep the context"""
    return re.sub(r'@\w+', '', text)

def remove_hashtags_but_keep_words(text):
    """Remove # but keep the words"""
    return re.sub(r'#', '', text)

def remove_special_characters(text):
    """Remove special characters but keep spaces"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def normalize_repeated_chars(text):
    """Normalize repeated characters (e.g., 'hellooo' -> 'hello')"""
    return re.sub(r'(.)\1{2,}', r'\1', text)

def remove_stopwords(text):
    """Remove common stopwords"""
    words = text.split()
    filtered = [word for word in words if word.lower() not in STOP_WORDS]
    return ' '.join(filtered)

def preprocess_text(text):
    """
    Complete text preprocessing pipeline
    Steps:
    1. Convert emojis to text
    2. Remove URLs
    3. Remove mentions
    4. Remove hashtag symbols
    5. Lowercase
    6. Normalize repeated characters
    7. Remove special characters
    8. Remove extra whitespace
    """
    # Step 1: Convert emojis
    text = convert_emojis(text)
    
    # Step 2: Remove URLs
    text = remove_urls(text)
    
    # Step 3: Remove mentions
    text = remove_mentions(text)
    
    # Step 4: Remove hashtag symbols
    text = remove_hashtags_but_keep_words(text)
    
    # Step 5: Lowercase
    text = text.lower()
    
    # Step 6: Normalize repeated characters
    text = normalize_repeated_chars(text)
    
    # Step 7: Remove special characters (but keep spaces)
    text = remove_special_characters(text)
    
    # Step 8: Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def extract_emotions(text, sentiment_label, sentiment_score):
    """
    Extract detailed emotions from text
    Returns: primary emotion and confidence
    """
    text_lower = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        emotion_scores[emotion] = score
    
    # If no keywords found, use sentiment
    if max(emotion_scores.values()) == 0:
        if sentiment_label == 'POSITIVE':
            return 'happy' if sentiment_score > 0.8 else 'content'
        else:
            return 'sad' if sentiment_score > 0.5 else 'neutral'
    
    # Return most common emotion
    primary_emotion = max(emotion_scores, key=emotion_scores.get)
    return primary_emotion

def get_top_words(text, n=5):
    """
    Get most frequent words
    """
    words = text.lower().split()
    word_freq = Counter(words)
    return word_freq.most_common(n)

def analyze_sentiment_intensity(text, sentiment_score):
    """
    Determine intensity of sentiment
    """
    abs_score = abs(sentiment_score)
    if abs_score > 0.85:
        return 'Very High'
    elif abs_score > 0.70:
        return 'High'
    elif abs_score > 0.50:
        return 'Medium'
    else:
        return 'Low'

def extract_keywords(text, n=10):
    """
    Extract top keywords from text
    """
    words = text.lower().split()
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 3]
    word_freq = Counter(filtered_words)
    return [word for word, _ in word_freq.most_common(n)]

# Example usage
if __name__ == "__main__":
    test_text = "I absolutely LOVE this product!!! 😍😍 It's the BEST thing ever! #amazing #awesome"
    print(f"Original: {test_text}")
    print(f"Cleaned: {preprocess_text(test_text)}")
    print(f"Keywords: {extract_keywords(test_text)}")
