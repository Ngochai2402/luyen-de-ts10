# Hệ thống Quản lý Trung tâm Hưng Phương

> File này cho Claude Code biết bối cảnh đầy đủ về dự án. Đọc kỹ trước khi bắt đầu bất kỳ task nào.

## 🎯 Mục tiêu dự án

Xây dựng hệ thống quản lý trung tâm dạy thêm Hưng Phương (~150 học sinh) để **thay thế EasyEdu V2** (đang trả 8 triệu/năm). Lý do thay thế:
- EasyEdu **không có API** → không tự động hóa được, dữ liệu bị nhốt
- Chỉ **1/3 phụ huynh** cài app EasyEdu → thông báo điểm danh không đến được
- Vendor lock-in, không mở rộng tính năng được

## 🏗 Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────┐
│  GIAO DIỆN NGƯỜI DÙNG                                   │
│  - App Giáo viên (PWA)                                  │
│  - App Thủ quỹ (PWA)                                    │
│  - App Quản lý (PWA)                                    │
│  - App Phụ huynh (PWA)                                  │
└──────────────┬──────────────────────────────────────────┘
               │ HTTPS REST API
               ▼
┌─────────────────────────────────────────────────────────┐
│  WordPress REST API (Hostinger)                         │
│  Base: https://toanhinh.com/wp-json/hp-api/v1/          │
│  Auth: X-API-Key header                                 │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐   ┌─────────────┐
│   MySQL     │   │     n8n     │
│ (Hostinger) │   │  Webhooks   │
│             │   │   ↓         │
│ hp_attendance   │  ZNS (Zalo) │
│ hp_tuition  │   │  (100% PH)  │
│ ...         │   └─────────────┘
└─────────────┘
```

**Nguyên tắc cốt lõi:**
- **MySQL Hostinger** = nguồn sự thật duy nhất, không lưu dữ liệu ở chỗ khác
- **API-first**: xây API trước, app sau — tránh vendor lock-in tự gây ra
- **ZNS thay vì Zalo OA**: vượt qua giới hạn 48h, 100% PH nhận được
- **PWA thay vì App Store**: triển khai nhanh, phụ huynh không cần cài

## 🔧 Hạ tầng đã có sẵn

| Thành phần | Vai trò | Trạng thái |
|---|---|---|
| WordPress + Tutor LMS | CMS, học online, user management | ✅ đang chạy trên Hostinger |
| MySQL Hostinger | Database chính | ✅ có sẵn, n8n đã connect |
| Plugin `tutor-lms-staff-api.php` | API key + endpoints staff cũ | ✅ sẽ MỞ RỘNG (không viết lại) |
| n8n | Tự động hóa workflow | ✅ đang chạy |
| Railway | XeLaTeX, Puppeteer (compute riêng) | ✅ chỉ dùng cho compile, không lưu data |
| Zalo OA | Đã có | ✅ |
| ZNS | Cần đăng ký + duyệt template | 🔄 sẽ làm song song |
| API key | `ThayHai_BaoMat_2026!@#` | ✅ dùng lại key cũ |

## 👥 Vai trò người dùng

| Vai trò | Người | Quyền |
|---|---|---|
| **Chủ trung tâm** | Thầy Hải | Toàn quyền: dashboard, tài chính, nhân sự |
| **Quản lý** | Cô Mai | Lớp học, lịch dạy, ghi danh HS, điểm danh |
| **Thủ quỹ** | Chị Lan | Thu chi, học phí, báo cáo tài chính |
| **Giáo viên** | Thầy Nam, Cô Hoa, Thầy Long, Cô Vân | Điểm danh + giao BTVN cho lớp được phân |
| **Phụ huynh** | (~150 phụ huynh) | Xem điểm danh, kết quả test, học phí của con |

## 💰 Mô hình lương GV

- **Lương cứng:** 8 buổi/tháng × đơn giá GV
- **Thưởng**: tỷ lệ HS đi học, dạy phụ trội, đúng giờ...
- Mỗi buổi dạy thực tế = +1 record vào bảng `hp_teacher_sessions`
- Lương tháng = tổng buổi × đơn giá + thưởng - phạt (nếu có)

## 🗄 Database Schema

Xem chi tiết SQL trong `database/migrations/`. Các bảng chính:

- `hp_attendance` — Điểm danh từng HS từng buổi
- `hp_tuition` — Học phí tháng của HS
- `hp_tuition_payments` — Lịch sử thanh toán
- `hp_classes` — Thông tin lớp
- `hp_class_sessions` — Buổi học (đã/sắp diễn ra)
- `hp_class_teachers` — Quan hệ nhiều-nhiều: 1 lớp có thể có nhiều GV
- `hp_homework` — Bài tập về nhà
- `hp_teacher_sessions` — Buổi dạy thực tế của GV (để tính lương)
- `hp_salary_bonus` — Thưởng/phạt GV
- `hp_expenses` — Chi phí vận hành (điện, nước, mặt bằng, in ấn)
- `hp_extra_fees` — Phụ thu (tài liệu, dụng cụ...)

