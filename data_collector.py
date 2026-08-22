import requests
import json
import os
import csv
import re
import time
import dotenv
from google_play_scraper import Sort, reviews

dotenv.load_dotenv()

# Configurations
KEYWORDS = [
    "wishlist", "saved", "save for later", "liked", "favourites", "bookmark", "shortlisted", "want to buy", 
    "didn't buy", "couldn't buy", "not bought", "holding off", "waiting", "out of stock", "size not available", 
    "expensive", "too costly", "not sure", "confused", "can't decide", "on the fence", "size confusion", 
    "will it fit", "looks different", "different in real", "color different", "fabric", "material", "looks cheap", 
    "will buy later", "next month", "after salary", "payday", "waiting for sale", "budget", "someday", 
    "planning to buy", "maybe later", "compared", "comparing", "better option", "checking other sites", 
    "similar product", "alternatives", "YouTube review", "searched on YouTube", "Instagram", "looked up", 
    "size chart", "asked friend", "influencer", "googled", "fit", "fitting", "true to size", "runs small", 
    "runs large", "body type", "petite", "plus size", "how to style", "outfit idea", "occasion", "styling", 
    "friend suggested", "trending", "gifted", "birthday", "party", "wedding", "wish they had", "would have bought", 
    "missing feature", "no review", "no size guide", "can't filter", "wish Myntra had", "why doesn't Myntra", 
    "Myntra should", "missing on Myntra", "no option to", "if only", "would have bought if", "feature request", 
    "please add", "Myntra needs to", "still no", "why can't I", "not possible on Myntra"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Heuristics for Research Questions mapping
RQ_KEYWORDS = {
    1: ["wishlist", "saved", "save for later", "liked", "favourites", "bookmark", "shortlisted", "want to buy"],
    2: ["didn't buy", "couldn't buy", "not bought", "out of stock", "expensive", "too costly", "confused", "can't decide", "on the fence"],
    3: ["not sure", "confused", "can't decide", "on the fence", "size confusion", "will it fit", "looks different", "different in real", "color different", "fabric", "material", "looks cheap"],
    4: ["holding off", "waiting", "will buy later", "next month", "after salary", "payday", "waiting for sale", "budget", "someday", "planning to buy", "maybe later"],
    5: ["compared", "comparing", "better option", "checking other sites", "similar product", "alternatives"],
    6: ["YouTube review", "searched on YouTube", "Instagram", "looked up", "googled"],
    7: ["size chart", "fit", "fitting", "true to size", "runs small", "runs large", "body type", "petite", "plus size", "how to style", "outfit idea", "occasion", "styling", "friend suggested", "trending", "gifted", "birthday", "party", "wedding"],
    8: ["wishlist", "bookmark", "save for later", "planning to buy", "would have bought"],
    9: ["plus size", "student", "budget", "gift", "birthday", "first time"],
    10: ["wish they had", "would have bought", "missing feature", "no review", "no size guide", "can't filter", "wish Myntra had", "why doesn't Myntra", "Myntra should", "missing on Myntra", "no option to", "if only", "would have bought if", "feature request", "please add", "Myntra needs to", "still no", "why can't I", "not possible on Myntra"]
}

def clean_text(text):
    # Replace newlines/tabs with space to maintain clean markdown table rows
    return text.replace("\n", " ").replace("\r", " ").replace("|", "\\|").strip()

def matches_quality_rules(text):
    # Rule: Must mention Myntra or refer to Myntra app (this is true since App Store/Play Store is for Myntra app)
    # Rule: Contains only emojis with no meaningful text
    text_no_emojis = re.sub(r'[^\w\s,.:;!?\'"-]', '', text).strip()
    if not text_no_emojis:
        return False
    # Rule: Is 3 words or fewer
    words = text.split()
    if len(words) <= 3:
        return False
    # Rule: Is a rating number with no written explanation (already covered by above rules)
    # Rule: Is spam, promotional, or written by brand (heuristic check)
    spam_keywords = ["promocode", "referral link", "use my code", "earn money", "whatsapp me"]
    for sk in spam_keywords:
        if sk in text.lower():
            return False
    return True

def get_matched_keywords(text):
    text_lower = text.lower()
    matched = []
    for kw in KEYWORDS:
        # Use word boundary or simple search to find keyword match
        if kw in text_lower:
            matched.append(kw)
    return matched

def get_rq_answered(text, matched_kws):
    text_lower = text.lower()
    rqs = set()
    # Check keyword matches
    for rq_num, rq_kws in RQ_KEYWORDS.items():
        for kw in rq_kws:
            if kw in text_lower:
                rqs.add(rq_num)
    # Ensure it answers at least one research question
    if not rqs:
        # Fallback check
        return []
    return sorted(list(rqs))

def get_user_segment(text):
    text_lower = text.lower()
    segments = []
    if "plus size" in text_lower or "fat" in text_lower or "xl" in text_lower or "xxl" in text_lower or "curves" in text_lower:
        segments.append("plus size")
    if "student" in text_lower or "college" in text_lower or "pocket money" in text_lower:
        segments.append("student")
    if "cheap" in text_lower or "expensive" in text_lower or "costly" in text_lower or "price" in text_lower or "budget" in text_lower or "sale" in text_lower or "discount" in text_lower or "affordable" in text_lower:
        segments.append("budget shopper")
    if "gift" in text_lower or "gifting" in text_lower or "present" in text_lower or "husband" in text_lower or "wife" in text_lower or "sister" in text_lower or "friend" in text_lower:
        segments.append("gift buyer")
    if "first time" in text_lower or "first order" in text_lower or "new user" in text_lower or "new account" in text_lower:
        segments.append("first-time buyer")
    if "regular" in text_lower or "always" in text_lower or "every time" in text_lower or "frequently" in text_lower or "often" in text_lower:
        segments.append("repeat buyer")
    if "tier 2" in text_lower or "town" in text_lower or "village" in text_lower:
        segments.append("tier 2 city")
    
    if not segments:
        return "unidentified"
    return ", ".join(segments)

def load_existing_reviews(filepath):
    existing = []
    seen_texts = set()
    try:
        import os
        if not os.path.exists(filepath):
            return existing
        print(f"Loading existing reviews from {filepath}...")
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("|") and not line.startswith("| #") and not line.startswith("|---"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 9:
                    raw_text = parts[2].replace("\\|", "|")
                    source = parts[3]
                    date = parts[4]
                    platform = parts[5]
                    kws = parts[6]
                    rqs = parts[7]
                    segment = parts[8]
                    
                    if raw_text.lower() not in seen_texts:
                        seen_texts.add(raw_text.lower())
                        existing.append({
                            "raw_text": raw_text,
                            "source": source,
                            "date": date,
                            "platform": platform,
                            "keywords_matched": kws,
                            "rq_answered": rqs,
                            "segment": segment
                        })
        print(f"Loaded {len(existing)} unique existing reviews.")
    except Exception as e:
        print(f"Error loading existing reviews: {e}")
    return existing

def fetch_play_store(max_rows=1000, existing_reviews=None):
    print(f"Fetching Play Store reviews (target: {max_rows})...")
    collected = []
    seen_texts = set()
    
    if existing_reviews:
        for r in existing_reviews:
            if r["source"] == "Play Store":
                collected.append(r)
                seen_texts.add(r["raw_text"].lower())
                
    print(f"Loaded {len(collected)} existing Play Store reviews.")
    if len(collected) >= max_rows:
        return collected[:max_rows]
        
    sorts = [Sort.NEWEST, Sort.MOST_RELEVANT]
    seen_ids = set()
    
    for sort_type in sorts:
        if len(collected) >= max_rows:
            break
        try:
            continuation_token = None
            batch_count = 0
            while len(collected) < max_rows:
                batch_count += 1
                print(f"Fetching Play Store batch {batch_count} for sort {sort_type}...")
                if continuation_token is not None:
                    result, continuation_token = reviews(
                        'com.myntra.android',
                        lang='en',
                        country='in',
                        sort=sort_type,
                        count=1000,
                        continuation_token=continuation_token
                    )
                else:
                    result, continuation_token = reviews(
                        'com.myntra.android',
                        lang='en',
                        country='in',
                        sort=sort_type,
                        count=1000
                    )
                if not result:
                    break
                    
                new_in_batch = 0
                for item in result:
                    review_id = item.get('reviewId')
                    if review_id in seen_ids:
                        continue
                    seen_ids.add(review_id)
                    
                    content = clean_text(item.get('content', ''))
                    if content.lower() in seen_texts:
                        continue
                        
                    if not matches_quality_rules(content):
                        continue
                        
                    matched_kws = get_matched_keywords(content)
                    if not matched_kws:
                        continue
                        
                    rqs = get_rq_answered(content, matched_kws)
                    if not rqs:
                        continue
                        
                    date_str = item.get('at').strftime('%Y-%m-%d') if item.get('at') else 'N/A'
                    segment = get_user_segment(content)
                    
                    row = {
                        "raw_text": content,
                        "source": "Play Store",
                        "date": date_str,
                        "platform": "Android App",
                        "keywords_matched": ", ".join(matched_kws),
                        "rq_answered": ", ".join(map(str, rqs)),
                        "segment": segment
                    }
                    collected.append(row)
                    seen_texts.add(content.lower())
                    new_in_batch += 1
                    
                    if len(collected) >= max_rows:
                        break
                        
                print(f"Batch {batch_count}: processed {len(result)} reviews, found {new_in_batch} new qualifying reviews. Total Play Store: {len(collected)}")
                
                if not continuation_token:
                    break
                    
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error fetching Play Store reviews with sort {sort_type}: {e}")
            
    return collected[:max_rows]

def fetch_app_store(max_rows=1000, existing_reviews=None):
    print(f"Fetching App Store reviews (target: {max_rows})...")
    collected = []
    seen_texts = set()
    
    if existing_reviews:
        for r in existing_reviews:
            if r["source"] == "App Store":
                collected.append(r)
                seen_texts.add(r["raw_text"].lower())
                
    print(f"Loaded {len(collected)} existing App Store reviews.")
    if len(collected) >= max_rows:
        return collected[:max_rows]
    
    countries = ["in", "ae", "sg", "gb", "ca", "au", "sa", "om", "qa", "kw", "bh", "us"]
    sorts = ["mostrecent", "mostHelpful"]
    new_reviews_fetched = 0
    
    for country in countries:
        if len(collected) >= max_rows:
            break
        for sort in sorts:
            if len(collected) >= max_rows:
                break
            print(f"Scraping App Store reviews for country: {country}, sort: {sort}...")
            for page in range(1, 11):
                if len(collected) >= max_rows:
                    break
                try:
                    url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id=907394059/sortby={sort}/json"
                    response = requests.get(url, headers=HEADERS, timeout=10)
                    if response.status_code != 200:
                        continue
                        
                    data = response.json()
                    entries = data.get('feed', {}).get('entry', [])
                    if not entries:
                        continue
                        
                    for entry in entries:
                        if 'im:name' in entry:
                            continue
                            
                        content = clean_text(entry.get('content', {}).get('label', ''))
                        if content.lower() in seen_texts:
                            continue
                            
                        if not matches_quality_rules(content):
                            continue
                            
                        matched_kws = get_matched_keywords(content)
                        if not matched_kws:
                            continue
                            
                        rqs = get_rq_answered(content, matched_kws)
                        if not rqs:
                            continue
                            
                        updated_label = entry.get('updated', {}).get('label', 'N/A')
                        date_str = updated_label.split('T')[0] if 'T' in updated_label else updated_label
                        segment = get_user_segment(content)
                        
                        row = {
                            "raw_text": content,
                            "source": "App Store",
                            "date": date_str,
                            "platform": "iOS App",
                            "keywords_matched": ", ".join(matched_kws),
                            "rq_answered": ", ".join(map(str, rqs)),
                            "segment": segment
                        }
                        collected.append(row)
                        seen_texts.add(content.lower())
                        new_reviews_fetched += 1
                        
                        if len(collected) >= max_rows:
                            break
                            
                except Exception as e:
                    print(f"Error fetching App Store reviews for country {country}, sort {sort}, page {page}: {e}")
                    break
            
            time.sleep(0.5)
            
    print(f"Scraped App Store: found {new_reviews_fetched} new qualifying reviews. Total App Store: {len(collected)}")
    return collected[:max_rows]

def fetch_reddit(max_rows=100, existing_reviews=None):
    print(f"Fetching Reddit data (target: {max_rows})...")
    collected = []
    seen_texts = set()
    
    if existing_reviews:
        for r in existing_reviews:
            if r["source"] == "Reddit":
                collected.append(r)
                seen_texts.add(r["raw_text"].lower())
                
    print(f"Loaded {len(collected)} existing Reddit reviews.")
    if len(collected) >= max_rows:
        return collected[:max_rows]
        
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "myntra_feedback_engine_v1.0")
    
    if not client_id or not client_secret:
        print("Reddit scraping skipped: REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables are missing.")
        raise Exception("Authentication required (REDDIT_CLIENT_ID/SECRET missing)")
        
    import praw
    from praw.models import Comment
    from datetime import datetime, timezone
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Subreddits relevant to Indian ecommerce/fashion/discussions
        subreddits = ["IndianFashionAddicts", "india", "AskIndia", "frugalmalefashion"]
        new_reviews_fetched = 0
        
        for sub_name in subreddits:
            if len(collected) >= max_rows:
                break
            print(f"Searching r/{sub_name} for 'Myntra' posts/comments...")
            try:
                sub = reddit.subreddit(sub_name)
                # Search submissions
                for submission in sub.search("Myntra", limit=50):
                    if len(collected) >= max_rows:
                        break
                    
                    # 1. Check submission text
                    sub_text = clean_text(submission.selftext)
                    if sub_text and len(sub_text) > 10 and sub_text.lower() not in seen_texts:
                        if matches_quality_rules(sub_text):
                            matched_kws = get_matched_keywords(sub_text)
                            if matched_kws:
                                rqs = get_rq_answered(sub_text, matched_kws)
                                if rqs:
                                    date_str = datetime.fromtimestamp(submission.created_utc, timezone.utc).strftime('%Y-%m-%d')
                                    row = {
                                        "raw_text": sub_text,
                                        "source": "Reddit",
                                        "date": date_str,
                                        "platform": f"r/{sub_name} Post",
                                        "keywords_matched": ", ".join(matched_kws),
                                        "rq_answered": ", ".join(map(str, rqs)),
                                        "segment": get_user_segment(sub_text)
                                    }
                                    collected.append(row)
                                    seen_texts.add(sub_text.lower())
                                    new_reviews_fetched += 1
                                    
                    # 2. Check comments
                    submission.comments.replace_more(limit=0)
                    comments_list = submission.comments.list()
                    comments = [c for c in comments_list if isinstance(c, Comment)]
                    for comment in comments[:30]:
                        if len(collected) >= max_rows:
                            break
                        comment_text = clean_text(comment.body)
                        if not comment_text or len(comment_text) < 10 or comment_text.lower() in seen_texts:
                            continue
                            
                        if not matches_quality_rules(comment_text):
                            continue
                            
                        matched_kws = get_matched_keywords(comment_text)
                        if not matched_kws:
                            continue
                            
                        rqs = get_rq_answered(comment_text, matched_kws)
                        if not rqs:
                            continue
                            
                        date_str = datetime.fromtimestamp(comment.created_utc, timezone.utc).strftime('%Y-%m-%d')
                        row = {
                            "raw_text": comment_text,
                            "source": "Reddit",
                            "date": date_str,
                            "platform": f"r/{sub_name} Comment",
                            "keywords_matched": ", ".join(matched_kws),
                            "rq_answered": ", ".join(map(str, rqs)),
                            "segment": get_user_segment(comment_text)
                        }
                        collected.append(row)
                        seen_texts.add(comment_text.lower())
                        new_reviews_fetched += 1
                        
            except Exception as e:
                print(f"Error scraping sub r/{sub_name}: {e}")
                
        print(f"Scraped Reddit: found {new_reviews_fetched} new qualifying reviews. Total Reddit: {len(collected)}")
        return collected[:max_rows]
        
    except Exception as e:
        print(f"Reddit client initialization error: {e}")
        raise e

def fetch_twitter(max_rows=100, existing_reviews=None):
    print(f"Fetching Twitter/X data (target: {max_rows})...")
    collected = []
    seen_texts = set()
    
    if existing_reviews:
        for r in existing_reviews:
            if r.get("source") == "Twitter":
                collected.append(r)
                seen_texts.add(r["raw_text"].lower())
                
    print(f"Loaded {len(collected)} existing Twitter reviews.")
    if len(collected) >= max_rows:
        return collected[:max_rows]
        
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("Twitter/X scraping skipped: TWITTER_BEARER_TOKEN environment variable is missing.")
        raise Exception("Authentication required (TWITTER_BEARER_TOKEN missing)")
        
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "v2RecentSearchPython"
    }
    params = {
        "query": "Myntra -is:retweet",
        "max_results": 100,
        "tweet.fields": "created_at,text"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
        data = response.json()
        tweets = data.get("data", [])
        
        new_reviews_fetched = 0
        for item in tweets:
            if len(collected) >= max_rows:
                break
                
            text = clean_text(item.get("text", ""))
            if not text or len(text) < 10 or text.lower() in seen_texts:
                continue
                
            if not matches_quality_rules(text):
                continue
                
            matched_kws = get_matched_keywords(text)
            if not matched_kws:
                continue
                
            rqs = get_rq_answered(text, matched_kws)
            if not rqs:
                continue
                
            created_at = item.get("created_at")
            date_str = created_at[:10] if created_at else time.strftime('%Y-%m-%d')
            
            row = {
                "raw_text": text,
                "source": "Twitter",
                "date": date_str,
                "platform": "Twitter/X",
                "keywords_matched": ", ".join(matched_kws),
                "rq_answered": ", ".join(map(str, rqs)),
                "segment": get_user_segment(text)
            }
            collected.append(row)
            seen_texts.add(text.lower())
            new_reviews_fetched += 1
            
        print(f"Scraped Twitter: found {new_reviews_fetched} new qualifying reviews. Total Twitter: {len(collected)}")
        return collected[:max_rows]
    except Exception as e:
        print(f"Twitter API request error: {e}")
        raise e

def fetch_youtube(max_rows=100, existing_reviews=None):
    print(f"Fetching YouTube data (target: {max_rows})...")
    collected = []
    seen_texts = set()
    
    if existing_reviews:
        for r in existing_reviews:
            if r.get("source") == "YouTube":
                collected.append(r)
                seen_texts.add(r["raw_text"].lower())
                
    print(f"Loaded {len(collected)} existing YouTube reviews.")
    if len(collected) >= max_rows:
        return collected[:max_rows]
        
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YouTube scraping skipped: YOUTUBE_API_KEY environment variable is missing.")
        raise Exception("Authentication required (YOUTUBE_API_KEY missing)")
        
    search_url = "https://www.googleapis.com/youtube/v3/search"
    comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    
    try:
        search_params = {
            "key": api_key,
            "q": "Myntra haul OR Myntra review",
            "type": "video",
            "part": "id,snippet",
            "maxResults": 10,
            "relevanceLanguage": "en"
        }
        
        search_response = requests.get(search_url, params=search_params)
        if search_response.status_code != 200:
            raise Exception(f"YouTube Search API Error {search_response.status_code}: {search_response.text}")
            
        search_data = search_response.json()
        video_items = search_data.get("items", [])
        video_ids = [item["id"]["videoId"] for item in video_items if "id" in item and "videoId" in item["id"]]
        
        new_reviews_fetched = 0
        for video_id in video_ids:
            if len(collected) >= max_rows:
                break
                
            comment_params = {
                "key": api_key,
                "videoId": video_id,
                "part": "snippet",
                "maxResults": 50,
                "textFormat": "plainText"
            }
            
            comment_response = requests.get(comments_url, params=comment_params)
            if comment_response.status_code != 200:
                continue
                
            comment_data = comment_response.json()
            comment_items = comment_data.get("items", [])
            
            for item in comment_items:
                if len(collected) >= max_rows:
                    break
                    
                snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                text_original = snippet.get("textOriginal", "")
                text = clean_text(text_original)
                
                if not text or len(text) < 10 or text.lower() in seen_texts:
                    continue
                    
                if not matches_quality_rules(text):
                    continue
                    
                matched_kws = get_matched_keywords(text)
                if not matched_kws:
                    continue
                    
                rqs = get_rq_answered(text, matched_kws)
                if not rqs:
                    continue
                    
                published_at = snippet.get("publishedAt")
                date_str = published_at[:10] if published_at else time.strftime('%Y-%m-%d')
                
                row = {
                    "raw_text": text,
                    "source": "YouTube",
                    "date": date_str,
                    "platform": "YouTube Comment",
                    "keywords_matched": ", ".join(matched_kws),
                    "rq_answered": ", ".join(map(str, rqs)),
                    "segment": get_user_segment(text)
                }
                collected.append(row)
                seen_texts.add(text.lower())
                new_reviews_fetched += 1
                
        print(f"Scraped YouTube: found {new_reviews_fetched} new qualifying reviews. Total YouTube: {len(collected)}")
        return collected[:max_rows]
    except Exception as e:
        print(f"YouTube API request error: {e}")
        raise e

def main():
    existing_reviews = load_existing_reviews("collected_data.md")
    
    play_store_data = fetch_play_store(1000, existing_reviews=existing_reviews)
    app_store_data = fetch_app_store(1000, existing_reviews=existing_reviews)
    
    reddit_data = []
    twitter_data = []
    youtube_data = []
    skipped_sources = []
    
    # Reddit
    try:
        reddit_data = fetch_reddit(100, existing_reviews=existing_reviews)
    except Exception as e:
        skipped_sources.append(f"Reddit ({e})")
        
    # Twitter
    try:
        twitter_data = fetch_twitter(100, existing_reviews=existing_reviews)
    except Exception as e:
        skipped_sources.append(f"Twitter/X ({e})")
        
    # YouTube
    try:
        youtube_data = fetch_youtube(100, existing_reviews=existing_reviews)
    except Exception as e:
        skipped_sources.append(f"YouTube ({e})")
        
    all_data = play_store_data + app_store_data + reddit_data + twitter_data + youtube_data
    
    # Generate collected_data.md
    output_path = "collected_data.md"
    print(f"Writing dataset to {output_path}...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Collected User Feedback Dataset (Myntra Only)\n\n")
        f.write("This dataset contains actual user feedback verbatim from public sources matching Myntra-specific filtering rules.\n\n")
        
        f.write("## Data Collection Table\n\n")
        f.write("| # | Raw Text (verbatim) | Source | Date | Platform | Keywords Matched | Research Question Answered (1–10) | User Segment Flag |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        
        for idx, row in enumerate(all_data, 1):
            f.write(f"| {idx} | {row['raw_text']} | {row['source']} | {row['date']} | {row['platform']} | {row['keywords_matched']} | {row['rq_answered']} | {row['segment']} |\n")
            
        f.write("\n## Skipped Sources\n\n")
        if skipped_sources:
            for source in skipped_sources:
                f.write(f"- {source}\n")
        else:
            f.write("None. All sources fetched successfully.\n")
            
    print(f"Successfully collected {len(all_data)} rows.")
    print(f"Play Store: {len(play_store_data)} rows")
    print(f"App Store: {len(app_store_data)} rows")
    print(f"Reddit: {len(reddit_data)} rows")
    print(f"Twitter/X: {len(twitter_data)} rows")
    print(f"YouTube: {len(youtube_data)} rows")

if __name__ == "__main__":
    main()
