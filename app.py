"""광주·전남 관광지 대시보드 (간략버전).

한국관광공사 Tour API 의 areaBasedList2 단일 엔드포인트만 사용한다.
- 지역(광주 5 / 전남 38)별 관광지 목록 조회
- 지역 / 관광지명 필터
- Folium 지도 + 목록 + CSV 다운로드
"""

import os
from html import escape

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# 페이지 설정 (다른 st 명령보다 먼저 호출되어야 함)
st.set_page_config(page_title="광주·전남 관광지 대시보드 (간략버전)", layout="wide")
st.title("🗺️ 광주·전남 관광지 대시보드 (간략버전)")


def get_service_key():
    """서비스 키를 읽는다. .streamlit/secrets.toml 우선, 없으면 OS 환경변수."""
    try:
        key = st.secrets.get("TOUR_API_SERVICE_KEY")
        if key:
            return str(key).strip()
    except Exception:
        # secrets.toml 이 없거나 문법 오류인 경우 → 환경변수로 폴백
        pass
    return (os.getenv("TOUR_API_SERVICE_KEY") or "").strip() or None


SERVICE_KEY = get_service_key()

# 유일한 API 엔드포인트
API_BASE = "https://apis.data.go.kr/B551011/KorService2"
API_URL = f"{API_BASE}/areaBasedList2"

# 5: 광주광역시, 38: 전라남도
AREA_CODES = (5, 38)
AREAS = {
    "전체": AREA_CODES,
    "광주광역시": (5,),
    "전라남도": (38,),
}

CONTENT_TYPE_ID = 12  # 관광지
NUM_ROWS = 50
MAX_PAGES = 2  # 지역별 최대 조회 페이지 수 (페이지당 NUM_ROWS건)
DEFAULT_MAP_CENTER = [35.0, 126.9]

DISPLAY_COLUMNS = [
    "title",
    "region",
    "cat1",
    "cat2",
    "cat3",
    "address",
    "tel",
    "lat",
    "lng",
]


class ApiError(Exception):
    """API 호출 실패를 사용자 안내 문구와 함께 전달한다."""


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tour_data(area_code, page_no=1):
    """
    areaBasedList2 에서 관광지 목록 1페이지를 조회한다.

    Returns:
        list[dict]: items.item 목록
    """
    if not SERVICE_KEY:
        raise ApiError(
            "SERVICE_KEY가 설정되지 않았습니다. .streamlit/secrets.toml 파일의 "
            "TOUR_API_SERVICE_KEY를 확인해주세요."
        )

    params = {
        "serviceKey": SERVICE_KEY,
        "MobileOS": "ETC",
        "MobileApp": "GJBoard",
        "_type": "json",
        "areaCode": area_code,
        "contentTypeId": CONTENT_TYPE_ID,
        "numOfRows": NUM_ROWS,
        "pageNo": page_no,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=15)
    except requests.exceptions.Timeout as exc:
        raise ApiError(
            "API 요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"API 요청 중 오류가 발생했습니다: {exc}") from exc

    if response.status_code == 403:
        raise ApiError(
            "API 인증 오류입니다. SERVICE_KEY가 유효한지 확인해주세요."
        )
    if response.status_code != 200:
        raise ApiError(f"API 요청 실패 (상태 코드 {response.status_code})")

    try:
        data = response.json()
    except ValueError as exc:
        raise ApiError(
            "API 응답을 해석할 수 없습니다. 인증키 인코딩 설정을 확인해주세요."
        ) from exc

    # resultCode 검증 ("0000"이 정상)
    header = (data.get("response") or {}).get("header") or {}
    result_code = header.get("resultCode")
    if result_code not in ("0000", "00"):
        raise ApiError(
            f"API 호출 오류 [{result_code or '-'}]: "
            f"{header.get('resultMsg', '알 수 없는 오류')}"
        )

    # body.items.item 추출 (items가 "" 또는 단일 dict인 경우도 처리)
    body = (data.get("response") or {}).get("body") or {}
    items = (body.get("items") or {}).get("item", [])
    if isinstance(items, dict):
        items = [items]

    return items


def build_df(items):
    """API 응답(item 목록)을 대시보드용 데이터프레임으로 변환한다."""
    rows = []

    for item in items:
        try:
            lat = float(item.get("mapy"))
            lng = float(item.get("mapx"))
        except (TypeError, ValueError):
            # 좌표가 없는 항목은 지도에 표시할 수 없으므로 건너뜀
            continue

        address = " ".join(
            part for part in (item.get("addr1"), item.get("addr2")) if part
        )

        rows.append(
            {
                "id": str(item.get("contentid", "")).strip(),
                "title": item.get("title") or "관광지",
                "region": item.get("addr1") or "",
                "cat1": item.get("cat1") or "",
                "cat2": item.get("cat2") or "",
                "cat3": item.get("cat3") or "",
                "address": address,
                "tel": item.get("tel") or "",
                "image": item.get("firstimage") or "",
                "lat": lat,
                "lng": lng,
            }
        )

    if not rows:
        return pd.DataFrame(columns=DISPLAY_COLUMNS + ["id", "image"])

    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=["id"]).reset_index(drop=True)


