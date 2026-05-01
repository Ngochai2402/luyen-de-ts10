# CLAUDE.md

## 🌐 Hạ tầng dịch vụ thực tế (UPDATED)

Đây là setup hạ tầng thực tế đang dùng. Khi triển khai, MUST tuân theo phân chia này:

### 🟢 HOSTINGER — Trái tim hệ thống
**Vai trò:** Lưu trữ dữ liệu chính + Web app
**Đang chạy:**
- WordPress + Tutor LMS (đã sẵn sàng)
- MySQL database (sẽ chứa 15 bảng hp_*)
- Plugin tutor-lms-staff-api.php (cũ, sẽ mở rộng)
- Domain chính: toanhinh.com

**Sẽ deploy ở đây:**
- Plugin hp-api.php (mở rộng, không thay thế plugin cũ)
- 4 PWA: giáo viên, thủ quỹ, quản lý, phụ huynh
- Toàn bộ database hp_*

**Quy tắc:**
- KHÔNG cài Node.js, Python, n8n trên Hostinger (shared hosting)
- KHÔNG chạy script background, cron job phức tạp
- Chỉ PHP + MySQL + file tĩnh (HTML/CSS/JS)
- Upload qua File Manager hoặc FTP

### 🟡 TINO VPS N8N — Automation Engine
**Vai trò:** Tự động hóa workflow + ZNS
**Gói đang dùng:** VPS N8N cài sẵn của Tino (~179k/tháng)
**Đang chạy:**
- n8n self-hosted (đã có sẵn workflow)
- Linux đầy đủ, SSH access

**Sẽ deploy ở đây:**
- Workflow gửi ZNS khi HS vắng học
- Workflow nhắc học phí qua ZNS
- Workflow trigger từ webhook khi có sự kiện trong MySQL Hostinger

**Quy tắc:**
- Mọi automation chạy ở đây
- n8n gọi MySQL Hostinger qua kết nối từ xa (đã setup)
- n8n nhận webhook từ plugin Hostinger
- KHÔNG lưu data quan trọng trên VPS này (chỉ workflow logs)

### 🔵 RAILWAY — Specialized Compute
**Vai trò:** Tính toán chuyên biệt cần Linux/Chromium
**Đang chạy:**
- XeLaTeX compiler (compile đề Toán PDF)
- Puppeteer (chụp screenshot, render HTML → PDF)

**Quy tắc:**
- CHỈ dùng cho compute, không lưu data
- Plugin Hostinger gọi qua HTTP API khi cần
- KHÔNG cài thêm n8n hay app khác (đã có Tino)
- KHÔNG kết nối database trực tiếp từ Railway

## 🔄 Luồng dữ liệu giữa 3 dịch vụ

```
USER ACTION (Giáo viên điểm danh)
    ↓
PWA gửi POST request
    ↓
HOSTINGER: Plugin hp-api.php nhận → INSERT vào MySQL → Gọi webhook Tino n8n
    ↓ (HTTP POST webhook)
TINO VPS N8N: Query MySQL Hostinger lấy SĐT phụ huynh → Call ZNS API → UPDATE zns_sent=1
    ↓
PHỤ HUYNH NHẬN ZNS

(Khi cần PDF/đề Toán)
HOSTINGER plugin → Gọi Railway API → XeLaTeX/Puppeteer → return PDF → gửi user
```

## 🔐 Credentials & Endpoints (KHÔNG commit, dùng .env)

```env
# Hostinger MySQL (DATA CHÍNH)
HOSTINGER_DB_HOST=...
HOSTINGER_DB_USER=...
HOSTINGER_DB_PASSWORD=...
HOSTINGER_DB_NAME=...

# Hostinger API
API_BASE_URL=https://toanhinh.com/wp-json/hp-api/v1
API_KEY=ThayHai_BaoMat_2026!@#

# Tino VPS N8N (AUTOMATION)
N8N_BASE_URL=https://[your-tino-vps-domain]
N8N_WEBHOOK_ATTENDANCE=https://[your-tino-vps]/webhook/attendance
N8N_WEBHOOK_TUITION=https://[your-tino-vps]/webhook/tuition
N8N_API_KEY=...

# Railway (COMPUTE)
RAILWAY_LATEX_URL=https://[your-railway-app].railway.app/compile
RAILWAY_PUPPETEER_URL=https://[your-railway-app].railway.app/screenshot

# ZNS (qua Tino n8n)
ZNS_APP_ID=...
ZNS_SECRET=...
ZNS_TEMPLATE_ABSENCE=...
ZNS_TEMPLATE_TUITION_REMINDER=...
```

## ⚠️ QUY TẮC BẮT BUỘC khi triển khai

### 1. Phân chia trách nhiệm rõ ràng
- Cần lưu data → Hostinger MySQL
- Cần automation → Tino n8n
- Cần compute đặc biệt → Railway
- KHÔNG bao giờ trộn lẫn

### 2. Mọi truy cập database đều qua Hostinger plugin
- Tino n8n KHÔNG kết nối thẳng MySQL trừ trường hợp đặc biệt (đọc dữ liệu)
- Railway KHÔNG bao giờ kết nối MySQL
- App PWA KHÔNG bao giờ kết nối MySQL

### 3. Bảo mật webhook giữa các dịch vụ
- Tino n8n → Hostinger: dùng X-API-Key
- Hostinger → Tino n8n: dùng webhook secret
- Railway endpoints: cần authentication token

### 4. Khi gặp lỗi, kiểm tra theo thứ tự
1. Hostinger: error log trong cPanel
2. Tino VPS: journalctl -u n8n qua SSH
3. Railway: log trong dashboard Railway
4. Network: kiểm tra firewall, IP whitelist

### 5. Backup
- Hostinger MySQL: backup tự động hàng ngày + manual export trước migration
- Tino n8n: export workflow JSON định kỳ vào GitHub
- Railway: code đã trên GitHub, không cần backup riêng

## 💰 Chi phí vận hành thực tế

| Dịch vụ | Vai trò | Chi phí/tháng |
|---|---|---|
| Hostinger | WordPress + MySQL + PWA | ~50-150k |
| Tino VPS N8N | Automation + ZNS | ~179k |
| Railway | XeLaTeX + Puppeteer | ~120-250k |
| TỔNG | | ~350-580k |

So với EasyEdu (667k/tháng) → tiết kiệm + linh hoạt hơn nhiều.

## 🚫 KHÔNG làm những điều sau

1. KHÔNG đề xuất chuyển n8n từ Tino sang Railway (đã ổn định)
2. KHÔNG đề xuất gộp tất cả vào 1 VPS (mất dự phòng)
3. KHÔNG đề xuất thuê dịch vụ database riêng (MySQL Hostinger đủ tốt)
4. KHÔNG đề xuất rời Hostinger trước 6 tháng vận hành
5. KHÔNG cài WordPress lên Tino VPS (đã có ở Hostinger)

## ✅ NÊN làm những điều sau

1. Tận dụng tối đa hạ tầng hiện có
2. Test kết nối giữa 3 dịch vụ trước khi deploy production
3. Document mọi webhook URL và API key trong .env
4. Backup workflow n8n định kỳ vào GitHub
5. Monitor uptime cả 3 dịch vụ