## 🛣 Lộ trình triển khai (5 giai đoạn, 8-10 tuần)

### **GIAI ĐOẠN 1: Database Foundation** (1 ngày)
- [ ] Chạy migration tạo 11 bảng MySQL
- [ ] Insert data mẫu để test
- [ ] Verify schema với `SHOW TABLES`

### **GIAI ĐOẠN 2: WordPress Plugin API** (3-5 ngày)
- [ ] Mở rộng plugin `tutor-lms-staff-api.php`
- [ ] Endpoints điểm danh: POST/GET `/attendance`
- [ ] Endpoints học phí: GET `/tuition`, POST `/tuition/payment`
- [ ] Endpoints lớp: GET `/classes`, GET `/classes/{code}/students`
- [ ] Endpoints lương GV: GET `/teacher/{id}/salary`
- [ ] Test với Postman/curl

### **GIAI ĐOẠN 3: App Giáo Viên (PWA)** (1 tuần)
- [ ] 4 tab: Trang chủ · Lịch dạy · Nhiệm vụ · Lương
- [ ] Điểm danh 1-click (Có/Vắng/Muộn)
- [ ] Giao BTVN
- [ ] Hiển thị lương real-time
- [ ] Task tự động đánh dấu xong khi điểm danh

### **GIAI ĐOẠN 4: App Thủ Quỹ + Quản Lý** (2 tuần)
- [ ] App Thủ quỹ: thu học phí, sổ thu chi, báo cáo
- [ ] App Quản lý: lớp học, lịch dạy, ghi danh HS
- [ ] n8n workflow: trigger ZNS khi có HS vắng
- [ ] n8n workflow: trigger ZNS nhắc học phí

### **GIAI ĐOẠN 5: PWA Phụ Huynh + Bỏ EasyEdu** (2-3 tuần)
- [ ] Cài Super PWA plugin
- [ ] Trang phụ huynh xem thông tin con
- [ ] Push notification
- [ ] Migration dữ liệu từ EasyEdu
- [ ] Hủy gói EasyEdu

## ⚠️ Quy tắc quan trọng

1. **KHÔNG kết nối thẳng app → MySQL.** Luôn qua REST API.
2. **KHÔNG lưu data ở Google Sheets/Railway.** MySQL là duy nhất.
3. **KHÔNG tạo bảng mới khi đã có bảng tương đương.** Mở rộng `wp_users`, `wp_usermeta` trước.
4. **API key bắt buộc** cho mọi endpoint — header `X-API-Key`.
5. **Test trên staging** trước khi deploy production (toanhinh.com).
6. **Backup MySQL** trước mỗi migration.
7. **Plugin PHP** ở folder `wp-plugin/` — upload lên `wp-content/plugins/` của Hostinger.

## 🚀 Cách bắt đầu task mới với Claude Code

Khi gửi task cho Claude Code, hãy reference:
- File này (`CLAUDE.md`) cho bối cảnh chung
- File trong `docs/` cho chi tiết từng phần
- File migration trong `database/migrations/` đã đặt sẵn

Ví dụ prompt:
```
Đọc CLAUDE.md, sau đó:
1. Review database/migrations/001_initial_schema.sql
2. Tạo plugin wp-plugin/hp-api.php với endpoint POST /attendance
3. Test bằng curl với data mẫu
```

## 📂 Cấu trúc thư mục

```
hung-phuong-system/
├── CLAUDE.md                    ← File này (đọc đầu tiên)
├── README.md                    ← Hướng dẫn nhanh
├── database/
│   ├── migrations/              ← SQL tạo bảng theo thứ tự
│   └── seed-data.sql            ← Data mẫu để test
├── wp-plugin/
│   ├── hp-api.php               ← Plugin chính (mở rộng staff-api)
│   └── includes/                ← Các file con theo module
├── apps/
│   ├── teacher/                 ← App Giáo viên (PWA)
│   ├── cashier/                 ← App Thủ quỹ
│   ├── manager/                 ← App Quản lý
│   └── parent-pwa/              ← PWA Phụ huynh
├── n8n-workflows/               ← JSON workflow để import vào n8n
└── docs/
    ├── api-reference.md         ← Tài liệu API
    ├── deployment.md            ← Cách deploy lên Hostinger
    └── decisions.md             ← Lý do chọn từng giải pháp
```

## 🔐 Thông tin nhạy cảm

KHÔNG commit vào git:
- API key thực
- MySQL password
- Hostinger credentials
- ZNS API token

Dùng file `.env` (đã có trong `.gitignore`) cho các giá trị này.

---

**Liên hệ:** Thầy Hải (Chủ trung tâm)
**Bắt đầu:** April 2026

---

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
