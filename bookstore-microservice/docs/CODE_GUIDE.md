# Hướng dẫn Code – Giải thích từng phần (Assignment 05)

Tài liệu này giải thích chi tiết các đoạn code quan trọng trong từng service, giúp báo cáo kỹ thuật đạt chuẩn và dễ đạt điểm tối đa.

---

## 1. Customer-Service – FR1 (Đăng ký tự tạo giỏ)

### 1.1 Model `Customer` (customers/models.py)

```python
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Giải thích:** Mỗi microservice sở hữu database riêng. Customer-service chỉ lưu dữ liệu khách hàng trong bảng của mình; không có bảng Cart hay Book ở đây. `unique=True` trên email đảm bảo không trùng email khi đăng ký.

### 1.2 View `CustomerListCreate` – POST tạo customer và gọi Cart (customers/views.py)

```python
def post(self, request):
    serializer = CustomerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    customer = serializer.save()
    # FR1: Tự động tạo cart khi đăng ký – gọi cart-service qua REST
    try:
        r = requests.post(
            f"{CART_SERVICE_URL}/api/cart/create/",
            json={"customer_id": customer.id},
            timeout=5,
        )
        if r.status_code not in (200, 201):
            logger.warning("Cart creation returned %s: %s", r.status_code, r.text)
    except requests.RequestException as e:
        logger.exception("Failed to create cart for customer %s: %s", customer.id, e)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

**Giải thích:**  
- Sau khi lưu Customer vào DB của customer-service, ta **không** gọi hàm nội bộ để tạo Cart vì Cart nằm ở service khác.  
- Thay vào đó, gửi **HTTP POST** tới cart-service với `customer_id`. Đây là **inter-service REST communication** – nguyên tắc loose coupling: service không import model của service kia, chỉ giao tiếp qua API.  
- Dùng `timeout=5` và try/except để tránh block; nếu cart-service lỗi, customer vẫn đã được tạo (có thể xử lý bù trừ hoặc retry sau).

---

## 2. Cart-Service – Database per Service (chỉ lưu ID)

### 2.1 Model Cart, CartItem (cart/models.py)

```python
class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)  # Không phải ForeignKey(Customer)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book_id = models.IntegerField()  # Không phải ForeignKey(Book)
    quantity = models.PositiveIntegerField(default=1)
```

**Giải thích:**  
- **Database per Service:** Cart và Customer nằm ở hai DB khác nhau, nên **không thể** dùng `ForeignKey(Customer)`. Chỉ lưu `customer_id` (Integer). Tương tự, không có bảng Book trong cart-service nên dùng `book_id` (Integer).  
- Khi cần tên sách, giá, cart-service sẽ gọi **GET /api/books/batch/?ids=1&ids=2** của book-service để lấy dữ liệu theo lô (batch), tránh gọi từng sách một.

### 2.2 Kiểm tra Customer/Book tồn tại trước khi thêm vào giỏ (cart/views.py)

```python
def _customer_exists(customer_id):
    try:
        r = requests.get(f"{CUSTOMER_SERVICE_URL}/api/customers/{customer_id}/", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False
```

**Giải thích:** Cart-service không có bảng Customer, nên để validate “khách hàng có tồn tại không” phải gọi REST API của customer-service. Đây là cách làm chuẩn trong microservices: **validate qua API**, không share database.

---

## 3. Order-Service – FR4 (Saga: Order → Pay → Ship, có bù trừ)

### 3.1 Luồng tạo đơn (order_app/views.py)

