
# 백신(Avast 등)의 HTTPS 검사 인증서도 믿도록 Windows 인증서 저장소를 사용한다.
# Gmail·OpenAI 연결보다 먼저 실행되어야 하므로 가장 위에 둔다.
import truststore
truststore.inject_into_ssl()

import streamlit as st
from dotenv import load_dotenv
from ai_service import analyze_email
from gmail_service import GmailAuthError, get_recent_emails

load_dotenv()

st.set_page_config(
    page_title="Namsanemailagent",
    page_icon=":material/mail:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


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
        except GmailAuthError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Gmail 연결 오류: {e}")

    emails = st.session_state.emails

    if emails:
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

    else:
        email_body = ""
        current_id = "empty"
        st.info("새로고침을 눌러 Gmail 받은 편지함을 불러오세요.")

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
        with st.spinner("AI가 이메일을 분석하고 있어요..."):
            result = analyze_email(email_body)

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
