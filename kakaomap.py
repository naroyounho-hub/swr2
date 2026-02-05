from __future__ import annotations

from typing import Dict, List, Optional
import os
import requests
import streamlit as st

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def kakao_keyword_search(
    query: str,
    category: Optional[str] = None,  # e.g. "FD6" (food)
    x: Optional[float] = None,
    y: Optional[float] = None,
    radius: Optional[int] = None,
    page: int = 1,
    size: int = 15,
    api_key: Optional[str] = None,
) -> List[Dict[str, str]]:
    key = api_key or st.secrets.get("KAKAO_REST_API_KEY", "") or KAKAO_REST_API_KEY
    if not key:
        raise ValueError("KAKAO_REST_API_KEY is empty")

    params = {
        "query": query,
        "page": page,
        "size": size,
    }
    if category:
        params["category_group_code"] = category
    if x is not None and y is not None:
        params["x"] = x
        params["y"] = y
    if radius is not None:
        params["radius"] = radius

    headers = {"Authorization": f"KakaoAK {key}"}
    r = requests.get(KAKAO_KEYWORD_URL, params=params, headers=headers, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = r.text
        except Exception:
            detail = ""
        msg = f"Kakao Local API error: {r.status_code} {r.reason}"
        if detail:
            msg = f"{msg} | body: {detail}"
        raise requests.HTTPError(msg, response=r) from e
    data = r.json()

    docs = []
    for d in data.get("documents", []):
        docs.append(
            {
                "x": d.get("x"),
                "y": d.get("y"),
                "place_name": d.get("place_name"),
                "address_name": d.get("address_name"),
                "place_url": d.get("place_url"),
            }
        )
    return docs
