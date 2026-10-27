# areaBasedList2 응답 필드 정리

한국관광공사 Tour API `areaBasedList2` (관광타입 12 = 관광지) 응답의 `items.item` 필드 설명입니다.
이 대시보드(`app.py`)는 이 중 **핵심 9개 필드**(+참고용 분류 코드 2개)만 사용합니다.

---

## 1. 한눈에 보는 핵심 필드

지도·목록을 만들 때 실제로 필요한 필드는 다음 9개뿐입니다.

| API 필드 | 앱 컬럼 | 의미 | 예시 |
|---|---|---|---|
| `contentid` | `id` | 콘텐츠 고유번호 (중복 제거 기준) | `127480` |
| `title` | `title` | 관광지 이름 | `가거도` |
| `addr1` | `region`, `address` | 기본 주소 (시·도 판별에도 사용) | `전남광주통합특별시 신안군 흑산면 가거도길 38-2` |
| `addr2` | `address` | 상세 주소 (없으면 빈값) | `(고군면)` |
| `mapx` | `lng` | **경도** (동서) | `125.1263860145` |
| `mapy` | `lat` | **위도** (남북) | `34.0520609879` |
| `tel` | `tel` | 전화번호 (없으면 빈값) | `061-240-8000` |
| `firstimage` | `image` | 대표 이미지 원본 URL | `http://tong.visitkorea.or.kr/.../image2_1.jpg` |
| `cat3` | `cat3` | 소분류 코드 (참고용 표시) | `A01011300` |

> ⚠️ `mapx` = 경도(lng), `mapy` = 위도(lat). 순서가 반대라서 가장 자주 틀리는 부분입니다.

---

## 2. 전체 필드 (목적별 그룹)

### 2-1. 식별 · 명칭

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `contentid` | 콘텐츠 고유번호 | 관광정보를 식별하는 번호 | `127480` |
| `contenttypeid` | 콘텐츠 유형 | `12`=관광지, `14`=문화시설, `15`=축제, `25`=여행코스, `28`=레포츠, `32`=숙박, `38`=쇼핑, `39`=음식점 | `12` |
| `title` | 관광지 이름 | 목록·지도에 표시할 이름 | `가거도` |

### 2-2. 주소 · 위치

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `addr1` | 기본 주소 | 시·도 + 시·군·구 + 도로명까지 포함 | `전남광주통합특별시 신안군 흑산면 가거도길 38-2` |
| `addr2` | 상세 주소 | 동/리 등 추가 정보. 없으면 빈값 | `(고군면)` |
| `zipcode` | 우편번호 | 주소의 우편번호 | `58866` |
| `mapx` | 경도 (X) | 지도 동서 위치 → `lng` | `125.1263860145` |
| `mapy` | 위도 (Y) | 지도 남북 위치 → `lat` | `34.0520609879` |
| `mlevel` | 지도 확대 수준 | 지도 표시 시 권장 줌 레벨 | `6` |

### 2-3. 지역 코드 (3가지 체계가 섞여 있음)

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `areacode` | 관광공사 지역 코드 | Tour API 시·도 코드. **광주 5 / 전남 38 / 서울 1** | `38` |
| `sigungucode` | 관광공사 시·군·구 코드 | `areacode` 하위 코드. **알파벳/행정순이 아니므로 문서 표를 확인** | `12` (가거도/신안) |
| `lDongRegnCd` | 법정동 시·도 코드 | 행정표준 법정동 체계. Tour API 코드와 **다름** | `12` (광주·전남 공통) |
| `lDongSignguCd` | 법정동 시·군·구 코드 | 법정동 체계의 하위 코드 | `870` (신안) |

> 세 체계를 구분해서 쓰세요. API 요청 파라미터(`areaCode`)에는 **`areacode` 체계**를 사용합니다.
> 실제 응답에서 광주(`areacode=5`)와 전남(`areacode=38`)이 모두 `lDongRegnCd=12`로 내려오므로,
> 지역 구분이 필요하면 `areacode`/`sigungucode`를 쓰는 편이 안전합니다.

### 2-4. 분류 코드 (2가지 체계가 함께 제공됨)

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `cat1` | 대분류 (구분류) | `A01` 자연, `A02` 인문(문화/예술/역사), `A03` 레포츠, `A04` 쇼핑, `A05` 음식 | `A02` |
| `cat2` | 중분류 (구분류) | `cat1`의 하위 분류 | `A0201` |
| `cat3` | 소분류 (구분류) | `cat2`의 하위 분류. 목록 표시용 | `A02010700` |
| `lclsSystm1` | 대분류 (신분류) | 2023년 개편된 관광 분류체계. 응답에는 `NA`, `HS`, `VE` 등이 내려옴 | `NA` |
| `lclsSystm2` | 중분류 (신분류) | 신분류 체계의 하위 분류 | `NA02` |
| `lclsSystm3` | 소분류 (신분류) | 신분류 체계의 하위 분류 | `NA020500` |

