# 🎨 KGVN Poster Tools v3.0

**by hienmods**

Bộ công cụ tùy chỉnh poster cho **Liên Quân Mobile (AOV)**.  
Hỗ trợ **Android (Termux)** và **iOS (Cloud Shell / iSH)**.

---

## 📦 2 Tool trong bộ

| Tool | Mô tả | File |
|------|--------|------|
| 🌸 **Flowborn Poster** | Mod poster Flowborn (có badge, sticker, nameplate) | `flowborn_poster.py` |
| 🖼️ **Load Tran** | Mod ảnh load trận (playerimage) | `loadtran.py` |

---

## ✨ Tính năng chung

- 🖼️ Hỗ trợ **JPG, PNG, WEBP, GIF, MP4**
- 🔐 Dynamic encodeparam (Sign Bridge — tự tạo mã mới mỗi request)
- 👥 Multi-account (chạy nhiều tài khoản song song)
- ⚡ Auto Sign Bridge (Node.js / Python)
- 🚀 Boost mode (tăng lượt dùng nền)
- 📱 Chạy trên **Android** và **iOS**

### 🌸 Flowborn Poster (riêng)
- 🎭 10 vị trí sticker tùy chỉnh
- 🎖️ 25 badge rank thật (SSS+ → A VIP)
- ✍️ Tên skin overlay
- 📝 Nameplate tùy chỉnh
- 🚫 Tùy chọn bỏ sticker

### 🖼️ Load Tran (riêng)
- 📐 Auto resize ảnh chuẩn poster (1080×1701)
- 🔄 COS credentials riêng cho mỗi file upload
- 📊 savepostereditinfo trước saveposter

---

## 📝 Cách capture file HAR

1. Mở app capture trên điện thoại:
   - **Android**: PCAPdroid / HTTP Canary
   - **iOS**: Reqable / ProxyPin
2. Bắt đầu capture → Mở **Liên Quân Mobile**
3. Vào **Flowborn Poster** hoặc **thay poster load trận** trong game
4. Thay đổi 1 ảnh bất kỳ → **Lưu**
5. Dừng capture → **Export file .har**

> ⚠️ File HAR chứa token đăng nhập. **Không chia sẻ** file HAR cho người khác!

---

## 📱 Cài đặt & Sử dụng trên Android (Termux)

### Bước 1: Mở Termux

### Bước 2: Copy thư mục tool vào Termux
```bash
cp -r /sdcard/Download/FlowbornPosterTool ~/ckk
cd ~/ckk
```

### Bước 3: Chạy setup
```bash
bash setup.sh
```

### Bước 4: Chạy tool
```bash
# Flowborn Poster
flb
# hoặc
python flowborn_poster.py

# Load Tran
python loadtran.py
```

---

## 🍎 Cài đặt & Sử dụng trên iOS

Có **2 cách** chạy tool trên iOS:

### Cách 1: Google Cloud Shell ⭐ (Khuyến nghị)

> ☁️ Chạy trên cloud miễn phí, không cần cài đặt gì, sign bridge hoạt động mượt!

**Bước 1:** Mở Safari trên iPhone, vào link:

