# BookStore Microservices – Assignment 05

Hệ thống BookStore kiến trúc microservices (Django REST Framework), đáp ứng đầy đủ 12 service và 5 Functional Requirements theo tài liệu Assignment 05.

## Cấu trúc

- `customer-service` – Đăng ký/đăng nhập khách hàng, tự tạo cart (FR1)
- `staff-service` – Staff quản lý sách (FR2)
- `manager-service` – Dashboard quản lý
- `catalog-service` – Danh mục sách
- `book-service` – CRUD sách
- `cart-service` – Giỏ hàng: thêm/xem/cập nhật (FR3)
- `order-service` – Đơn hàng, gọi pay + ship (FR4)
- `ship-service` – Vận chuyển
- `pay-service` – Thanh toán
- `comment-rate-service` – Đánh giá sách (FR5)
- `recommender-ai-service` – Gợi ý sách
- `api-gateway` – Điểm vào duy nhất, routing

## Chạy hệ thống và hiển thị giao diện

### Cách 1: Docker Compose (khuyến nghị)

```bash
cd bookstore-microservice
docker compose up --build
```

Đợi tất cả container chạy xong (có thể mất vài phút lần đầu). Sau đó:

- **Mở giao diện web:** truy cập **http://localhost:8000** trên trình duyệt.
- **API:** cùng địa chỉ, prefix `/api/` (ví dụ http://localhost:8000/api/books/).
- Các service backend: port 8001–8012 (xem `docker-compose.yml`).

### Cách 2: Chạy từng service bằng tay (không dùng Docker)

1. Cài Python 3.10+, tạo venv và cài dependency trong từng thư mục service (Django, djangorestframework, requests).
2. Trong mỗi service: `python manage.py migrate && python manage.py runserver 0.0.0.0:8xxx` (port theo từng service).
3. Chạy **api-gateway** cuối: `cd api-gateway && python manage.py runserver 0.0.0.0:8000`.
4. Mở trình duyệt: **http://localhost:8000**.

**Lưu ý:** Khi chạy tay, cần chỉnh biến môi trường (CUSTOMER_SERVICE_URL, BOOK_SERVICE_URL, …) trỏ tới đúng host:port của từng service (ví dụ `http://127.0.0.1:8001`).

### Giao diện web (trên http://localhost:8000)

| Trang | Mô tả |
|-------|--------|
| **Trang chủ** | Đăng ký khách hàng (FR1), xem danh mục sách, gợi ý đọc |
| **Giỏ hàng** | Xem/cập nhật/xóa mục trong giỏ (FR3); nhập Customer ID nếu chưa đăng ký trên máy này |
| **Thanh toán** | Đặt hàng – Order → Pay → Ship (FR4) |
| **Quản lý sách** | Staff thêm/sửa/xóa sách (FR2) |
| **Dashboard** | Thống kê số khách hàng, sách, đơn hàng |
| **Chi tiết sách** | Thêm vào giỏ, xem và gửi đánh giá (FR5) |

Giao diện dùng HTML/CSS/JS, gọi REST API qua Gateway; không cần cài thêm frontend framework.

## Tài liệu

- `docs/ARCHITECTURE.md` – Sơ đồ kiến trúc, Database per Service
- `docs/API.md` – API documentation
- `docs/CODE_GUIDE.md` – Giải thích code từng service