def load_poi_data(area_codes):
    """선택한 지역의 관광지 목록을 페이지 단위로 모아 데이터프레임으로 반환한다."""
    items = []

    for area_code in area_codes:
        for page_no in range(1, MAX_PAGES + 1):
            batch = fetch_tour_data(area_code, page_no)
            items.extend(batch)
            # 요청 건수보다 적게 반환되면 마지막 페이지
            if len(batch) < NUM_ROWS:
                break

    return build_df(items)


def create_map(data):
    """관광지를 Folium 지도로 시각화한다."""
    m = folium.Map(location=DEFAULT_MAP_CENTER, zoom_start=9)

    for _, row in data.iterrows():
        if pd.isna(row["lat"]) or pd.isna(row["lng"]):
            continue

        popup_parts = [f"<b>{escape(str(row['title']))}</b>"]
        if row.get("address"):
            popup_parts.append(escape(str(row["address"])))
        if row.get("tel"):
            popup_parts.append(f"☎ {escape(str(row['tel']))}")
        if row.get("image"):
            popup_parts.append(
                f"<img src='{escape(str(row['image']))}' width='220' "
                "style='margin-top:4px'/>"
            )

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=folium.Popup("".join(popup_parts), max_width=280),
            tooltip=str(row["title"]),
        ).add_to(m)

    return m


# ➕ 사이드바 필터
st.sidebar.header("🔍 필터")

area_label = st.sidebar.radio(
    "📍 지역 선택", options=list(AREAS), key="area_filter"
)

if st.sidebar.button("🔄 데이터 새로고침", key="reload_data_btn"):
    fetch_tour_data.clear()
    st.rerun()

# ➕ 데이터 로드 (캐시 1시간)
try:
    with st.spinner("관광지 데이터를 불러오는 중입니다..."):
        df_all = load_poi_data(AREAS[area_label])
except ApiError as exc:
    st.error(str(exc))
    df_all = build_df([])

df_poi = df_all

# 관광지명 검색
keyword = st.sidebar.text_input(
    "🔎 관광지명 검색", placeholder="예: 국립공원", key="title_filter"
)

if keyword.strip():
    df_poi = df_poi[
        df_poi["title"].fillna("").astype(str).str.contains(
            keyword.strip(), case=False, na=False
        )
    ]

# ➕ 요약 지표
metric_cols = st.columns(2)
metric_cols[0].metric("📥 전체 관광지", f"{len(df_all):,}건")
metric_cols[1].metric("📍 표시 중", f"{len(df_poi):,}건")

# ➕ 지도
st.subheader(f"📍 관광지 지도 ({len(df_poi):,}건)")
if df_poi.empty:
    st.info("표시할 관광지가 없습니다. 지역이나 필터를 변경해보세요.")
else:
    st_folium(create_map(df_poi), width=800, height=540, key="tour_map")

# ➕ 목록
st.subheader("📋 관광지 목록")
if df_poi.empty:
    st.caption("조회된 데이터가 없습니다.")
else:
    st.dataframe(
        df_poi[DISPLAY_COLUMNS], width="stretch", hide_index=True
    )

    st.download_button(
        "⬇️ 관광지 CSV 다운로드",
        data=df_poi.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"gwangju_jeonnam_poi_{len(df_poi)}.csv",
        mime="text/csv",
        key="download_poi_csv",
    )
