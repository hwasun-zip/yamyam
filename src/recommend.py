"""얌얌 추천 로직 (핵심 재구현).

흐름: 현재 날씨 → 설문 기반 선호 메뉴 기준표 매칭 → 후보 식당 정렬

- 날씨별 선호 메뉴 기준표는 설문 50여 명 결과를 정리한 것
- 원 프로젝트에서는 네이버 검색 API로 후보 식당을 수집하고
  공공데이터(기상청)에서 현재 날씨를 받아왔다
"""

import pandas as pd

# 설문 결과 기준표 (날씨 조건 → 선호 메뉴 카테고리, 선호 순위 순)
WEATHER_MENU_MAP = {
    "비":   ["국물 요리", "전·부침 요리"],
    "더움": ["차가운 면 요리", "빙수·디저트"],
    "추움": ["국물 요리", "찜·탕 요리"],
    "맑음": ["가벼운 식사", "카페·브런치"],
}


def classify_weather(temp_c: float, rain_mm: float) -> str:
    if rain_mm >= 1.0:
        return "비"
    if temp_c >= 28:
        return "더움"
    if temp_c <= 5:
        return "추움"
    return "맑음"


def score_restaurant(row: pd.Series, preferred: list[str]) -> float:
    """날씨 선호 매칭(주 점수) + 평점(보조) + 거리 패널티."""
    menu_score = 0.0
    if row["category"] in preferred:
        # 선호 1순위면 2점, 2순위면 1점
        menu_score = 2.0 - preferred.index(row["category"])
    return menu_score * 10 + row["rating"] * 2 - row["distance_km"]


def recommend(restaurants: pd.DataFrame, temp_c: float, rain_mm: float, top_n: int = 5):
    weather = classify_weather(temp_c, rain_mm)
    preferred = WEATHER_MENU_MAP[weather]
    df = restaurants.copy()
    df["score"] = df.apply(score_restaurant, axis=1, preferred=preferred)
    print(f"오늘 날씨 분류: {weather} → 선호 메뉴: {', '.join(preferred)}")
    return df.sort_values("score", ascending=False).head(top_n)


if __name__ == "__main__":
    sample = pd.DataFrame([
        {"name": "명동칼국수", "category": "국물 요리",   "rating": 4.6, "distance_km": 0.3},
        {"name": "진국설렁탕", "category": "국물 요리",   "rating": 4.4, "distance_km": 0.5},
        {"name": "그린샐러드바", "category": "가벼운 식사", "rating": 4.5, "distance_km": 0.2},
        {"name": "화덕피자집", "category": "양식",        "rating": 4.7, "distance_km": 0.4},
        {"name": "냉면본가",   "category": "차가운 면 요리", "rating": 4.3, "distance_km": 0.6},
    ])
    # 예시: 비 오는 날 18도
    print(recommend(sample, temp_c=18, rain_mm=3.2)[["name", "category", "rating", "score"]])
