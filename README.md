# 🎨 Flowborn Poster Tool v1.0

**by hienmods**

Tool tự động tạo poster Flowborn cho Liên Quân Mobile (AOV) trên Termux.

---

## ✨ Tính năng

- 🖼️ Hỗ trợ **JPG, PNG, WEBP, GIF, MP4**
- 🔐 Dynamic encodeparam (tự tạo mã xác thực mới mỗi request)
- 👥 Multi-account (chạy nhiều tài khoản cùng lúc)
- ⚡ Auto sign bridge (Node.js)
- 🎭 Hỗ trợ sticker, nameplate tùy chỉnh

---

## 📱 Yêu cầu

- **Android** với **Termux** đã cài đặt
- File **.har** capture từ game (xem hướng dẫn bên dưới)
- Ảnh/video muốn làm poster

---

## 🚀 Cài đặt

### Bước 1: Mở Termux

### Bước 2: Copy toàn bộ thư mục tool vào Termux
```bash
cp -r /sdcard/Download/FlowbornPosterTool ~/ckk
cd ~/ckk
```

### Bước 3: Chạy setup
```bash
bash setup.sh
```

Setup sẽ tự động cài:
- Python
- Node.js
- requests + Pillow

---

## 📝 Cách capture file HAR

1. Mở app **PCAPdroid** hoặc **HTTP Canary** trên Android
2. Bắt đầu capture → Mở **Liên Quân Mobile**
3. Vào **Flowborn Poster** trong game
4. Thay đổi 1 sticker bất kỳ → **Lưu** poster
5. Dừng capture → **Export file .har**
6. Copy file .har vào thư mục tool

> ⚠️ File HAR chứa token đăng nhập. **Không chia sẻ** file HAR cho người khác!

---

## 🎮 Cách sử dụng

### 1. Copy files cần thiết vào thư mục tool:
- File `.har` (từ game)
- Ảnh/video muốn đăng

### 2. Chạy tool:
```bash
python flowborn_poster.py
```

### 3. Làm theo hướng dẫn trên màn hình:
- Chọn tài khoản (nếu có nhiều file HAR)
- Chọn ảnh/video
- Chọn số vòng lặp
- Đợi tool hoàn thành

### Các lệnh khác:
```bash
# Test sign bridge
python flowborn_poster.py --test-sign

# Chỉ định file HAR
python flowborn_poster.py --har tenfile.har

# Chỉ định số vòng
python flowborn_poster.py --rounds 3
```

---

## ❓ FAQ & Khắc phục lỗi

### "Sign bridge KHONG HOAT DONG"
```bash
# Kiểm tra Node.js
node --version

# Nếu chưa có, cài lại:
pkg install nodejs
```

### "-5001:auth failed"
- Token trong file HAR đã hết hạn
- Capture file HAR mới từ game

### "HTTP 403"
- Token hết hạn hoặc sai
- Capture lại file HAR

### "Thieu: pip install requests"
```bash
pip install requests Pillow
```

---

## 📁 Cấu trúc files

```
FlowbornPosterTool/
├── flowborn_poster.py              ← Tool chính
├── sign_bridge.js                  ← Sign bridge (Node.js)
├── camp-security-oversea.0.1.0.js  ← Security lib
├── setup.sh                        ← Script cài đặt
├── README.md                       ← File này
└── (các file .har và ảnh/video)
```

---

## ⚠️ Lưu ý

- Tool chỉ sử dụng được **1 lần**.
- **Không** chia sẻ file HAR cho người khác (chứa thông tin đăng nhập).
- Mở game sau khi tool chạy xong để xem poster mới.

---

**© 2026 hienmods** — All rights reserved.
