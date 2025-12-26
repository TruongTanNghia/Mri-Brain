import os
from typing import Tuple, Optional
from config import OPENAI_API_KEY

_KB = {
    "glioma":       "Khối u phát triển từ tế bào thần kinh đệm, có thể lành hoặc ác tính; cần đánh giá mức độ lan rộng bằng MRI có tiêm thuốc tương phản.",
    "meningioma":   "Khối u thường lành tính phát triển từ màng não; phẫu thuật cắt bỏ có thể giúp khỏi hoàn toàn.",
    "pituitary":    "U tuyến yên thường ảnh hưởng nội tiết; cần làm thêm xét nghiệm hormone và MRI vùng yên.",
    "notumor":      "Không phát hiện tổn thương dạng u rõ ràng; nên theo dõi định kỳ để đảm bảo ổn định.",
    "background":   "Ảnh nền hoặc tín hiệu nhiễu; cần chụp lại hoặc kiểm tra chất lượng hình ảnh MRI."
}

def fallback_tip(label: str) -> str:
    return _KB.get(label, "Cần tham khảo ý kiến bác sĩ chuyên khoa để đánh giá thêm hình ảnh MRI và định hướng điều trị phù hợp.")

def generate_tips_html(disease_label: str, max_tokens: int = 400) -> Tuple[Optional[str], Optional[str]]:
    """
    Trả về (tips_html, error_text). Nếu thành công tips_html là chuỗi HTML (<ul><li>..</li></ul>)
    Nếu thất bại trả về (None, error_message) và bạn có thể gọi fallback_tip.
    """
    if not OPENAI_API_KEY:
        return None, "NO_API_KEY"

    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        prompt = f"""
        Bạn là bác sĩ chuyên khoa thần kinh và chẩn đoán hình ảnh MRI não.
        Mô hình AI đã phát hiện loại bệnh: {disease_label}.
        Hãy TRẢ VỀ CHÍNH XÁC MỘT ĐOẠN HTML CHỈ GỒM MỘT DANH SÁCH BULLET: <ul><li>...</li></ul>

        Yêu cầu:
        - Giọng điệu nhẹ nhàng, mang tính tư vấn y học, hướng đến bệnh nhân (trấn an, giải thích, định hướng tiếp theo).
        - Tổng cộng có 3 mục (<li>):
            1) Giải thích ngắn gọn về loại bệnh và tác nhân hoặc nguyên nhân hình thành.
            2) Mô tả ngắn về quá trình tiến triển và các xét nghiệm, chẩn đoán cần thiết để làm rõ hơn.
            3) Gợi ý hướng điều trị, chăm sóc và lời khuyên tinh thần cho bệnh nhân.
        - Bôi đậm các cụm từ chính bằng thẻ HTML <b>...</b> như: <b>Nguyên nhân</b>,.
        - KHÔNG thêm tiêu đề hoặc văn bản ngoài thẻ <ul>.
        - KHÔNG chèn CSS, Markdown, hoặc code fence.
        - KHÔNG dùng ký hiệu ** để bôi đậm. Chỉ dùng thẻ HTML <b>...</b>.
        - Trả về đúng định dạng HTML: <ul><li>...</li></ul>
        """.strip()

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=max_tokens
        )

        tips_html = resp["choices"][0]["message"]["content"].strip()
        return tips_html, None

    except Exception as e:
        return None, str(e)
