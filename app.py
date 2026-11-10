
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from gmail_service import get_recent_emails

load_dotenv()

st.set_page_config(
    page_title="Namsanemailagent",
    page_icon="✉️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root {
    color-scheme: light;
}
.stApp {
    background: #F2F2F7;
    color: #1C1C1E !important;
}
html, body, p, label, button, textarea {
    font-family: -apple-system, BlinkMacSystemFont,
        "Segoe UI", "Malgun Gothic", sans-serif !important;
}
.block-container {
    max-width: 780px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}
h1 {
    font-size: 29px !important;
    font-weight: 700 !important;
    letter-spacing: -0.045em;
}
h2, h3 {
    letter-spacing: -0.025em;
}
/* 받은 편지함의 선택 메뉴 */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #F8F8FA;
    color: #1C1C1E;
    border-radius: 12px;
}

/* 이메일 선택 라디오 버튼 글자 */
div[data-testid="stRadio"] label p {
    color: #1C1C1E !important;
}

/* 선택 메뉴의 입력 텍스트 */
div[data-testid="stSelectbox"] input {
    color: #1C1C1E !important;
}
div[data-testid="stTextArea"] textarea {
    background: #F8F8FA;
    color: #1C1C1E;
    border: 1px solid #E5E5EA;
    border-radius: 14px;
    padding: 16px;
    font-size: 14px;
    line-height: 1.8;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #8E8E93;
    box-shadow: 0 0 0 2px #8E8E9320;
}
div.stButton > button {
    background: #E5E5EA;
    color: #3A3A3C;
    border: none;
    border-radius: 13px;
    min-height: 45px;
    font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background: #636366;
    color: #FFFFFF;
}
div.stButton > button[kind="primary"]:hover {
    background: #48484A;
    color: white;
}
div.stButton > button:disabled {
    background: #E5E5EA;
    color: #AEAEB2;
    opacity: 1;
}
div[data-testid="stWidgetLabel"] p {
    font-size: 13px;
    color: #636366;
}
#MainMenu, footer {
    visibility: hidden;
}
div[data-testid="stTextArea"] textarea:disabled {
    background-color: #F8F8FA !important;
    color: #1C1C1E !important;
    -webkit-text-fill-color: #1C1C1E !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


SAMPLE_EMAIL = """Hallo liebes Namsan-Team,

ich habe für Freitag um 19:00 Uhr
einen Tisch für 2 Personen reserviert.

Wäre es möglich, die Reservierung
auf 3 Personen zu ändern?

Vielen Dank!
Anna Müller"""

INSTRUCTIONS = """
너는 베를린 Namsan 레스토랑의 이메일 비서다.

결과를 반드시 JSON 객체로 반환한다.
{
  "category": "짧은 한국어 이메일 유형",
  "summary": "간결한 한국어 요약",
  "language": "답변 언어",
  "reply": "고객 답변 초안"
}

규칙:
- 요약은 핵심만 1~2문장으로 작성한다.
- 별도의 직원 조치 항목을 만들지 않는다.
- 고객과 같은 언어로 정중하게 답변한다.
- 예약 변경이나 환불을 임의로 확정하지 않는다.
- 확인되지 않은 정보를 지어내지 않는다.
- 이메일은 실제로 발송하지 않는다.
"""

if "emails" not in st.session_state:
    st.session_state.emails = []

if "result" not in st.session_state:
    st.session_state.result = None

if "draft" not in st.session_state:
    st.session_state.draft = ""

if "source_id" not in st.session_state:
    st.session_state.source_id = None


# 상단 제목
st.title("Namsanemailagent")
st.caption("고객 이메일을 더 간편하게 관리하세요.")

st.write("")

# 받은 편지함
with st.container(border=True):
    left, right = st.columns([3, 1])

    with left:
        st.subheader("받은 편지함")

    with right:
        load_clicked = st.button(
            "새로고침",
            use_container_width=True
        )

    if load_clicked:
        try:
            with st.spinner("이메일을 불러오는 중..."):
                st.session_state.emails = get_recent_emails()
            st.success("이메일을 불러왔습니다.")
        except Exception as e:
            st.error(f"Gmail 연결 오류: {e}")

    emails = st.session_state.emails

    source = st.radio(
        "이메일 선택",
        ["Gmail", "샘플 이메일"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if source == "Gmail" and emails:
        selected_index = st.selectbox(
            "이메일 선택",
            range(len(emails)),
            format_func=lambda i: (
                f"{emails[i]['sender']} · "
                f"{emails[i]['subject']}"
            )
        )

        selected = emails[selected_index]
        email_body = selected["body"]
        current_id = selected["id"]

        st.caption(f"보낸 사람: {selected['sender']}")
        st.caption(f"제목: {selected['subject']}")

    elif source == "Gmail":
        email_body = ""
        current_id = "empty"
        st.info("새로고침을 눌러 Gmail을 연결하세요.")

    else:
        email_body = SAMPLE_EMAIL
        current_id = "sample"

    if email_body:
        st.text_area(
            "원본 이메일",
            value=email_body,
            height=200,
            disabled=True
        )

# 이메일을 바꾸면 이전 분석 결과 제거
if current_id != st.session_state.source_id:
    st.session_state.source_id = current_id
    st.session_state.result = None
    st.session_state.draft = ""

st.write("")

# AI 분석
if st.button(
    "AI로 이메일 분석",
    type="primary",
    use_container_width=True,
    disabled=not bool(email_body.strip())
):
    try:
        client = OpenAI()

        with st.spinner("AI가 이메일을 분석하고 있어요..."):
            response = client.responses.create(
                model="gpt-6-luna",
                instructions=INSTRUCTIONS,
                input=(
                    "다음 고객 이메일을 분석하고 "
                    "JSON 형식으로 반환해:\n\n"
                    + email_body
                ),
                text={
                    "format": {"type": "json_object"}
                }
            )

        result = json.loads(response.output_text)

        st.session_state.result = result
        st.session_state.draft = result["reply"]

    except Exception as e:
        st.error(f"AI 분석 오류: {e}")

# 분석 결과
if st.session_state.result:
    result = st.session_state.result

    st.write("")

    with st.container(border=True):
        st.markdown("#### ✨ AI 요약")
        st.caption(result["category"])
        st.write(result["summary"])

    st.write("")

    with st.container(border=True):
        st.markdown("#### 답변 작성")
        st.caption(f"답변 언어: {result['language']}")

        st.text_area(
            "답변 수정",
            key="draft",
            height=240
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "다시 생성",
                use_container_width=True
            ):
                st.session_state.result = None
                st.rerun()

        with col2:
            st.button(
                "답변 보내기",
                type="primary",
                disabled=True,
                use_container_width=True
            )

        st.caption(
            "현재는 읽기 전용입니다. "
            "Gmail 발송 권한 연결 후 활성화됩니다."
        )