> `cat1~3`(구분류)과 `lclsSystm1~3`(신분류)은 **같은 대상을 다르게 코딩한 것**입니다. 하나만 골라 쓰면 됩니다.

### 2-5. 이미지 · 저작권

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `firstimage` | 대표 이미지 (원본) | 팝업/상세에 표시할 큰 이미지 | `http://tong.visitkorea.or.kr/.../image2_1.jpg` |
| `firstimage2` | 대표 이미지 (썸네일) | 목록용 축소 이미지 | `http://tong.visitkorea.or.kr/.../image2_1.jpg` |
| `cpyrhtDivCd` | 저작권 유형 코드 | 공공누리 이용 유형. `Type1` 출처표시 / `Type2` 출처표시+상업적이용금지 / `Type3` 출처표시+변경금지 / `Type4` 출처표시+상업적이용금지+변경금지 | `Type1` |

### 2-6. 연락처 · 등록/수정 시각

| 컬럼명 | 한글 의미 | 설명 | 예시 |
|---|---|---|---|
| `tel` | 전화번호 | 관광지/관리기관 연락처. 없으면 빈값 | `061-240-8000` |
| `createdtime` | 최초 등록 시각 | `YYYYMMDDHHMMSS` | `20030905090000` → 2003-09-05 09:00 |
| `modifiedtime` | 최종 수정 시각 | `YYYYMMDDHHMMSS` | `20260630184428` → 2026-06-30 18:44:28 |

---

## 3. 실제 응답 예시 (가거도, contentid 127480)

```json
{
  "contentid": "127480",
  "contenttypeid": "12",
  "title": "가거도",
  "addr1": "전남광주통합특별시 신안군 흑산면 가거도길 38-2",
  "addr2": "",
  "zipcode": "58866",
  "areacode": "38",
  "sigungucode": "12",
  "lDongRegnCd": "12",
  "lDongSignguCd": "870",
  "cat1": "A01",
  "cat2": "A0101",
  "cat3": "A01011300",
  "lclsSystm1": "NA",
  "lclsSystm2": "NA02",
  "lclsSystm3": "NA020500",
  "mapx": "125.1263860145",
  "mapy": "34.0520609879",
  "mlevel": "6",
  "tel": "",
  "firstimage": "http://tong.visitkorea.or.kr/cms/resource/.../image2_1.jpg",
  "firstimage2": "http://tong.visitkorea.or.kr/cms/resource/.../image2_1.jpg",
  "cpyrhtDivCd": "Type1",
  "createdtime": "20030905090000",
  "modifiedtime": "20260630184428"
}
```

→ 앱에서는 `title`, `addr1`+`addr2`, `mapx`(lng), `mapy`(lat), `tel`, `firstimage`만 꺼내 씁니다.

---

## 4. 앱에서의 처리 방식

```python
# 좌표: mapx=경도, mapy=위도 (순서 주의)
lng = float(item.get("mapx"))
lat = float(item.get("mapy"))

# 주소: 기본 + 상세 주소 결합
address = " ".join(p for p in (item.get("addr1"), item.get("addr2")) if p)

# 나머지는 없으면 빈 문자열로 보정
title = item.get("title") or "관광지"
tel = item.get("tel") or ""
image = item.get("firstimage") or ""
```

- 좌표(`mapx`/`mapy`)가 없거나 숫자로 변환되지 않는 항목은 **지도에 표시할 수 없으므로 건너뜁니다**.
- `contentid` 기준으로 중복을 제거합니다(같은 관광지가 여러 페이지에 걸쳐 올 수 있음).
- 페이지네이션은 `numOfRows`(페이지당 건수) + `pageNo`(페이지 번호)로 처리합니다.

---

## 5. 자주 헷갈리는 필드 요약

| 헷갈리는 쌍 | 구분 기준 |
|---|---|
| `mapx` vs `mapy` | x = 경도(lng), y = 위도(lat) |
| `areacode` vs `lDongRegnCd` | 앞은 Tour API 코드(광주 5/전남 38), 뒤는 법정동 코드(현재 응답은 광주·전남 모두 12) |
| `cat1~3` vs `lclsSystm1~3` | 앞은 구분류, 뒤는 신분류 — 하나만 사용 |
| `firstimage` vs `firstimage2` | 앞은 원본(팝업용), 뒤는 썸네일(목록용) |
| `createdtime` vs `modifiedtime` | 등록 시각 vs 최종 수정 시각 |
