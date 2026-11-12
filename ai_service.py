
import json

from openai import OpenAI

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


def analyze_email(email_body):
    """고객 이메일을 분석해 category, summary, language, reply를 담은 dict를 반환한다."""
    client = OpenAI()

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

    return json.loads(response.output_text)
