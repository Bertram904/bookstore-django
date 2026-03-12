# BÁO CÁO KỸ THUẬT – ASSIGNMENT 05  
## BookStore Microservices (Django REST Framework)

**Môn:** Kiến trúc và Thiết kế Phần mềm / Software Architecture and Design  
**Nội dung:** Triển khai hệ thống BookStore theo kiến trúc vi dịch vụ (microservices), đáp ứng 12 service và 5 Functional Requirements.

---

## 1. Mục tiêu và phạm vi (4.1, 4.2)

### 1.1 Mục tiêu
Mục đích của Assignment 05 là tái cấu trúc hệ thống BookStore từ kiến trúc nguyên khối (monolithic) sang kiến trúc vi dịch vụ (microservices) bằng **Django REST Framework**. Mỗi dịch vụ chịu trách nhiệm một chức năng nghiệp vụ riêng, có cơ sở dữ liệu riêng và giao tiếp qua REST.

### 1.2 Các service đã triển khai (12 service)
| STT | Service | Port (Docker) | Chức năng chính |
|-----|---------|----------------|------------------|
| 1 | staff-service | 8002 | FR2: Staff quản lý sách (proxy book-service) |
| 2 | manager-service | 8003 | Dashboard: thống kê customers, books, orders |
| 3 | customer-service | 8001 | Khách hàng; FR1: đăng ký tự tạo cart |
| 4 | catalog-service | 8004 | Danh mục sách (proxy book-service) |
| 5 | book-service | 8005 | CRUD sách, batch API cho cart |
| 6 | cart-service | 8006 | FR3: Giỏ hàng – thêm/xem/cập nhật/xóa |
| 7 | order-service | 8007 | FR4: Đơn hàng, Saga (pay + ship) |
| 8 | ship-service | 8008 | Reserve/release vận chuyển |
| 9 | pay-service | 8009 | Reserve/release thanh toán |
| 10 | comment-rate-service | 8010 | FR5: Đánh giá sách |
| 11 | recommender-ai-service | 8011 | Gợi ý sách |
| 12 | api-gateway | 8000 | Điểm vào duy nhất, định tuyến tới các service |

---

## 2. Functional Requirements (4.3)

### FR1: Customer registration automatically creates a cart
- **Luồng:** Client gửi POST /api/customers/ với name, email → customer-service lưu Customer → gọi POST http://cart-service:8000/api/cart/create/ với customer_id → cart-service tạo Cart.
- **Code:** Xem `docs/CODE_GUIDE.md` mục 1.2 (CustomerListCreate post).

### FR2: Staff manages books
- Staff gọi GET/POST/PUT/DELETE /api/staff/books/ qua Gateway; staff-service proxy sang book-service. Book-service cung cấp API CRUD và có thể dùng Django Admin.

### FR3: Customer adds books to cart, view cart, update cart
- **Thêm:** POST /api/cart/add/<customer_id>/ với book_id, quantity. Cart-service kiểm tra customer và book tồn tại qua REST, thêm/cập nhật CartItem.
- **Xem:** GET /api/cart/view/<customer_id>/ – trả về items kèm thông tin sách (gọi book-service batch).
- **Cập nhật/xóa:** PATCH /api/cart/update/..., DELETE /api/cart/remove/...

### FR4: Order triggers payment and shipping
- Order-service thực hiện Saga: lấy giỏ → tính tổng → tạo Order pending → reserve pay → reserve ship. Thành công → status=completed; thất bại → compensate (release pay, release ship), status=failed. Chi tiết code trong `docs/CODE_GUIDE.md` mục 3.

### FR5: Customer can rate books
- POST /api/reviews/rate/ với book_id, customer_id, rating (1–5), comment. Comment-rate-service kiểm tra sách tồn tại qua book-service, dùng update_or_create. GET /api/reviews/book/<book_id>/ trả về danh sách đánh giá và điểm trung bình.

---

## 3. Technical Requirements (4.4)

- **Django REST Framework:** Tất cả service dùng DRF (APIView, ModelSerializer) hoặc Django view (Gateway).
- **REST inter-service calls:** requests (Python) để gọi HTTP giữa các service; URL lấy từ biến môi trường (Docker Compose).
- **Docker Compose:** Một file docker-compose.yml định nghĩa 12 service + api-gateway, mỗi service có build từ Dockerfile riêng, port mapping và environment (URL các service khác).
- **Independent databases:** Mỗi service có db.sqlite3 riêng (hoặc có thể cấu hình MySQL per service). Cart lưu customer_id, book_id dạng Integer, không dùng ForeignKey sang DB khác.

---

## 4. Kiến trúc và Database per Service

- **Sơ đồ:** Xem `docs/ARCHITECTURE.md` (sơ đồ ASCII và bảng Database per Service).
- **Nguyên tắc:** Cart-service không lưu bảng Book/Customer; khi cần dữ liệu chi tiết thì gọi REST API của book-service và customer-service. Order-service điều phối pay-service và ship-service theo mô hình Saga.

---

## 5. API Documentation

- Toàn bộ endpoint qua API Gateway (port 8000) được liệt kê trong `docs/API.md`, kèm method, path, body và ví dụ curl.

---

## 6. Cấu trúc mã nguồn và giải thích code

- Cấu trúc thư mục: `bookstore-microservice/` chứa từng thư mục service (customer-service, book-service, cart-service, ...), mỗi thư mục là một Django project.
- Giải thích chi tiết từng phần code (FR1, FR3, FR4, FR5, Gateway, Database per Service) nằm trong `docs/CODE_GUIDE.md`, có thể trích trực tiếp vào báo cáo 8–12 trang.

---

## 7. Chạy hệ thống và Deliverables

- **Chạy:** `cd bookstore-microservice && docker compose up --build`. Truy cập API qua http://localhost:8000.
- **Deliverables đáp ứng:** (1) Mã nguồn (GitHub), (2) Sơ đồ kiến trúc (ARCHITECTURE.md), (3) API documentation (API.md), (4) Demo video 10 phút (thực hiện riêng), (5) Báo cáo kỹ thuật 8–12 trang (có thể dựa trên BÁO_CAO_KY_THUAT_ASS05.md và CODE_GUIDE.md).

---

*Tài liệu này dùng làm khung báo cáo kỹ thuật Assignment 05; có thể mở rộng từng mục với sơ đồ PlantUML, bảng so sánh, và trích dẫn code từ repo.*
