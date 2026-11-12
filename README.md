
# Namsan email agent

베를린 한식당 Namsan의 고객 이메일 업무를
지원하는 AI 에이전트 프로젝트입니다.

## 1. 누구를 위한 에이전트인가?

Namsan email agent는 독일에 위치한 레스토랑에서
한인 사장님이 고객 이메일을 처리하는 직원을 위한 AI 업무
보조 에이전트입니다.

외국어 고객 이메일을 한국어로 간결하게 요약하고,
고객이 사용한 언어로 답변 초안을 생성합니다.

직원이 이메일을 빠르게 이해하고 답변을
작성하는 데 드는 시간을 줄이는 것이 목표입니다.

## 2. 주요 기능

- 고객 이메일 유형 분류
- 고객 요청 사항 한국어 요약
- 독일어 및 영어 답변 초안 생성
- 답변 초안 수정
- Gmail API를 이용한 이메일 조회 기능 개발

## 3. 현재 진행 상황

### 구현 완료
- Python 및 uv 개발 환경 구성
- Streamlit 웹 대시보드
- OpenAI Responses API 연결
- AI 이메일 요약 및 답변 생성
- 답변 초안 편집

### 개발 중
- Gmail OAuth 인증 및 실제 이메일 조회 검증
- Gmail 이메일 목록과 AI 분석 기능 통합
- 직원 승인 후 원본 스레드에 답장 발송
- 자동 이메일 확인 및 처리 상태 관리

현재 Gmail 받은 편지함에서 불러온 이메일만
AI로 분석하며, Gmail 연동 기능은 테스트 중입니다.

## 4. 기술 스택

- Python
- uv
- Streamlit
- OpenAI Responses API
- Gmail API
- Google OAuth 2.0

## 5. 실행 방법

필요한 라이브러리 설치:

    uv sync

프로젝트 루트에 .env 파일 생성:

    OPENAI_API_KEY=your_api_key

앱 실행:

    uv run streamlit run app.py

Gmail 연동 테스트 시 Google Cloud에서
OAuth Desktop Client를 생성하고
credentials.json 파일을 준비해야 합니다.

## 6. 보안

실제 Gmail 이메일 발송 기능은 아직
구현되지 않았습니다.