👉 [Mở Cloud Shell](https://shell.cloud.google.com/cloudshell/open?git_repo=https://github.com/longbmtgithub/FlowbornPosterTool&open_in_editor=flowborn_poster.py&shellonly=true)

→ Đăng nhập tài khoản Google (miễn phí, không cần thẻ)

**Bước 2:** Upload file `.har` và ảnh/video

**Bước 3:** Chạy tool:
```bash
# Flowborn Poster
sh r

# Load Tran
sh r loadtran
```
*(Trên Cloud Shell, tool sử dụng Web Login bằng username/password đăng ký trên web)*

---

### Cách 2: iSH (Offline trên iPhone)

> 📲 Chạy trực tiếp trên iPhone, không cần mạng cloud.

**Bước 1:** Tải **iSH Shell** từ App Store

**Bước 2:** Chạy setup:
```bash
sh setup_ish.sh
```

**Bước 3:** Copy file `.har` và ảnh vào thư mục, rồi chạy:
```bash
python3 flowborn_poster.py
# hoặc
python3 loadtran.py
```

---

## 🎮 Các lệnh

### Flowborn Poster
```bash
python flowborn_poster.py                # Chạy bình thường
python flowborn_poster.py --test-sign    # Test sign bridge
python flowborn_poster.py --har ten.har  # Chỉ định HAR
python flowborn_poster.py --rounds 3     # 3 vòng lặp
python flowborn_poster.py --device-id    # Lấy mã thiết bị
```

### Load Tran
```bash
python loadtran.py                       # Chạy bình thường
python loadtran.py --test-sign           # Test sign bridge
python loadtran.py --har ten.har         # Chỉ định HAR
python loadtran.py --rounds 3            # 3 vòng lặp
python loadtran.py --dry-run             # Chỉ kiểm tra
```

---

## 🎖️ Danh sách Badge Rank (Flowborn)

| # | Badge | # | Badge |
|---|-------|---|-------|
| 1 | SSS+ Tối Thượng | 14 | S+ Hữu Hạn |
| 2 | SSS+ Hữu Hạn | 15 | S+ Giáp Thìn |
| 3 | SSS Premium | 16 | S Premium |
| 4 | SSS Hữu Hạn | 17 | S Hữu Hạn |
| 5 | SSS Giáp Thìn | 18 | S+ Bậc |
| 6 | SS Tuyệt Sắc | 19 | SS Bậc |
| 7 | SS Hữu Hạn | 20 | S Bậc |
| 8 | SS Premium | 21 | A Bậc |
| 9 | SS+ Premium | 22 | A VIP |
| 10 | SS+ Hữu Hạn | 23 | S+ Bính Ngọ |
| 11 | SS Giáp Thìn | 24 | SS Bính Ngọ |
| 12 | SS VIP | 25 | SS+ Bính Ngọ |
| 13 | S+ Premium | | |

---

## ❓ FAQ & Khắc phục lỗi

### "Sign bridge KHONG HOAT DONG"
```bash
# Kiểm tra Node.js
node --version

# Nếu chưa có:
# Android: pkg install nodejs
# iSH: apk add nodejs
```

### "-5001:auth failed"
- Token trong file HAR đã hết hạn
- **Capture file HAR mới** từ game và chạy lại

### "HTTP 403"
- Token hết hạn hoặc sai
- Capture lại file HAR

### "License: Device chua duoc cap phep"
- Chạy `python flowborn_poster.py --device-id` để lấy mã thiết bị
- Gửi mã cho **hienmods** để kích hoạt

### Sign bridge timeout trên iSH
- Dùng **Google Cloud Shell** thay thế
- Hoặc đợi 3-5 phút để Node.js load xong trên iSH

---

## 📁 Cấu trúc files

```
FlowbornPosterTool/
├── flowborn_poster.py              ← Flowborn Poster (obfuscated)
├── loadtran.py                     ← Load Tran (obfuscated)
├── sign_bridge.js                  ← Sign bridge (Node.js)
├── sign_bridge_py.py               ← Sign bridge (Python - cho iSH)
├── camp-security-oversea.0.1.0.js  ← Security lib
├── badges/                         ← 25 badge rank PNG
│   ├── sss+tt.png
│   ├── sss+hh.png
│   └── ... (25 files)
├── setup.sh                        ← Setup Android/Termux
├── setup_ish.sh                    ← Setup iOS/iSH
└── README.md                       ← File này
```

---

## ⚠️ Lưu ý

- Liên hệ **hienmods** để mua license.
- **Không** chia sẻ file HAR cho người khác (chứa thông tin đăng nhập).
- Mở game sau khi tool chạy xong để xem poster mới.

---

**© 2025 hienmods** — All rights reserved.
