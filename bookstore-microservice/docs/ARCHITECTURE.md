# Kiến trúc hệ thống BookStore Microservices – Assignment 05

## 1. Tổng quan

Hệ thống BookStore được phân tách thành **12 microservice** độc lập và **1 API Gateway**, đáp ứng đầy đủ yêu cầu Assignment 05 (Academic Microservice Implementation). Mỗi service có **database riêng** (Database per Service), giao tiếp qua **REST**.

## 2. Sơ đồ kiến trúc

```
                    +------------------+
                    |     Client       |
                    +--------+---------+
                             |
                             | HTTP (port 8000)
                             v
                    +------------------+
                    |   API Gateway    |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+----------------+  +----------------+  +----------------+
| customer-svc   |  | book-service   |  | cart-service   |
| (8001)         |  | (8005)         |  | (8006)         |
+----------------+  +----------------+  +----------------+
         |                   |                   |
         |    FR1: Đăng ký   |    FR3: Add/View  |
         +------------------>|    Cart            |
         |    tạo cart       |<-------------------+
         |                   |
         v                   v
+----------------+  +----------------+  +----------------+
| staff-service  |  | order-service  |  | pay-service    |
| (8002)         |  | (8007)         |  | (8009)         |
+----------------+  +----------------+  +----------------+
         |                   |                   |
         | FR2: Quản lý sách |    FR4: Saga       |
         +------------------>|    Pay + Ship      |
                             v
                    +----------------+  +----------------+
                    | ship-service   |  | comment-rate   |
                    | (8008)         |  | (8010) FR5     |
                    +----------------+  +----------------+
```

## 3. Nguyên tắc Database per Service

| Service | Database | Giải thích |
|---------|----------|------------|
| customer-service | SQLite (db.sqlite3) | Bảng Customer – không chia sẻ với service khác |
| book-service | SQLite | Bảng Book |
| cart-service | SQLite | Bảng Cart, CartItem – chỉ lưu `customer_id`, `book_id` (Integer), không FK sang DB khác |
| order-service | SQLite | Bảng Order |
| pay-service | SQLite | Bảng PaymentReservation |
| ship-service | SQLite | Bảng ShipmentReservation |
| comment-rate-service | SQLite | Bảng Review (book_id, customer_id là ID tham chiếu) |
| staff, manager, catalog, recommender, api-gateway | SQLite (tối thiểu) hoặc không dùng DB | Proxy/aggregation, có thể không có bảng nghiệp vụ |

**Điểm quan trọng:** Cart-service **không** dùng `ForeignKey(Book)` hay `ForeignKey(Customer)` vì Book và Customer nằm ở database khác. Chỉ lưu `book_id`, `customer_id` (Integer). Khi cần tên sách, giá, cart-service gọi REST API của book-service (batch).

## 4. Luồng chức năng (Functional Requirements)

### FR1: Customer registration automatically creates a cart
- Client gọi **POST /api/customers/** (qua Gateway) với `{"name":"...", "email":"..."}`.
- customer-service lưu Customer, sau đó gọi **POST http://cart-service:8000/api/cart/create/** với `{"customer_id": customer.id}`.
- cart-service kiểm tra customer tồn tại (GET customer-service), tạo Cart.

### FR2: Staff manages books
- Staff gọi qua Gateway: **GET/POST /api/staff/books/**, **PUT/DELETE /api/staff/books/<id>/**.
- staff-service proxy sang book-service (REST).

### FR3: Add, view, update cart
- **POST /api/cart/add/<customer_id>/** với `{"book_id": 1, "quantity": 2}` – cart-service kiểm tra book tồn tại (gọi book-service), thêm/cập nhật CartItem.
- **GET /api/cart/view/<customer_id>/** – trả về giỏ kèm thông tin sách (gọi book-service batch).
- **PATCH /api/cart/update/<customer_id>/<item_id>/** – cập nhật số lượng.
- **DELETE /api/cart/remove/<customer_id>/<item_id>/** – xóa mục.

### FR4: Order triggers payment and shipping
- **POST /api/orders/create/** với `{"customer_id": 1, "address": "..."}`.
- order-service: lấy giỏ (cart-service), tính tổng (book-service), tạo Order pending → **reserve pay** → **reserve ship**. Nếu thành công: status=completed. Nếu thất bại: **compensate** (release pay, release ship), status=failed.

### FR5: Customer can rate books
- **POST /api/reviews/rate/** với `{"book_id": 1, "customer_id": 1, "rating": 5, "comment": "..."}`.
- comment-rate-service kiểm tra book tồn tại (book-service), `update_or_create` Review.
- **GET /api/reviews/book/<book_id>/** – danh sách đánh giá + điểm trung bình.

## 5. Cấu trúc thư mục (gợi ý)

```
bookstore-microservice/
├── docker-compose.yml
├── README.md
├── docs/
│   ├── ARCHITECTURE.md   (file này)
│   ├── API.md
│   └── CODE_GUIDE.md
├── api-gateway/
├── customer-service/
├── staff-service/
├── manager-service/
├── catalog-service/
├── book-service/
├── cart-service/
├── order-service/
├── ship-service/
├── pay-service/
├── comment-rate-service/
└── recommender-ai-service/
```

Mỗi service là một **Django project** độc lập (manage.py, settings, urls, app với models/views/serializers).
