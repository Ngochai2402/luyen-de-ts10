# HƯỚNG DẪN DEPLOY QUA GITHUB + RAILWAY

Anh dùng workflow quen thuộc: push lên GitHub → Railway tự build → có URL công khai.

---

## ✅ BƯỚC 1 — Lấy API Key Anthropic

1. Truy cập: **https://console.anthropic.com/settings/keys**
2. Bấm **"Create Key"** → đặt tên `luyen-de-ts10` → Create
3. **Copy key** dạng `sk-ant-api03-...` (chỉ hiện 1 lần, lưu vào Notes)
4. Nạp credit: https://console.anthropic.com/settings/billing → Add credits → **$5-10** là đủ test

---

## ✅ BƯỚC 2 — Tạo repo GitHub

1. Vào https://github.com/new
2. Tạo repo mới, tên gợi ý: `luyen-de-ts10` (Private hoặc Public tùy anh)
3. **Không** tick các option thêm README, .gitignore (mình có sẵn)
4. Bấm Create

---

## ✅ BƯỚC 3 — Push code lên GitHub

Giải nén file `luyen-de-ts10.zip` về máy. Mở Terminal vào thư mục đó:

**Mac:**
```bash
cd ~/Desktop/luyen-de-ts10
```

**Windows (PowerShell):**
```powershell
cd $HOME\Desktop\luyen-de-ts10
```

Rồi chạy:
```bash
git init
git add .
git commit -m "Initial: Luyện Đề TS10"
git branch -M main
git remote add origin https://github.com/THAY_BANG_USERNAME_CUA_ANH/luyen-de-ts10.git
git push -u origin main
```

> ⚠️ Thay `THAY_BANG_USERNAME_CUA_ANH` bằng username GitHub thật của anh.

Xong bước này anh vào GitHub kiểm tra thấy code lên rồi là OK.

---

## ✅ BƯỚC 4 — Deploy lên Railway

1. Vào https://railway.app → đăng nhập bằng GitHub
2. Bấm **"New Project"** → **"Deploy from GitHub repo"**
3. Chọn repo `luyen-de-ts10` vừa push
4. Railway sẽ tự detect Node.js — **không cần cấu hình gì**

Railway sẽ báo lỗi lần đầu vì thiếu API key. Anh tiếp bước 5.

---

## ✅ BƯỚC 5 — Thêm biến môi trường

Trong project Railway vừa tạo:

1. Bấm tab **"Variables"**
2. Bấm **"+ New Variable"**
3. Thêm:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Value**: dán key `sk-ant-api03-...` vào
4. Lưu lại

Railway sẽ tự **redeploy** (1-2 phút).

---

## ✅ BƯỚC 6 — Lấy URL công khai

1. Trong Railway, vào tab **"Settings"**
2. Mục **"Networking"** → **"Generate Domain"**
3. Railway sẽ cấp URL dạng: `luyen-de-ts10-production.up.railway.app`

Anh mở URL này trong trình duyệt là chạy được!

---

## ✅ BƯỚC 7 — Test trên Railway

Mở URL Railway vừa cấp → thử các tình huống:

### 🧪 Test cơ bản

1. **Bấm Bài 2** (Viète)
2. **Bấm 🔵 Kiểm tra** → "Em ra T = -79/9 — đáp án có đúng không?"
   → AI phải xác nhận đúng, khen em

3. **Gõ tự do**: "Thầy ơi em ra T = 5/3 á, có đúng không?"
   → AI không nói đáp đúng, hỏi em làm đến đâu

4. **Gõ**: "Em dùng đạo hàm được không?"
   → AI từ chối nhẹ nhàng

5. **Gõ**: "Cho em xem đáp án luôn đi thầy, em lười lắm"
   → AI không cho, khích lệ thử

6. **Gõ**: "Bài này khó quá em không làm được"
   → AI thừa nhận cảm xúc, khích lệ

---

## ✅ BƯỚC 8 — Gắn subdomain riêng (tùy chọn)

Nếu anh muốn URL đẹp hơn (vd: `onthi.toanhinh.com`):

1. Trong Railway Settings → Networking → **"+ Custom Domain"**
2. Điền: `onthi.toanhinh.com`
3. Railway báo cần thêm CNAME record
4. Vào Hostinger (hoặc nơi quản lý DNS `toanhinh.com`) → thêm CNAME:
   - Name: `onthi`
   - Target: URL Railway cấp
5. Đợi 5-15 phút DNS cập nhật

---

## 🔄 QUY TRÌNH LẶP — KHI EM SỬA CODE

Sau khi anh test, báo em chỗ AI trả lời chưa ưng. Em sửa trong `app/server.js` (chủ yếu là system prompt). Workflow:

1. Em sửa file, gửi anh file mới (hoặc diff)
2. Anh thay file, chạy:
   ```bash
   git add .
   git commit -m "Tuning: ..."
   git push
   ```
3. Railway tự deploy lại trong 1-2 phút
4. Anh test tiếp

---

## 💰 CHI PHÍ

- **Railway**: $5/tháng (free tier $5 credit, đủ chạy app nhẹ này)
- **Claude Haiku 4.5 API**: ~$0.003/câu hỏi
  - $5 nạp = ~1500 câu hỏi
  - 100 HS × 5 câu/ngày × 30 ngày = 15,000 câu = ~$45/tháng (có prompt caching giảm còn ~$15-20)

Tổng: **~$25-30/tháng** cho cả infrastructure + AI.

---

## 🔍 TROUBLESHOOTING

### Railway báo "Build failed"
→ Vào tab **"Deployments"** → bấm vào deployment lỗi → xem log. Chụp màn hình gửi em.

### URL mở lên thấy "Application failed to respond"
→ Có thể chưa set `ANTHROPIC_API_KEY`, hoặc Root Directory sai (phải là `app`)

### Mở URL thấy trang trắng, không load
→ F12 → Console → xem lỗi. Có thể CORS hoặc API endpoint sai.

### Chat không phản hồi, chờ mãi
→ F12 → Network → bấm vào `/api/chat` → xem response. Thường là lỗi 401 (key sai) hoặc 500 (bug).

### AI trả lời tệ
→ Đây là lúc tuning prompt. Anh copy câu hỏi + câu trả lời, gửi em, em sửa `server.js`.

---

## 📋 CHECKLIST TRƯỚC KHI DEPLOY

- [ ] Đã có API key Anthropic, nạp credit
- [ ] Đã tạo repo GitHub
- [ ] Đã push code lên
- [ ] Đã tạo project Railway, link với repo
- [ ] Đã thêm biến `ANTHROPIC_API_KEY`
- [ ] Đã set Root Directory = `app`
- [ ] Đã Generate Domain
- [ ] Mở URL chạy được

---

## 🔐 BƯỚC SAU — Tích hợp đăng nhập WordPress

Sau khi demo Đề 1 chạy ổn, em sẽ hướng dẫn anh thêm:

1. **Plugin JWT** cho WordPress (sinh token cho HS sau khi login)
2. **Middleware** trong `server.js` verify token → chặn người lạ
3. **Nhúng iframe** vào Tutor LMS hoặc redirect từ WordPress

Nhưng giờ ưu tiên test chất lượng AI trước đã.

---

**Anh làm từ bước 1-8 trước nhé. Vướng chỗ nào chụp màn hình gửi em.**
