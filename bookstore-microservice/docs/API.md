# API Documentation – BookStore Microservices

Tất cả API được gọi qua **API Gateway** tại `http://localhost:8000`. Gateway định tuyến theo path tới đúng service.

---

## 1. Customer Service (Identity)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| GET | /api/customers/ | Danh sách khách hàng | - |
| POST | /api/customers/ | Đăng ký khách hàng (FR1: tự tạo cart) | `{"name": "Nguyen Van A", "email": "a@example.com"}` |
| GET | /api/customers/<id>/ | Chi tiết một khách hàng | - |

---

## 2. Staff Service (FR2 – Quản lý sách)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| GET | /api/staff/books/ | Danh sách sách | - |
| POST | /api/staff/books/ | Thêm sách | `{"title": "...", "author": "...", "price": "99.00", "stock": 10}` |
| GET | /api/staff/books/<id>/ | Chi tiết sách | - |
| PUT | /api/staff/books/<id>/ | Cập nhật sách | same as POST |
| DELETE | /api/staff/books/<id>/ | Xóa sách | - |

---

## 3. Book Service (Catalog)

| Method | Path | Mô tả | Body / Query |
|--------|------|--------|--------------|
| GET | /api/books/ | Danh sách sách | - |
| GET | /api/books/batch/?ids=1&ids=2 | Lấy nhiều sách theo ID (dùng nội bộ/cart) | - |
| GET | /api/books/<id>/ | Chi tiết sách | - |
| POST | /api/books/ | Tạo sách | `{"title", "author", "price", "stock"}` |
| PUT | /api/books/<id>/ | Cập nhật sách | - |
| DELETE | /api/books/<id>/ | Xóa sách | - |

---

## 4. Cart Service (FR3)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| POST | /api/cart/create/ | Tạo giỏ (gọi từ customer-service khi đăng ký) | `{"customer_id": 1}` |
| POST | /api/cart/add/<customer_id>/ | Thêm sách vào giỏ hoặc cộng số lượng | `{"book_id": 1, "quantity": 2}` |
| GET | /api/cart/view/<customer_id>/ | Xem giỏ kèm thông tin sách | - |
| PATCH | /api/cart/update/<customer_id>/<item_id>/ | Cập nhật số lượng mục | `{"quantity": 3}` |
| DELETE | /api/cart/remove/<customer_id>/<item_id>/ | Xóa mục khỏi giỏ | - |
| GET | /api/cart/by-customer/<customer_id>/ | Lấy giỏ + items (cho order-service) | - |

---

## 5. Order Service (FR4 – Saga)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| POST | /api/orders/create/ | Tạo đơn: lấy cart → reserve pay → reserve ship → completed hoặc compensate | `{"customer_id": 1, "address": "123 ABC"}` |
| GET | /api/orders/?customer_id=1 | Danh sách đơn (có thể lọc theo customer_id) | - |

---

## 6. Pay Service (FR4)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| POST | /api/pay/reserve/ | Reserve thanh toán (Saga) | `{"order_id": "uuid", "amount": "99.00"}` |
| POST | /api/pay/<id>/release/ | Hủy reserve (compensation) | - |

---

## 7. Ship Service (FR4)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| POST | /api/ship/reserve/ | Reserve vận chuyển (Saga) | `{"order_id": "uuid", "address": "..."}` |
| POST | /api/ship/<id>/release/ | Hủy reserve (compensation) | - |

---

## 8. Comment-Rate Service (FR5)

| Method | Path | Mô tả | Body |
|--------|------|--------|------|
| POST | /api/reviews/rate/ | Đánh giá sách (1–5), tạo hoặc cập nhật | `{"book_id": 1, "customer_id": 1, "rating": 5, "comment": "Hay"}` |
| GET | /api/reviews/book/<book_id>/ | Danh sách đánh giá + điểm trung bình | - |

---

## 9. Catalog Service

| Method | Path | Mô tả |
|--------|------|--------|
| GET | /api/catalog/books/ | Danh sách sách (proxy book-service) |

---

## 10. Manager Service

| Method | Path | Mô tả |
|--------|------|--------|
| GET | /api/manager/dashboard/ | Dashboard: customers_count, books_count, orders_count |

---

## 11. Recommender Service

| Method | Path | Mô tả |
|--------|------|--------|
| GET | /api/recommend/?limit=5 | Gợi ý sách (trả về N sách đầu từ book-service) |
---

## OpenAPI / Swagger cho từng service

Mỗi service hiện có OpenAPI schema và Swagger UI:

- `GET /api/schema/` -> OpenAPI JSON
- `GET /api/schema/swagger-ui/` -> Swagger UI
- `GET /api/schema/redoc/` -> Redoc UI

Ví dụ với book-service (cổng mặc định 8005):
- http://localhost:8005/api/schema/
- http://localhost:8005/api/schema/swagger-ui/
- http://localhost:8005/api/schema/redoc/

Tương tự cho customer-service, cart-service, order-service, pay-service, ship-service, comment-rate-service, manager-service, catalog-service, recommender-ai-service.
---

## Ví dụ gọi qua Gateway (curl)

```bash
# Đăng ký khách hàng (tự tạo cart)
curl -X POST http://localhost:8000/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Nguyen Van A","email":"a@test.com"}'

# Thêm sách vào giỏ (customer_id=1)
curl -X POST http://localhost:8000/api/cart/add/1/ \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"quantity":2}'

# Xem giỏ
curl http://localhost:8000/api/cart/view/1/

# Tạo đơn
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"address":"123 Hanoi"}'

# Đánh giá sách
curl -X POST http://localhost:8000/api/reviews/rate/ \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"customer_id":1,"rating":5,"comment":"Tot"}'
```
