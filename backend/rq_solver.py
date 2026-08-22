import json
import pandas as pd

RESEARCH_QUESTIONS = {
    1: {
        "title": "Why do users add fashion products to their wishlist?",
        "short_name": "Wishlist Drivers & Intent",
        "description": "Explores the psychological and functional reasons users shortlist items without purchasing immediately.",
        "keywords": ["wishlist", "saved", "liked", "bookmark", "shortlist", "want to buy"],
        "default_friction": "Aesthetic curation & casual bookmarking without purchase commitment.",
        "delay_penalty": 1.4,
        "intent_intensity": 0.55
    },
    2: {
        "title": "What prevents wishlisted products from eventually being purchased?",
        "short_name": "Conversion Roadblocks & Drops",
        "description": "Identifies the core drop-off catalysts between saving an item and final checkout.",
        "keywords": ["didn't buy", "couldn't buy", "out of stock", "expensive", "too costly", "confused", "can't decide"],
        "default_friction": "Sudden stockouts in user's size and checkout anxiety on value perception.",
        "delay_penalty": 2.1,
        "intent_intensity": 0.85
    },
    3: {
        "title": "What uncertainties remain after users have identified a product they like?",
        "short_name": "Post-Shortlist Hesitation",
        "description": "Analyzes remaining friction regarding sizing, fabric drape, and real vs photo appearance.",
        "keywords": ["not sure", "confused", "will it fit", "looks different", "different in real", "fabric", "material", "looks cheap"],
        "default_friction": "Visual-reality gap: fear that fabric, color, or silhouette will disappoint in person.",
        "delay_penalty": 1.9,
        "intent_intensity": 0.78
    },
    4: {
        "title": "What causes users to postpone a purchase?",
        "short_name": "Purchase Postponement Triggers",
        "description": "Investigates timing factors like payday cycles, upcoming sales, and event-based dates.",
        "keywords": ["holding off", "waiting", "will buy later", "next month", "after salary", "payday", "waiting for sale", "planning to buy"],
        "default_friction": "Timeline misalignment: saving for payday or future events without urgency triggers.",
        "delay_penalty": 2.4,
        "intent_intensity": 0.82
    },
    5: {
        "title": "How do users compare multiple shortlisted products?",
        "short_name": "Shortlist Evaluation & Comparison",
        "description": "Examines how shoppers evaluate tradeoffs between similar items across Myntra and external competitors.",
        "keywords": ["compared", "comparing", "better option", "checking other sites", "similar product", "alternatives"],
        "default_friction": "Lack of side-by-side spec, fabric, and sizing comparisons on platform.",
        "delay_penalty": 1.6,
        "intent_intensity": 0.72
    },
    6: {
        "title": "What information do users seek outside Myntra before purchasing?",
        "short_name": "External Information Seeking",
        "description": "Tracks customer journeys to YouTube, Instagram, and Reddit for real try-ons and authentic reviews.",
        "keywords": ["YouTube review", "searched on YouTube", "Instagram", "looked up", "googled", "influencer", "asked friend"],
        "default_friction": "Social proof deficit: searching YouTube/Instagram for unedited video try-ons.",
        "delay_penalty": 1.8,
        "intent_intensity": 0.76
    },
    7: {
        "title": "What role do fit, size, styling, price, reviews, occasion and social validation play?",
        "short_name": "Fit, Styling & Social Validation",
        "description": "Quantifies the dominant conversion driver: sizing confidence and styling clarity.",
        "keywords": ["size chart", "fit", "fitting", "true to size", "runs small", "runs large", "body type", "petite", "plus size", "styling", "occasion"],
        "default_friction": "Inconsistent brand sizing & fear of cumbersome return/tag verification loops.",
        "delay_penalty": 2.5,
        "intent_intensity": 0.90
    },
    8: {
        "title": "When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?",
        "short_name": "High-Intent vs Bookmarking",
        "description": "Distinguishes between high-intent 'ready to buy' shortlists and passive mood-board inspiration.",
        "keywords": ["wishlist", "bookmark", "save for later", "planning to buy", "would have bought"],
        "default_friction": "Cluttered wishlist where high-intent items get buried under casual bookmarks.",
        "delay_penalty": 1.7,
        "intent_intensity": 0.65
    },
    9: {
        "title": "How do these behaviors differ across user segments?",
        "short_name": "Cross-Segment Behavioral Variance",
        "description": "Analyzes how plus-size shoppers, students, budget buyers, and tier-2 consumers experience wishlist friction.",
        "keywords": ["plus size", "student", "budget", "gift", "birthday", "first time", "repeat buyer", "tier 2"],
        "default_friction": "Segment-specific hurdles (e.g. plus-size stock scarcity vs student delivery fee sensitivity).",
        "delay_penalty": 2.0,
        "intent_intensity": 0.80
    },
    10: {
        "title": "What unmet needs emerge consistently across user conversations?",
        "short_name": "Systemic Unmet Needs",
        "description": "Extracts high-frequency customer feature requests and platform gaps from user feedback.",
        "keywords": ["wish they had", "would have bought", "missing feature", "no review", "no size guide", "can't filter", "wish Myntra had", "please add"],
        "default_friction": "Demand for cross-brand size standardizer, occasion countdowns, and outfit coordinators.",
        "delay_penalty": 2.2,
        "intent_intensity": 0.88
    }
}

class RQSolver:
    def __init__(self, data_loader, groq_engine):
        self.data_loader = data_loader
        self.groq_engine = groq_engine
        
    def get_rq_evidence(self, rq_num, limit=20):
        if self.data_loader.df.empty:
            return []
        df = self.data_loader.df
        # Match RQ answered column or keywords
        rq_info = RESEARCH_QUESTIONS.get(rq_num, {})
        kws = rq_info.get("keywords", [])
        
        # Check rq_answered
        matches_rq = df[df["rq_answered"].str.contains(str(rq_num), na=False)]
        if len(matches_rq) < limit:
            # Add keyword matches
            kw_pattern = "|".join(kws)
            matches_kw = df[df["raw_text"].str.contains(kw_pattern, case=False, na=False)]
            combined = pd.concat([matches_rq, matches_kw]).drop_duplicates(subset=["raw_text"])
            return combined.head(limit).to_dict("records")
        return matches_rq.head(limit).to_dict("records")

    def get_opportunity_score(self, rq_num):
        rq_info = RESEARCH_QUESTIONS.get(rq_num, {})
        evidence = self.get_rq_evidence(rq_num, limit=500)
        total_items = max(len(self.data_loader.df), 1)
        
        volume_ratio = len(evidence) / total_items
        delay_penalty = rq_info.get("delay_penalty", 1.5)
        intent_intensity = rq_info.get("intent_intensity", 0.7)
        
        # OIS = Volume Ratio * Delay Penalty * Intent Intensity * 100
        ois = round(volume_ratio * delay_penalty * intent_intensity * 100, 2)
        return {
            "volume_count": len(evidence),
            "volume_ratio": round(volume_ratio * 100, 1),
            "delay_penalty": delay_penalty,
            "intent_intensity": intent_intensity,
            "opportunity_impact_score": ois
        }