1. Lấy giỏ từ cart-service (`/api/cart/by-customer/<customer_id>/`).  
2. Lấy giá sách từ book-service (`/api/books/batch/?ids=...`) để tính tổng.  
3. Tạo bản ghi Order với `status="pending"`.  
4. Gọi pay-service **POST /api/pay/reserve/** (reserve thanh toán).  
5. Gọi ship-service **POST /api/ship/reserve/** (reserve vận chuyển).  
6. Nếu cả hai thành công → cập nhật Order `status="completed"`.  
7. Nếu bất kỳ bước nào thất bại → **compensate**: gọi **release** pay và ship, cập nhật Order `status="failed"`.

**Đoạn code chính (rút gọn):**

```python
# Bước 2: Reserve payment
r_pay = requests.post(f"{PAY_SERVICE_URL}/api/pay/reserve/", ...)
if r_pay.status_code not in (200, 201):
    raise Exception(...)
pay_reservation_id = r_pay.json().get("id")

# Bước 3: Reserve shipping
r_ship = requests.post(f"{SHIP_SERVICE_URL}/api/ship/reserve/", ...)
if r_ship.status_code not in (200, 201):
    raise Exception(...)

# Bước 4: Confirm
order.status = "completed"
order.save(update_fields=["status"])
return Response(...)

except Exception as e:
    # Compensation
    if pay_reservation_id:
        requests.post(f"{PAY_SERVICE_URL}/api/pay/{pay_reservation_id}/release/", ...)
    if ship_reservation_id:
        requests.post(f"{SHIP_SERVICE_URL}/api/ship/{ship_reservation_id}/release/", ...)
    order.status = "failed"
    order.save(update_fields=["status"])
```

**Giải thích:** Đây là mô hình **Saga đơn giản** (orchestration): order-service điều phối từng bước. Mỗi bước có **compensating transaction** (release) để khi lỗi có thể hoàn tác, đảm bảo tính nhất quán cuối cùng (eventual consistency).

---

## 4. Comment-Rate-Service – FR5 (Đánh giá sách)

### 4.1 Model Review (reviews/models.py)

```python
class Review(models.Model):
    book_id = models.IntegerField()      # Tham chiếu tới book-service
    customer_id = models.IntegerField()
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    unique_together = [["book_id", "customer_id"]]
```

**Giải thích:** Mỗi cặp (book_id, customer_id) chỉ có một đánh giá; cập nhật đánh giá dùng `update_or_create` trong view.

### 4.2 Kiểm tra sách tồn tại trước khi rate (reviews/views.py)

```python
if not _book_exists(book_id):
    return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
obj, created = Review.objects.update_or_create(
    book_id=book_id, customer_id=customer_id,
    defaults={"rating": rating, "comment": comment},
)
```

**Giải thích:** Comment-rate-service không lưu bảng Book; để đảm bảo “sách tồn tại” phải gọi **GET /api/books/<id>/** của book-service. Đây là **validation qua API** giữa các service.

---

## 5. API Gateway – Định tuyến theo path

### 5.1 Proxy (gateway/views.py)

```python
def proxy_request(service_key, request):
    base = BASE.get(service_key, "")  # BASE["customer"] = "http://customer-service:8000"
    path = request.path
    if request.GET:
        path += "?" + request.GET.urlencode()
    url = f"{base.rstrip('/')}{path}"
    # ... requests.get/post/put/patch/delete(url, ...)
    return HttpResponse(r.content, status=r.status_code, ...)
```

**Giải thích:** Client chỉ cần gọi **một điểm vào** (Gateway, port 8000). Gateway dựa vào `request.path` (ví dụ `/api/customers/`, `/api/cart/add/1/`) để map tới `service_key` (customer, cart, ...) và forward toàn bộ request tới base URL của service tương ứng. Các biến môi trường (CUSTOMER_SERVICE_URL, CART_SERVICE_URL, ...) được Docker Compose truyền vào.

### 5.2 Routing (gateway/urls.py)

Các path `/api/customers/...`, `/api/cart/...`, `/api/orders/...` được map tới từng ProxyView với `service_key` tương ứng (customer, cart, order, ...), đảm bảo mọi request tới đúng backend service.

---

## 6. Staff-Service – FR2 (Proxy tới Book-Service)

Staff-service **không** có bảng Book; nó chỉ **proxy** request tới book-service:

```python
def get(self, request):
    r = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
    r.raise_for_status()
    return Response(r.json())
```

**Giải thích:** FR2 yêu cầu “Staff manages books”. Có hai cách: (1) Staff gọi trực tiếp book-service, hoặc (2) qua staff-service làm proxy. Ở đây staff-service đóng vai trò **BFF/proxy** cho nghiệp vụ “staff”, có thể sau này thêm phân quyền, audit log tại đây.

---

## 7. Docker Compose – Môi trường giữa các service

Trong `docker-compose.yml`, mỗi service có `environment` chứa URL của các service khác, ví dụ:

```yaml
cart-service:
  environment:
    - CUSTOMER_SERVICE_URL=http://customer-service:8000
    - BOOK_SERVICE_URL=http://book-service:8000
```

**Giải thích:** Trong Docker network, các container gọi nhau bằng **tên service** (customer-service, book-service), không dùng localhost. Điều này cho phép mỗi service chạy trên một container, đúng mô hình microservices.

---

## Tóm tắt nguyên tắc đã áp dụng

| Nguyên tắc | Thể hiện trong code |
|------------|----------------------|
| Database per Service | Cart lưu customer_id, book_id (Integer); không FK sang DB khác. |
| Inter-service REST | customer-service POST tới cart-service; cart gọi customer/book để validate và lấy dữ liệu. |
| Saga (FR4) | order-service: reserve pay → reserve ship → confirm; lỗi thì release (compensate). |
| API Gateway | Một điểm vào, forward theo path tới đúng backend. |
| Validation qua API | cart-service kiểm tra customer/book tồn tại bằng GET tới service tương ứng. |

Khi viết báo cáo 8–12 trang, bạn có thể trích từng đoạn code trên và giải thích tương ứng như trong CODE_GUIDE.md để đạt tiêu chí “chi tiết, chuẩn senior”.
