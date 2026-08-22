import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DataLoader:
    def __init__(self, data_path="collected_data.json"):
        self.data_path = data_path
        self.df = self.load_data()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.build_search_index()
        
    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            return df
        elif os.path.exists("collected_data.md"):
            # Fallback to md
            rows = []
            with open("collected_data.md", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not line.startswith("| #") and not line.startswith("|---"):
                        line_clean = line.replace("\\|", "__PIPE__")
                        parts = [p.strip() for p in line_clean.split("|")]
                        if len(parts) >= 9:
                            rows.append({
                                "id": int(parts[1]) if parts[1].isdigit() else len(rows)+1,
                                "raw_text": parts[2].replace("__PIPE__", "|"),
                                "source": parts[3],
                                "date": parts[4],
                                "platform": parts[5],
                                "keywords_matched": parts[6],
                                "rq_answered": parts[7],
                                "segment": parts[8]
                            })
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame()

    def build_search_index(self):
        if not self.df.empty and "raw_text" in self.df.columns:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df["raw_text"].fillna(""))

    def search(self, query, top_k=10, source_filter=None, segment_filter=None, rq_filter=None):
        if self.df.empty or not query:
            return []
        
        filtered_df = self.df.copy()
        if source_filter and source_filter != "All":
            filtered_df = filtered_df[filtered_df["source"] == source_filter]
        if segment_filter and segment_filter != "All":
            filtered_df = filtered_df[filtered_df["segment"].str.contains(segment_filter, case=False, na=False)]
        if rq_filter and rq_filter != "All":
            filtered_df = filtered_df[filtered_df["rq_answered"].str.contains(str(rq_filter), na=False)]

        if filtered_df.empty:
            return []

        # Vector search
        query_vec = self.vectorizer.transform([query])
        indices = filtered_df.index.tolist()
        sub_matrix = self.tfidf_matrix[indices]
        sims = cosine_similarity(query_vec, sub_matrix).flatten()
        
        # Rank
        top_indices_local = sims.argsort()[::-1][:top_k]
        results = []
        for loc_idx in top_indices_local:
            score = float(sims[loc_idx])
            orig_idx = indices[loc_idx]
            row = self.df.iloc[orig_idx].to_dict()
            row["score"] = round(score, 4)
            results.append(row)
        return results

    def get_summary_metrics(self):
        if self.df.empty:
            return {}
        total = len(self.df)
        sources = self.df["source"].value_counts().to_dict()
        
        # Segment counts
        segments = {}
        for seg_str in self.df["segment"].dropna():
            for s in [x.strip() for x in seg_str.split(",") if x.strip()]:
                segments[s] = segments.get(s, 0) + 1
                
        # RQ counts
        rq_counts = {}
        for rq_str in self.df["rq_answered"].dropna():
            for rq in [x.strip() for x in str(rq_str).split(",") if x.strip()]:
                if rq.isdigit():
                    rq_num = int(rq)
                    rq_counts[rq_num] = rq_counts.get(rq_num, 0) + 1

        return {
            "total_reviews": total,
            "sources": sources,
            "segments": segments,
            "rq_counts": rq_counts
        }
