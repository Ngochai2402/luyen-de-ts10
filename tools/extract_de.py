#!/usr/bin/env python3
"""
extract_de.py — Trích xuất đề thi TS10 từ PDF thành JSON có cấu trúc

Chạy với API key của anh Hải:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 extract_de.py --de 2
    python3 extract_de.py --de 2,3,4
    python3 extract_de.py --all     # Chạy toàn bộ 48 đề

Requires:
    pip install anthropic pdfplumber pillow
"""

import os
import sys
import json
import base64
import argparse
import subprocess
import tempfile
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("❌ Thiếu thư viện anthropic. Cài: pip install anthropic")
    sys.exit(1)

# ================ CẤU HÌNH ================
PDF_PATH = "ĐA_P_A_N_BO___ĐE___TUYE__N_SINH_10_TP_HCM_2.pdf"
OUTPUT_DIR = "data"
MODEL = "claude-sonnet-4-6"  # Dùng Sonnet để extract (cần độ chính xác cao)
MAX_TOKENS = 8000

# Trang bắt đầu mỗi đề (anh Hải cần chạy find_de_pages() một lần để cập nhật)
# Dữ liệu mẫu cho 48 đề (anh Hải có thể điều chỉnh)
DE_PAGE_MAP = {
    1: (1, 6), 2: (7, 14), 3: (15, 21), 4: (22, 26), 5: (27, 34),
    # ... Anh Hải tự điền tiếp 43 đề còn lại bằng hàm find_de_pages()
}

# ================ PROMPT EXTRACT ================
EXTRACT_SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất đề thi Toán lớp 9 TS10 từ PDF.

Nhiệm vụ: Đọc các ảnh trang PDF (là đề + lời giải được gõ bằng LaTeX) và xuất ra JSON có cấu trúc chính xác.

QUY TẮC BẮT BUỘC:
1. Dùng LaTeX chuẩn với dấu $ cho công thức inline, $$ cho công thức display
2. Chuyển \\dfrac, \\cdot, \\Rightarrow, \\Leftrightarrow đúng chuẩn
3. KHÔNG bịa số liệu — nếu không đọc được rõ, ghi "[không rõ]"
4. Giữ nguyên toàn bộ lời giải của tài liệu — KHÔNG tóm tắt, KHÔNG sáng tạo
5. Tạo thêm:
   - "goi_y_cap_1": hướng suy nghĩ chung, 2-3 câu
   - "goi_y_cap_2": các bước cụ thể, rõ ràng
   - "phuong_phap_duoc_dung": liệt kê phương pháp từ lời giải
   - "kien_thuc_lien_quan": các định lý/công thức được dùng
   - "cau_dan": 5 nhóm câu dẫn học sinh bấm nhanh (xem chi tiết bên dưới)
6. "co_hinh_ve": true/false — đề có hình vẽ, biểu đồ, bảng

## Quy tắc "cau_dan" (CỰC KỲ QUAN TRỌNG)

Mỗi bài phải có đủ 5 nhóm câu dẫn, **CỤ THỂ cho nội dung bài đó** (KHÔNG được dùng câu chung chung):

**khoi_dong** (3 câu — khi HS chưa biết bắt đầu):
  - Phải dùng từ khóa của bài (VD bài Viète: "Em quên công thức Viète rồi")
  - Không dùng: "Em chưa hiểu đề" (quá chung)
  - Dùng: "Em chưa hiểu 'tung độ nhỏ hơn hoành độ' nghĩa là gì"

**dinh_huong** (3 câu — khi HS có ý, muốn xác nhận):
  - Dạng: "Em định [làm cụ thể] — đúng hướng không?"
  - VD: "Em định tính Δ = b² - 4ac rồi so sánh với 0 — đúng không?"

