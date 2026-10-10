import os
import numpy as np
import pandas as pd


def calculate_trend_score(domain, keywords=None):
    """
    Evaluates market interest score (0-100) based on domain and keywords.
    Handles None, empty strings, and non-iterable inputs safely.
    """
    high_growth_terms = [
        'ai', 'machine learning', 'agritech', 'fintech', 'edtech',
        'healthtech', 'saas', 'iot', 'robotics', 'cloud', 'cybersecurity'
    ]
    score = 75.0
    domain_str = str(domain or "").strip()

    if isinstance(keywords, str):
        keywords_list = [keywords]
    elif isinstance(keywords, (list, tuple, set)):
        keywords_list = [str(k) for k in keywords if k is not None]
    else:
        keywords_list = []

    combined = f"{domain_str} {' '.join(keywords_list)}".lower()

    for term in high_growth_terms:
        if term in combined:
            score += 4.5

    return min(98.5, round(score, 1))


def fetch_google_trends_score(domain, keywords=None):
    """
    Uses pytrends to calculate a Google Trends interest score.
    Falls back to the local heuristic when live trends are unavailable.
    """
    domain_str = str(domain or "").strip()
    if isinstance(keywords, str):
        keywords_list = [keywords]
    elif isinstance(keywords, (list, tuple, set)):
        keywords_list = [str(k).strip() for k in keywords if k]
    else:
        keywords_list = []

    terms = [domain_str] + keywords_list
    terms = [term for term in terms if term][:5]
    if not terms:
        terms = ["startup"]

    try:
        from pytrends.request import TrendReq
        proxies = [
            proxy.strip()
            for proxy in os.getenv("PYTRENDS_PROXIES", "").split(",")
            if proxy.strip()
        ]
        timeout = (
            int(os.getenv("PYTRENDS_CONNECT_TIMEOUT", "5")),
            int(os.getenv("PYTRENDS_READ_TIMEOUT", "10")),
        )
        pytrends = TrendReq(
            hl=os.getenv("PYTRENDS_LANGUAGE", "en-US"),
            tz=int(os.getenv("PYTRENDS_TIMEZONE", "330")),
            timeout=timeout,
            proxies=proxies,
            retries=int(os.getenv("PYTRENDS_RETRIES", "2")),
            backoff_factor=float(os.getenv("PYTRENDS_BACKOFF_FACTOR", "0.1")),
        )
        pytrends.build_payload(terms, timeframe="today 12-m")
        frame = pytrends.interest_over_time()
        if not frame.empty:
            numeric = frame.drop(columns=["isPartial"], errors="ignore")
            mean_val = numeric.mean().mean()
            if not np.isnan(mean_val):
                head_mean = numeric.head(4).mean().mean()
                tail_mean = numeric.tail(4).mean().mean()
                diff = tail_mean - head_mean
                momentum = float(diff) if not np.isnan(diff) else 0.0
                score = np.clip(mean_val + (momentum * 0.4), 0, 100)
                series_data = numeric.reset_index().tail(12).to_dict(
                    orient="records"
                )
                return {
                    "score": round(float(score), 1),
                    "source": "Google Trends via pytrends",
                    "series": series_data,
                }
    except Exception:
        pass

    fallback_score = calculate_trend_score(domain_str, keywords_list)
    return {
        "score": fallback_score,
        "source": "Heuristic trend model",
        "series": pd.DataFrame({
            "keyword": terms,
            "interest": [fallback_score] * len(terms),
        }).to_dict(orient="records"),
    }
