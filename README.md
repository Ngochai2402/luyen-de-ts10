# Luyện Đề TS10 · Trung Tâm Hưng Phương

Hệ thống ôn thi tuyển sinh lớp 10 với Thầy Toán AI đồng hành, bám sát đáp án chuẩn, không dùng kiến thức ngoài chương trình.

## 📦 Bộ gói này có gì?

```
luyen-de-ts10/
├── app/
│   ├── index.html          ← Giao diện web (đã nhúng sẵn Đề 1 để demo offline)
│   ├── server.js           ← Backend Node.js (Express + Claude API, deploy Railway)
│   └── package.json        ← Dependencies
├── data/
│   └── de-1.json           ← Đề 1 đầy đủ 7 bài (mẫu)
├── tools/
│   └── extract_de.py       ← Script Python để tự extract 47 đề còn lại
└── README.md               ← File này
```

## 🚀 Cách chạy demo

### Cách 1: Mở file HTML trực tiếp (nhanh nhất, để xem trước)

Mở `app/index.html` trong trình duyệt. Demo hoạt động **offline** (AI trả lời bằng dữ liệu đã nhúng).

### Cách 2: Chạy backend thật (để test với Claude API)

```bash
cd app/
npm install
export ANTHROPIC_API_KEY="sk-ant-..."
node server.js
```

Rồi sửa `index.html` để gọi `/api/chat` thay vì mock — chi tiết trong phần "Chuyển từ demo sang thật" bên dưới.

## 🔧 Extract 47 đề còn lại

Cài đặt:
```bash
pip install anthropic pdfplumber
```

Chạy:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
cd tools/
# Copy file PDF đáp án vào cùng thư mục
cp /đường/dẫn/ĐÁP_ÁN_BỘ_ĐỀ.pdf ./

# Quét để cập nhật bản đồ trang của 48 đề
python3 extract_de.py --scan

# Extract từng đề (test)
python3 extract_de.py --de 2
python3 extract_de.py --de 3,4,5

# Hoặc chạy toàn bộ (ước chừng $15-25)
python3 extract_de.py --all
```

Output: file `data/de-{N}.json` cho mỗi đề.

**Quan trọng**: Sau khi extract, anh Hải nên **duyệt lại mỗi JSON** — đặc biệt các phần:
- Công thức LaTeX (có thể AI parse hơi lệch)
- Gợi ý cấp 1, cấp 2 (đôi khi AI quá dài dòng hoặc hơi lệch)
- Hình vẽ (AI chỉ ghi chú thôi, không vẽ được)

## 🚀 Deploy lên Railway

1. Push code lên GitHub:
```bash
cd app/
git init && git add . && git commit -m "Initial"
git remote add origin https://github.com/USER/luyen-de-ts10.git
git push -u origin main
```

2. Trên Railway:
- Tạo project mới → Deploy từ GitHub
- Thêm biến môi trường `ANTHROPIC_API_KEY`
- Railway tự detect Node.js và chạy `npm start`

3. Cấu hình tên miền: `onthi.toanhinh.com` trỏ về Railway domain.

## 🔐 Tích hợp đăng nhập WordPress

Trong `server.js`, thêm middleware xác thực:

```javascript
app.use('/api/chat', async (req, res, next) => {
  // Verify JWT token từ WordPress
  const token = req.headers['authorization']?.replace('Bearer ', '');
  const user = await verifyWpToken(token);
  if (!user) return res.status(401).json({ error: 'Chưa đăng nhập' });
  req.user = user;
  next();
});
```

Dùng plugin `jwt-authentication-for-wp-rest-api` cho WordPress → sinh JWT token khi HS đăng nhập → frontend đính kèm token mỗi request.

## 💰 Chi phí dự kiến

- **Extract 48 đề (1 lần)**: ~$15-25 với Claude Sonnet 4.6
- **Hàng tháng (100 HS × 5 câu/ngày)**: ~$50-60 với Haiku 4.5 + prompt caching

## 🛡️ Grounding — AI không được "đi lệch"

System prompt ràng buộc chặt:
1. Chỉ dùng dữ liệu trong JSON của từng bài (không dùng kiến thức ngoài)
2. Whitelist phương pháp được phép (Vi-et, Delta, ...)
3. Từ chối kiến thức lớp 11 (đạo hàm, tích phân, ...)
4. Khi không chắc → nói "hỏi thầy Hải trực tiếp"

## 🔄 Chuyển từ demo sang thật

File `index.html` hiện dùng mock AI. Để chuyển sang thật, sửa hàm `sendToAI`:

```javascript
async function sendToAI(userMsg) {
  chatHistory.push({ role: 'user', content: userMsg });
  renderChat();

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      de_so: currentDe,
      bai_so: currentBai,
      history: chatHistory.slice(0, -1),
      user_message: userMsg,
      user_id: 'HS_ID_TỪ_WP'
    })
  });
  const data = await res.json();
  chatHistory.push({ role: 'assistant', content: data.response });
  renderChat();
}
```

## 📊 Dashboard giáo viên (tuần 3-4)

Endpoint `/api/logs` đã có sẵn. Cần dựng thêm 1 trang `/admin.html`:
- Xem HS nào đang hỏi gì
- Thống kê câu sai nhiều
- Cảnh báo HS lạm dụng "Xem lời giải"

## ⚠️ Lưu ý

- File `index.html` trong bản demo có **embed sẵn dữ liệu Đề 1** để chạy offline. Bản production sẽ load qua API `/api/de/:de_so`.
- Các "mock response" trong JS chỉ để demo. Khi deploy thật, xóa hàm `mockAIResponse` và dùng fetch API.
- `extract_de.py` chạy Sonnet nên đắt hơn Haiku 3x — nhưng chỉ chạy 1 lần nên chấp nhận được vì cần chính xác cao.

## 🎯 Lộ trình 1 tháng

| Tuần | Việc |
|---|---|
| 1 | Chạy `extract_de.py --all` → duyệt 48 đề |
| 2 | Deploy Railway + tích hợp WP login |
| 3 | Test với 2-3 HS thân → tuning prompt |
| 4 | Mở cả lớp, dựng dashboard GV |

---

Thầy Hải · Hưng Phương · Tháng 4/2026
