"""
Database Management - SQLite for storing sentiment analysis results
"""

import sqlite3
import json
from datetime import datetime
import os

DATABASE_NAME = 'emotion_identifier.db'

def get_db_path():
    """Get database file path"""
    return DATABASE_NAME

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Create sentiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            cleaned_text TEXT,
            sentiment VARCHAR(20),
            sentiment_score REAL,
            confidence REAL,
            emotion VARCHAR(50),
            emotion_confidence REAL,
            content_type VARCHAR(50),
            intensity VARCHAR(20),
            positive_indicators INTEGER,
            negative_indicators INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME
        )
    ''')
    
    # Create statistics table for caching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name VARCHAR(100),
            metric_value REAL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sentiment ON sentiments(sentiment)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emotion ON sentiments(emotion)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON sentiments(timestamp)')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def save_sentiment(data):
    """
    Save sentiment analysis result to database
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        analysis = data.get('analysis_details', {})
        
        cursor.execute('''
            INSERT INTO sentiments (
                original_text,
                cleaned_text,
                sentiment,
                sentiment_score,
                confidence,
                emotion,
                emotion_confidence,
                content_type,
                intensity,
                positive_indicators,
                negative_indicators,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('original_text'),
            data.get('cleaned_text'),
            data.get('sentiment'),
            data.get('sentiment_score'),
            data.get('confidence'),
            data.get('emotion'),
            data.get('emotion_confidence'),
            data.get('content_type'),
            analysis.get('intensity'),
            analysis.get('positive_indicators'),
            analysis.get('negative_indicators'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        print(f"✓ Sentiment saved: {data.get('sentiment')}")
        return True
    
    except Exception as e:
        print(f"Error saving sentiment: {str(e)}")
        return False

def get_history(limit=50):
    """
    Get sentiment analysis history
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id, original_text, sentiment, sentiment_score, confidence,
                emotion, emotion_confidence, content_type, intensity,
                positive_indicators, negative_indicators, created_at
            FROM sentiments
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'original_text': row[1],
                'sentiment': row[2],
                'sentiment_score': row[3],
                'confidence': row[4],
                'emotion': row[5],
                'emotion_confidence': row[6],
                'content_type': row[7],
                'intensity': row[8],
                'positive_indicators': row[9],
                'negative_indicators': row[10],
                'created_at': row[11]
            })
        
        return results
    
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return []

def get_statistics():
    """
    Get overall statistics
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM sentiments')
        total = cursor.fetchone()[0]
        
        # Sentiment distribution
        cursor.execute('SELECT sentiment, COUNT(*) FROM sentiments GROUP BY sentiment')
        sentiment_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Emotion distribution
        cursor.execute('SELECT emotion, COUNT(*) FROM sentiments GROUP BY emotion ORDER BY COUNT(*) DESC LIMIT 5')
        emotion_dist = [{'emotion': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) FROM sentiments')
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Average sentiment score
        cursor.execute('SELECT AVG(sentiment_score) FROM sentiments')
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        positive_count = sentiment_dist.get('Positive', 0)
        negative_count = sentiment_dist.get('Negative', 0)
        neutral_count = total - positive_count - negative_count
        
        return {
            'total_analyses': total,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': (positive_count / total * 100) if total > 0 else 0,
            'negative_percentage': (negative_count / total * 100) if total > 0 else 0,
            'neutral_percentage': (neutral_count / total * 100) if total > 0 else 0,
            'average_confidence': round(avg_confidence, 3),
            'average_sentiment_score': round(avg_score, 3),
            'top_emotions': emotion_dist
        }
    
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        return {}

def clear_history():
    """
    Delete all analysis history
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sentiments')
        conn.commit()
        conn.close()
        print("✓ History cleared")
        return True
    
    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        return False

def get_by_content_type(content_type, limit=50):
    """
    Get sentiments filtered by content type
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id, original_text, sentiment, sentiment_score, confidence,
                emotion, created_at
            FROM sentiments
            WHERE content_type = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (content_type, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'text': row[1],
                'sentiment': row[2],
                'score': row[3],
                'confidence': row[4],
                'emotion': row[5],
                'timestamp': row[6]
            })
        
        return results
    
    except Exception as e:
        print(f"Error getting by content type: {str(e)}")
        return []

def export_data(format='json'):
    """
    Export all data to JSON or CSV
    """
    try:
        history = get_history(10000)
        
        if format == 'json':
            return json.dumps(history, indent=2)
        
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if history:
                fieldnames = history[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(history)
            
            return output.getvalue()
    
    except Exception as e:
        print(f"Error exporting data: {str(e)}")
        return None

if __name__ == "__main__":
    # Initialize database on first run
    init_db()
    print("Database setup complete!")