**kiem_tra** (3 câu — khi HS đã có đáp án cụ thể):
  - Nêu luôn đáp số cụ thể để HS đối chiếu
  - VD: "Em ra x = 2 và y = 1 — đáp án có đúng không?"
  - VD: "Em tính V thùng = 3234 cm³ — có đúng không?"

**go_bi** (3 câu — các chỗ HS thường sai cụ thể):
  - VD: "Em không biết biến đổi x²/4 - x + 1 = 0"
  - VD: "Em tính trung bình bị sai do cộng nhầm"

**loi_giai** (3 mục cố định, KHÔNG đổi):
  - "📎 Xem gợi ý cấp 1 (hướng làm)."
  - "📎 Xem gợi ý cấp 2 (các bước chính)."
  - "📎 Xem lời giải đầy đủ."

Output: chỉ JSON, không có text nào khác, bắt đầu bằng { và kết thúc bằng }.

Schema:
{
  "de_so": <int>,
  "cum": <int>,
  "nam_hoc": "2026-2027",
  "nguon": "Hội đồng bộ môn Toán TP.HCM",
  "bai": [
    {
      "bai_so": <int>,
      "diem": <float>,
      "chu_de": "<string>",
      "de_bai": "<LaTeX>",
      "phuong_phap_duoc_dung": ["<string>", ...],
      "kien_thuc_lien_quan": ["<string>", ...],
      "dap_so": "<LaTeX>",
      "goi_y_cap_1": "<text>",
      "goi_y_cap_2": "<text>",
      "loi_giai_day_du": "<LaTeX/Markdown>",
      "cau_dan": {
        "khoi_dong": ["<cụ thể cho bài>", "<cụ thể cho bài>", "<cụ thể cho bài>"],
        "dinh_huong": ["<cụ thể cho bài>", "<cụ thể cho bài>", "<cụ thể cho bài>"],
        "kiem_tra": ["<cụ thể cho bài, có đáp số>", "<cụ thể cho bài>", "<cụ thể cho bài>"],
        "go_bi": ["<cụ thể cho bài>", "<cụ thể cho bài>", "<cụ thể cho bài>"],
        "loi_giai": [
          "📎 Xem gợi ý cấp 1 (hướng làm).",
          "📎 Xem gợi ý cấp 2 (các bước chính).",
          "📎 Xem lời giải đầy đủ."
        ]
      },
      "co_hinh_ve": <bool>,
      "ghi_chu_hinh": "<string>" (nếu co_hinh_ve)
    }
  ]
}
"""

def find_de_pages():
    """Tìm trang bắt đầu của mỗi đề trong file PDF."""
    import pdfplumber
    import re
    print("🔍 Đang quét PDF tìm vị trí các đề...")
    result = {}
    with pdfplumber.open(PDF_PATH) as pdf:
        total = len(pdf.pages)
        print(f"   Tổng: {total} trang")
        de_starts = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            m = re.search(r"ĐỀ THAM KHẢO TUYỂN SINH 10 SỐ (\d+)", text)
            if m:
                num = int(m.group(1))
                if num not in result:
                    de_starts.append((num, i + 1))
                    result[num] = [i + 1, None]
        # Tính trang kết thúc mỗi đề = trang bắt đầu đề tiếp theo - 1
        for j in range(len(de_starts)):
            num, start = de_starts[j]
            end = de_starts[j + 1][1] - 1 if j + 1 < len(de_starts) else total
            result[num] = (start, end)
    print(f"   ✅ Tìm thấy {len(result)} đề")
    return result


def render_pages_to_images(pdf_path, start, end, out_dir):
    """Render các trang PDF thành ảnh PNG."""
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([
        "pdftoppm", "-png", "-r", "150",
        "-f", str(start), "-l", str(end),
        pdf_path, f"{out_dir}/p"
    ], check=True)
    imgs = sorted(Path(out_dir).glob("p-*.png"))
    return imgs


def extract_de(de_so: int, page_map: dict, client: anthropic.Anthropic):
    """Extract 1 đề thành JSON bằng Claude Vision."""
    if de_so not in page_map:
        print(f"⚠️  Không tìm thấy đề {de_so} trong page_map")
        return None

    start, end = page_map[de_so]
    print(f"\n📖 Đang xử lý Đề {de_so} (trang {start}-{end})...")

    # Render ảnh
    with tempfile.TemporaryDirectory() as tmpdir:
        imgs = render_pages_to_images(PDF_PATH, start, end, tmpdir)
        print(f"   🖼️  {len(imgs)} trang đã render")

        # Encode base64 cho Claude Vision
        content = []
        for img in imgs:
            with open(img, 'rb') as f:
                data = base64.standard_b64encode(f.read()).decode()
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": data}
            })
        content.append({
            "type": "text",
            "text": f"Hãy trích xuất Đề TS10 Số {de_so} từ các trang trên thành JSON theo schema đã cho. Chỉ trả về JSON, không có text khác."
        })

        # Gọi API
        print(f"   🤖 Gọi Claude {MODEL}...")
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=EXTRACT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}]
        )
        raw = resp.content[0].text.strip()

        # Gỡ markdown fence nếu có
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        # Parse JSON
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"   ❌ Lỗi parse JSON: {e}")
            print(f"   Raw output: {raw[:500]}")
            # Lưu raw để debug
            with open(f"{OUTPUT_DIR}/de-{de_so}-raw.txt", "w") as f:
                f.write(raw)
            return None

        # Ghi file
        out_path = f"{OUTPUT_DIR}/de-{de_so}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Đã lưu: {out_path} ({len(data.get('bai', []))} bài)")
        return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--de", help="Số đề cần xử lý (vd: 2 hoặc 2,3,4)")
    parser.add_argument("--all", action="store_true", help="Xử lý tất cả 48 đề")
    parser.add_argument("--scan", action="store_true", help="Chỉ quét tìm vị trí các đề")
    args = parser.parse_args()

    # Kiểm tra API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Chưa có ANTHROPIC_API_KEY. Chạy:")
        print('   export ANTHROPIC_API_KEY="sk-ant-..."')
        sys.exit(1)

    # Kiểm tra PDF
    if not os.path.exists(PDF_PATH):
        print(f"❌ Không tìm thấy file: {PDF_PATH}")
        print("   Đặt file PDF đáp án vào cùng thư mục với script này.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Quét để cập nhật DE_PAGE_MAP đầy đủ
    page_map = find_de_pages()
    # Ghi ra file để xem
    with open(f"{OUTPUT_DIR}/de_page_map.json", 'w') as f:
        json.dump(page_map, f, indent=2)
    print(f"   💾 Đã lưu bản đồ trang: {OUTPUT_DIR}/de_page_map.json")

    if args.scan:
        print("\n✅ Xong. Kiểm tra file de_page_map.json.")
        return

    client = anthropic.Anthropic()

    # Xác định đề cần chạy
    if args.all:
        de_list = sorted(page_map.keys())
    elif args.de:
        de_list = [int(x) for x in args.de.split(",")]
    else:
        parser.print_help()
        sys.exit(1)

    print(f"\n🎯 Xử lý {len(de_list)} đề: {de_list}")
    ok = 0
    for de_so in de_list:
        try:
            data = extract_de(de_so, page_map, client)
            if data:
                ok += 1
        except Exception as e:
            print(f"   ❌ Lỗi đề {de_so}: {e}")

    print(f"\n🏁 Xong: {ok}/{len(de_list)} đề đã xử lý thành công")
    print(f"   Files lưu ở: {OUTPUT_DIR}/")
    print("\n💡 Bước tiếp theo:")
    print("   1. Mở mỗi file de-N.json để duyệt & chỉnh sửa lời giải")
    print("   2. Đưa các JSON vào ứng dụng luyện đề")


if __name__ == "__main__":
    main()
