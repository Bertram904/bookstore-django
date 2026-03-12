# Giao diện Web – BookStore

Giao diện web chạy trên **API Gateway** (port 8000), thiết kế gọn, chuyên nghiệp, dùng HTML/CSS/JS thuần, gọi REST API qua cùng domain.

## Cách chạy và mở giao diện

1. **Khởi động toàn bộ hệ thống:**
   ```bash
   cd bookstore-microservice
   docker compose up --build
   ```
2. **Mở trình duyệt:** truy cập **http://localhost:8000**

Không cần chạy thêm server frontend hay build; Gateway vừa serve HTML vừa proxy API.

## Các trang chính

| URL | Chức năng |
|-----|-----------|
| `/` | Trang chủ: đăng ký khách hàng (FR1), danh mục sách, gợi ý đọc |
| `/cart/` | Giỏ hàng: nhập Customer ID hoặc dùng ID đã lưu (localStorage), xem/sửa/xóa mục (FR3) |
| `/checkout/` | Đặt hàng: nhập Customer ID + địa chỉ → tạo đơn (FR4: Saga Pay + Ship) |
| `/staff/` | Quản lý sách: thêm/sửa/xóa sách (FR2), gọi API staff → book-service |
| `/manager/` | Dashboard: thống kê số khách hàng, sách, đơn hàng |
| `/book/<id>/` | Chi tiết sách: thêm vào giỏ, xem đánh giá, gửi đánh giá (FR5) |

## Luồng sử dụng gợi ý

1. Vào **Trang chủ** → Đăng ký (Họ tên + Email). Sau khi đăng ký, ID khách hàng được lưu trên trình duyệt.
2. Xem **Danh mục sách** → Bấm vào một sách → Trang chi tiết → Thêm vào giỏ (dùng Customer ID đã lưu).
3. Vào **Giỏ hàng** → Chỉnh số lượng hoặc xóa mục → **Thanh toán** → Nhập địa chỉ → Đặt hàng.
4. Vào **Chi tiết sách** → Gửi đánh giá (điểm 1–5, nhận xét) → FR5.
5. Vào **Quản lý sách** (Staff) → Thêm sách mới, sửa/xóa sách.
6. Vào **Dashboard** → Xem tổng số khách hàng, sách, đơn hàng.

## Công nghệ giao diện

- **HTML5** – Cấu trúc trang, form.
- **CSS3** – Biến (colors, fonts), grid/flexbox, bóng đổ, responsive.
- **JavaScript** – Gọi `fetch()` tới `/api/...`, cập nhật DOM, lưu Customer ID vào `localStorage`.
- **Font:** Outfit (tiêu đề), Source Serif 4 (logo) – Google Fonts.
- **Giao diện:** Tông xanh navy/teal (#1a4d5c), nền kem (#f8f6f3), accent cam (#c17f59), thẻ trắng, bo góc, shadow nhẹ.

File giao diện nằm trong `api-gateway/gateway/`:
- `templates/`: base.html, index.html, cart.html, checkout.html, staff.html, manager.html, book.html
- `static/css/style.css`: toàn bộ style
- `static/js/app.js`: logic gọi API và thao tác trang
