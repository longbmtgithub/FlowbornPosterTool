# 🎨 Flowborn Poster Tool v1.0

**by hienmods**

Tool tự động tạo poster Flowborn cho Liên Quân Mobile (AOV).  
Hỗ trợ **Android (Termux)** và **iOS (Cloud Shell / iSH)**.

---

## ✨ Tính năng

- 🖼️ Hỗ trợ **JPG, PNG, WEBP, GIF, MP4**
- 🔐 Dynamic encodeparam (tự tạo mã xác thực mới mỗi request)
- 👥 Multi-account (chạy nhiều tài khoản cùng lúc)
- ⚡ Auto sign bridge (Node.js)
- 🎭 Hỗ trợ sticker, nameplate tùy chỉnh
- 📱 Chạy được trên cả **Android** và **iOS**

---

## 📝 Cách capture file HAR

1. Mở app capture trên điện thoại:
   - **Android**: PCAPdroid / HTTP Canary
   - **iOS**: Reqable / ProxyPin
2. Bắt đầu capture → Mở **Liên Quân Mobile**
3. Vào **Flowborn Poster** trong game
4. Thay đổi 1 sticker bất kỳ → **Lưu** poster
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
python flowborn_poster.py
```

---

## 🍎 Cài đặt & Sử dụng trên iOS

Có **2 cách** chạy tool trên iOS:

### Cách 1: Google Cloud Shell ⭐ (Khuyến nghị)

> ☁️ Chạy trên cloud miễn phí, không cần cài đặt gì, sign bridge hoạt động mượt!

**Bước 1:** Mở Safari trên iPhone, vào link:

👉 [Mở Cloud Shell](https://shell.cloud.google.com/cloudshell/open?git_repo=https://github.com/longbmtgithub/FlowbornPosterTool&open_in_editor=flowborn_poster.py&shellonly=true)

→ Đăng nhập tài khoản Google (miễn phí, không cần thẻ)

**Bước 2:** Upload file `.har`:
- Nhấn nút **⋮** (góc phải trên) → **Upload** → chọn file HAR
- Di chuyển file vào thư mục tool:
```bash
mv ~/ten_file.har ~/FlowbornPosterTool/
```

**Bước 3:** Chạy tool:
```bash
sh r
```

> 💡 Lệnh `sh r` sẽ **tự cài thư viện** và chạy tool. Chỉ cần gõ 4 ký tự!

---

### Cách 2: iSH (Offline trên iPhone)

> 📲 Chạy trực tiếp trên iPhone, không cần mạng cloud. Nhưng sign bridge có thể chậm.

**Bước 1:** Tải **iSH Shell** từ App Store

**Bước 2:** Tải bản iSH từ [Releases](https://github.com/longbmtgithub/FlowbornPosterTool/releases):
```bash
wget https://github.com/longbmtgithub/FlowbornPosterTool/releases/download/v1.3/FlowbornPosterTool_v1.3_iSH.zip
unzip FlowbornPosterTool_v1.3_iSH.zip
```

**Bước 3:** Chạy setup:
```bash
sh setup_ish.sh
```

**Bước 4:** Copy file `.har` và ảnh vào thư mục, rồi chạy:
```bash
python3 flowborn_poster.py
```

> ⚠️ Trên iSH, sign bridge có thể chậm (do emulation). Nếu gặp timeout, tool sẽ tự dùng encodeparam từ HAR.

---

### So sánh 2 cách trên iOS

| | Cloud Shell ☁️ | iSH 📲 |
|---|---|---|
| **Tốc độ** | ⭐⭐⭐⭐⭐ Nhanh | ⭐⭐ Chậm |
| **Sign bridge** | ✅ Hoạt động | ⚠️ Có thể timeout |
| **Cài đặt** | Không cần | Cần cài app |
| **Yêu cầu** | Tài khoản Google | Không |
| **Offline** | ❌ Cần mạng | ✅ Được |

---

## 🎮 Các lệnh

```bash
# Chạy tool (cách nhanh - Cloud Shell)
sh r

# Chạy tool (cách thường)
python3 flowborn_poster.py

# Test sign bridge
python3 flowborn_poster.py --test-sign

# Chỉ định file HAR
python3 flowborn_poster.py --har tenfile.har

# Chỉ định số vòng
python3 flowborn_poster.py --rounds 3

# Lấy mã thiết bị (Device ID)
python3 flowborn_poster.py --device-id
```

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
- Chạy `python3 flowborn_poster.py --device-id` để lấy mã thiết bị
- Gửi mã cho **hienmods** để kích hoạt

### Sign bridge timeout trên iSH
- Dùng **Google Cloud Shell** thay thế (xem hướng dẫn ở trên)
- Hoặc đợi 3-5 phút để Node.js load xong trên iSH

---

## 📁 Cấu trúc files

```
FlowbornPosterTool/
├── flowborn_poster.py              ← Tool chính
├── sign_bridge.js                  ← Sign bridge (Node.js)
├── sign_bridge_py.py               ← Sign bridge (Python - cho iSH)
├── camp-security-oversea.0.1.0.js  ← Security lib
├── r                               ← Quick run (sh r)
├── setup.sh                        ← Setup Android/Termux
├── setup_ish.sh                    ← Setup iOS/iSH
├── README.md                       ← File này
└── (các file .har và ảnh/video)
```

---

## ⚠️ Lưu ý

- Liên hệ **hienmods** để mua license.
- **Không** chia sẻ file HAR cho người khác (chứa thông tin đăng nhập).
- Mở game sau khi tool chạy xong để xem poster mới.

---

**© 2025 hienmods** — All rights reserved.
