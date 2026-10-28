# 광주·전남 스마트 관광 대시보드

광주·전남 관광지와 반려동물 동반 정보, 전남 장애인 편의시설(무장애) 정보를 한 화면에서 탐색하는 Streamlit 대시보드입니다.

## 주요 기능

- 한국관광공사 `areaBasedList2` 관광지 조회 (광주 5 / 전남 38)
- `detailPetTour2` 반려동물 동반 정보 통합
- 전남 장애인 편의시설 `getHandicapAmenityList` 통합
  - 시설명·좌표 기반으로 관광지와 매칭
  - 매칭된 관광지에 `무장애/휠체어 가능` 표시
  - 지도에 장애인 편의시설 레이어 표시 (선택)
  - 편의시설 원본 목록 조회 및 CSV 다운로드
- 관광지·반려동물·무장애 통합 CSV 다운로드
- 오픈API 실패 시 샘플 CSV로 자동 폴백

## 데이터 출처

- [한국관광공사 Tour API](https://apis.data.go.kr/B551011/KorService2)
- [전남광주통합특별시 장애인 편의시설 용도별 안내 데이터](https://www.data.go.kr/data/15074680/openapi.do)

> 장애인 편의시설 API는 관광공사 API와 별도로 **활용신청**이 필요합니다. 활용신청 후 발급된 서비스키를 `.env`에 추가하세요.

## API 필드 정리

`areaBasedList2` 응답 필드의 의미, 앱 컬럼 매핑, 헷갈리는 필드 비교는
[docs/areaBasedList2_fields.md](docs/areaBasedList2_fields.md) 에 정리되어 있습니다.

## 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Secrets 설정

서비스 키는 **Streamlit secrets**(`.streamlit/secrets.toml`)로 관리합니다. `.env` 파일은 더 이상 사용하지 않습니다.

1. `.streamlit` 폴더에 `secrets.toml` 파일을 만듭니다.
2. `.streamlit/secrets.toml.example` 내용을 복사해 실제 키를 입력합니다.

```toml
TOUR_API_SERVICE_KEY = "관광공사_서비스키"
```

- `secrets.toml` 은 **Git에 커밋되지 않습니다** (`.gitignore` 등록됨).
- `TOUR_API_SERVICE_KEY` 가 secrets 에 없으면 OS 환경변수에서 한 번 더 찾습니다.
- Streamlit Cloud 배포 시에는 **App > Settings > Secrets** 에 같은 내용을 붙여넣으면 됩니다.

```bash
# 예시 파일 복사 (Windows PowerShell)
New-Item -ItemType Directory -Force .streamlit | Out-Null
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

## 실행

```bash
streamlit run app.py
```

## 캐시

- `data/cache/pet_tour_index.json`: 반려동물 상세 인덱스 (24시간)
- `data/cache/handicap_facilities.json`: 장애인 편의시설 목록 (24시간)

캐시는 Git에 포함되지 않습니다. 최초 실행 시 API 수집에 시간이 걸릴 수 있으며, 이후에는 캐시를 재사용합니다.

## 무장애 정보 통합 방식

1. 장애인 편의시설 API에서 시설 목록을 수집합니다.
2. 관광지와 시설의 **이름 유사도**와 **좌표 거리**를 함께 비교합니다.
   - 이름 유사도 0.85 이상 (좌표가 있으면 1km 이내)
   - 이름 유사도 0.65 이상 + 200m 이내
   - 50m 이내 + 이름 유사도 0.4 이상
   - API 원본에 좌표가 없을 때: 이름 유사도 0.65 이상
3. 매칭된 관광지에만 `wheelchair=True`와 편의시설 상세 정보를 부여합니다.
4. 매칭되지 않은 관광지는 기존 값을 유지합니다.

> API 문서상 지역 코드는 전남 22개 시·군 기준입니다. 따라서 광주 지역 관광지는 장애인 편의시설 매칭 대상에서 제외됩니다.

## 폴더 구조

- `/data`: 데이터 파일 및 로컬 캐시
- `/src`: 소스 코드
- `/tests`: 테스트 코드
- `/requirements`: 의존성 관리 파일
- `/docs`: 문서
- `app.py`: Streamlit 대시보드 본체
- `handicap.py`: 장애인 편의시설 API 연동 및 매칭 모듈
