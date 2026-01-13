# ⚓ NaviCard AI

**해군 정보 자동화 시스템** - 전 세계 해군/방산 뉴스를 AI가 분석하여 전문가용 인텔리전스 카드를 매일 생성합니다.

## ✨ 주요 기능

- 🌐 **자동 뉴스 수집**: Naval News, USNI, Defense News, Janes 실시간 모니터링
- 🎯 **스마트 필터링**: 함정/USV/제어 시스템 관련만 선별
- 🧠 **AI 심층 분석**: Gemini 3 Flash 기반 전문가 수준 요약
- 🎨 **AI 이미지 생성**: 뉴스 주제 기반 시네마틱 일러스트
- 💬 **대화형 대시보드**: Streamlit 기반 AI 챗봇
- 📧 **자동 이메일 발송**: 매일 오전 지정 시간에 배달

## 🚀 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 3. 실행
python src/main.py

# 4. 대시보드 (선택)
python -m streamlit run report_dashboard.py
```

## 🔧 환경 변수

| 변수명 | 설명 |
|--------|------|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `EMAIL_USER` | 발송 Gmail 주소 |
| `EMAIL_PASSWORD` | Gmail 앱 비밀번호 |
| `RECIPIENT_EMAILS` | 수신자 이메일 (콤마 구분) |

## 📁 프로젝트 구조

```
src/
├── main.py           # 메인 오케스트레이터
├── feed_parser.py    # RSS 뉴스 수집
├── summarizer.py     # Gemini 3 AI 분석
├── image_generator.py # Gemini 2.5 이미지 생성
└── mailer.py         # 이메일 발송
```

## ⏰ 자동화

GitHub Actions를 통해 매일 오전 7시(KST) 자동 실행됩니다.
수동 실행: Actions 탭 → "NaviCard AI Daily Run" → Run workflow

## 📜 라이선스

Private Project

---
*Powered by Google Gemini AI* 🤖
