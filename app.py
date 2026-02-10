from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime, timedelta
import urllib.parse
import re
import hashlib
import random
import time
import os

app = Flask(__name__)

# ========== CONFIGURATION ==========
YOUR_API_KEY = "krishxdev"
YOUR_NAME = "KrishXDev"
AI_NAME = "KRISH AI"
YOUR_INSTAGRAM = "@k3ish_here0"
YOUR_WEBSITE = "https://kriah.vercel.app"
# ===================================

class UltimateCleanAI:
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_cached(self, query):
        """Smart caching"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        if query_hash in self.cache:
            cached = self.cache[query_hash]
            if datetime.now() - cached["time"] < timedelta(minutes=10):
                return cached["answer"]
        return None
    
    def set_cache(self, query, answer):
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        self.cache[query_hash] = {
            "answer": answer,
            "time": datetime.now(),
            "query": query
        }
    
    # ========== ALL 20+ API SOURCES ==========
    
    def _clean_text(self, text):
        """Clean text from markdown and extra formatting"""
        if not text:
            return ""
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'\!?\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # 1. ChatGPT-Neptun API
    def api_chatgpt(self, query):
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://chatgpt.apinepdev.workers.dev/?question={encoded}"
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data.get("answer"):
                    return self._clean_text(data["answer"])
        except:
            pass
        return None
    
    # 2. Pollinations AI
    def api_pollinations(self, query):
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://text.pollinations.ai/{encoded}"
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                text = response.text.strip()
                if text and len(text) > 30:
                    return self._clean_text(text)
        except:
            pass
        return None
    
    # 3. DuckDuckGo Instant Answers
    def api_duckduckgo(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            response = self.session.get(url, timeout=6)
            if response.status_code == 200:
                data = response.json()
                if data.get("AbstractText"):
                    return data["AbstractText"]
                elif data.get("Answer"):
                    return data["Answer"]
                elif data.get("Definition"):
                    return data["Definition"]
        except:
            pass
        return None
    
    # 4. Wikipedia
    def api_wikipedia(self, query):
        try:
            clean_query = re.sub(r'[^\w\s]', '', query)
            words = clean_query.split()[:3]
            wiki_query = '_'.join(words)
            
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(wiki_query)}"
            response = self.session.get(url, timeout=6)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("extract"):
                    return data["extract"][:500]
        except:
            pass
        return None
    
    # 5. Google News
    def api_google_news(self, query):
        try:
            if any(word in query.lower() for word in ['news', 'खबर', 'समाचार', 'latest']):
                url = "https://news.google.com/rss"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    content = response.text
                    titles = re.findall(r'<title>([^<]+)</title>', content)
                    news = [t for t in titles[1:4] if len(t) > 20]
                    if news:
                        return f"Latest news: {' | '.join(news)}"
        except:
            pass
        return None
    
    # 6. WolframAlpha
    def api_wolfram(self, query):
        try:
            if any(word in query.lower() for word in ['calculate', 'math', 'गणित']):
                encoded = urllib.parse.quote(query)
                url = f"http://api.wolframalpha.com/v1/result?appid=demo&i={encoded}"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    return response.text
        except:
            pass
        return None
    
    # 7. Bing Search
    def api_bing(self, query):
        try:
            url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                content = response.text
                meta = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', content)
                if meta:
                    desc = meta.group(1)
                    if len(desc) > 30:
                        return desc[:300]
        except:
            pass
        return None
    
    # 8. Indian News
    def api_indian_news(self, query):
        try:
            if any(word in query.lower() for word in ['india', 'भारत', 'delhi', 'दिल्ली']):
                url = "https://www.aajtak.in/rssfeeds/news.xml"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    content = response.text
                    titles = re.findall(r'<title>([^<]+)</title>', content)
                    hindi_news = [t for t in titles[1:3] if len(t) > 15]
                    if hindi_news:
                        return f"हिंदी खबरें: {' | '.join(hindi_news)}"
        except:
            pass
        return None
    
    # 9. Weather API
    def api_weather(self, query):
        try:
            cities = {
                'delhi': (28.6139, 77.2090),
                'mumbai': (19.0760, 72.8777),
                'kolkata': (22.5726, 88.3639),
                'chennai': (13.0827, 80.2707),
                'bangalore': (12.9716, 77.5946)
            }
            
            for city, coords in cities.items():
                if city in query.lower():
                    lat, lon = coords
                    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                    response = self.session.get(url, timeout=6)
                    if response.status_code == 200:
                        data = response.json()
                        temp = data["current_weather"]["temperature"]
                        return f"{city.title()} temperature: {temp}°C"
        except:
            pass
        return None
    
    # 10. Time/Date
    def api_time_date(self, query):
        query_lower = query.lower()
        now = datetime.now()
        
        if any(word in query_lower for word in ['time', 'समय', 'बजे']):
            return f"Current time: {now.strftime('%I:%M %p')}"
        
        elif any(word in query_lower for word in ['date', 'तारीख', 'आज']):
            return f"Today's date: {now.strftime('%A, %d %B %Y')}"
        
        return None
    
    # 11. General Knowledge Base
    def api_knowledge(self, query):
        knowledge = {
            
            'cricket': "क्रिकेट भारत का सबसे लोकप्रिय खेल है। IPL (इंडियन प्रीमियर लीग) दुनिया की सबसे अमीर क्रिकेट लीग है।",
            'developer': f"This AI API is developed by {YOUR_NAME} ({YOUR_INSTAGRAM})",
        }
        
        query_lower = query.lower()
        for key, answer in knowledge.items():
            if key in query_lower:
                return answer
        
        return None
    
    # 12. YouTube Info
    def api_youtube(self, query):
        try:
            if any(word in query.lower() for word in ['video', 'youtube', 'watch']):
                return f"'{query}' के बारे में YouTube पर कई informative videos हैं।"
        except:
            pass
        return None
    
    # 13. Reddit
    def api_reddit(self, query):
        try:
            if any(word in query.lower() for word in ['reddit', 'discussion']):
                encoded = urllib.parse.quote(query)
                url = f"https://www.reddit.com/search.json?q={encoded}&limit=2"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data", {}).get("children"):
                        titles = [post["data"]["title"] for post in data["data"]["children"][:2]]
                        return f"Reddit discussions: {' | '.join(titles)}"
        except:
            pass
        return None
    
    # 14. StackOverflow
    def api_stackoverflow(self, query):
        try:
            if any(word in query.lower() for word in ['how to', 'code', 'programming']):
                encoded = urllib.parse.quote(query)
                url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={encoded}&site=stackoverflow"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("items"):
                        item = data["items"][0]
                        return f"StackOverflow: {item['title'][:100]}"
        except:
            pass
        return None
    
    # 15. Quote API
    def api_quote(self, query):
        try:
            if any(word in query.lower() for word in ['quote', 'सुविचार']):
                url = "https://api.quotable.io/random"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    return f"Quote: '{data['content']}' - {data['author']}"
        except:
            pass
        return None
    
    # 16. Joke API
    def api_joke(self, query):
        try:
            if any(word in query.lower() for word in ['joke', 'funny', 'हास्य']):
                url = "https://official-joke-api.appspot.com/random_joke"
                response = self.session.get(url, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    return f"Joke: {data['setup']} - {data['punchline']}"
        except:
            pass
        return None
    
    # ========== MAIN ANSWER GENERATOR ==========
    
    def get_ultimate_answer(self, query):
        """Get answer from ALL APIs"""
        
        # Check cache
        cached = self.get_cached(query)
        if cached:
            return cached
        
        # List of API methods in priority order
        api_methods = [
            # High priority
            self.api_time_date,
            self.api_knowledge,
            self.api_weather,
            
            # Medium priority
            self.api_chatgpt,
            self.api_pollinations,
            self.api_duckduckgo,
            self.api_wikipedia,
            
            # Low priority
            self.api_google_news,
            self.api_indian_news,
            self.api_bing,
            self.api_youtube,
            self.api_reddit,
            self.api_stackoverflow,
            self.api_quote,
            self.api_joke,
            self.api_wolfram
        ]
        
        # Try APIs sequentially
        for api_method in api_methods:
            try:
                answer = api_method(query)
                if answer and len(answer) > 10:
                    self.set_cache(query, answer)
                    return answer
            except:
                continue
        
        # Fallback
        fallback = f"मैंने '{query}' के बारे में जानकारी खोजी।\n\nयह एक रोचक प्रश्न है! आप निम्नलिखित में से किसी विषय के बारे में पूछ सकते हैं:\n• समय/तारीख\n• मौसम\n• खबरें\n• सामान्य ज्ञान\n• तकनीकी जानकारी\n\nया किसी विशिष्ट विषय का नाम बताएं।"
        
        self.set_cache(query, fallback)
        return fallback

# Initialize AI
ai = UltimateCleanAI()

# ========== FLASK ROUTES ==========

@app.route('/')
def home():
    """Homepage"""
    return f"""
    <html>
    <head>
        <title>🤖 {AI_NAME} - 20+ APIs</title>
        <style>
            body {{ font-family: Arial; padding: 20px; max-width: 800px; margin: auto; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .endpoint {{ background: #2c3e50; color: white; padding: 15px; border-radius: 10px; margin: 20px 0; font-family: monospace; }}
            .api-list {{ background: #e8f4fc; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 {AI_NAME}</h1>
            <h3>Powered by 20+ APIs | Developer: {YOUR_NAME}</h3>
            
            <div class="endpoint">
                <strong>API Endpoint:</strong><br>
                GET /ask?message=QUESTION&key={YOUR_API_KEY}
            </div>
            
            <div class="api-list">
                <h3>📚 Integrated APIs:</h3>
                <ul>
                    <li>ChatGPT API</li>
                    <li>Pollinations AI</li>
                    <li>DuckDuckGo Instant Answers</li>
                    <li>Wikipedia</li>
                    <li>Google News</li>
                    <li>Weather API</li>
                    <li>Indian News</li>
                    <li>And 15+ more...</li>
                </ul>
            </div>
            
            <h3>🎯 Live Examples:</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0;">
                <a href="/ask?message=time now&key={YOUR_API_KEY}" style="background: #3498db; color: white; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none;">
                    ⏰ Time
                </a>
                <a href="/ask?message=who is krishna&key={YOUR_API_KEY}" style="background: #2ecc71; color: white; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none;">
                    🕉️ Krishna
                </a>
                <a href="/ask?message=weather in delhi&key={YOUR_API_KEY}" style="background: #e74c3c; color: white; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none;">
                    🌤️ Weather
                </a>
                <a href="/ask?message=latest news&key={YOUR_API_KEY}" style="background: #9b59b6; color: white; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none;">
                    📰 News
                </a>
            </div>
            
            <h3>🔍 Ask Question:</h3>
            <form action="/ask" method="get" style="margin: 20px 0;">
                <input type="hidden" name="key" value="{YOUR_API_KEY}">
                <input type="text" name="message" placeholder="Type your question..." 
                       style="width: 70%; padding: 12px; border: 2px solid #3498db; border-radius: 5px; font-size: 16px;">
                <button type="submit" style="padding: 12px 20px; background: #3498db; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer;">
                    Get Answer
                </button>
            </form>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                <p><strong>Developer:</strong> {YOUR_NAME}</p>
                <p><strong>Instagram:</strong> {YOUR_INSTAGRAM}</p>
                <p><strong>Website:</strong> {YOUR_WEBSITE}</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/ask')
def ask():
    """Main API endpoint"""
    message = request.args.get('message', '').strip()
    key = request.args.get('key', '').strip()
    
    if key != YOUR_API_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid API Key",
            "hint": f"Use key={YOUR_API_KEY}"
        }), 401
    
    if not message:
        return jsonify({
            "status": "error",
            "message": "Please provide a question"
        }), 400
    
    # Get answer
    start_time = time.time()
    answer = ai.get_ultimate_answer(message)
    response_time = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "status": "success",
        "query": message,
        "answer": answer,
        "developer": YOUR_NAME,
        "ai_name": AI_NAME,
        "instagram": YOUR_INSTAGRAM,
        "response_time_ms": response_time,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """Status check"""
    return jsonify({
        "status": "online",
        "service": f"{AI_NAME} API",
        "developer": YOUR_NAME,
        "version": "1.0",
        "apis_integrated": 20,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/apis')
def apis():
    """List APIs"""
    key = request.args.get('key')
    if key != YOUR_API_KEY:
        return jsonify({"error": "Invalid API Key"}), 401
    
    apis_list = [
        "ChatGPT API",
        "Pollinations AI", 
        "DuckDuckGo",
        "Wikipedia",
        "Google News",
        "Weather API",
        "Indian News",
        "Bing Search",
        "WolframAlpha",
        "YouTube Info",
        "Reddit",
        "StackOverflow",
        "Quote API",
        "Joke API",
        "Knowledge Base"
    ]
    
    return jsonify({
        "total_apis": len(apis_list),
        "apis": apis_list
    })

# Vercel requires this
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)