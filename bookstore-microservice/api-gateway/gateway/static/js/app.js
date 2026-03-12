var app = (function() {
    'use strict';
    var CUSTOMER_KEY = 'bookstore_customer_id';

    function getCookie(name) {
        var v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    function api(method, url, body) {
        var opts = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        };
        if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH'))
            opts.body = typeof body === 'string' ? body : JSON.stringify(body);
        return fetch(url, opts).then(function(r) {
            var ct = r.headers.get('Content-Type') || '';
            if (ct.indexOf('application/json') !== -1)
                return r.json().then(function(data) {
                    if (!r.ok) throw { status: r.status, data: data };
                    return data;
                });
            if (!r.ok) throw { status: r.status, data: null };
            return r.text();
        });
    }

    function getCustomerId() {
        return localStorage.getItem(CUSTOMER_KEY) || '';
    }
    function setCustomerId(id) {
        localStorage.setItem(CUSTOMER_KEY, String(id));
    }

    function loadBooks(selector, url) {
        var el = document.querySelector(selector);
        if (!el) return;
        api('GET', url).then(function(data) {
            var list = Array.isArray(data) ? data : (data.recommendations || []);
            if (list.length === 0) {
                el.innerHTML = '<p class="empty-state">Chưa có sách nào.</p>';
                return;
            }
            el.innerHTML = list.map(function(b) {
                return '<div class="book-card">' +
                    '<a href="/book/' + b.id + '/">' +
                    '<h3>' + escapeHtml(b.title) + '</h3>' +
                    '<p class="author">' + escapeHtml(b.author) + '</p>' +
                    '<p class="price">' + formatPrice(b.price) + '</p>' +
                    '</a></div>';
            }).join('');
        }).catch(function(e) {
            el.innerHTML = '<p class="message error">Lỗi tải dữ liệu.</p>';
        });
    }

    function escapeHtml(s) {
        if (s == null) return '';
        var div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }
    function formatPrice(p) {
        if (p == null) return '—';
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(p));
    }

    function renderUserBlock(selector) {
        var id = getCustomerId();
        var el = document.querySelector(selector);
        if (!el) return;
        if (id) {
            el.innerHTML = '<span>Xin chào, khách #' + id + '</span> | ' +
                '<a href="/cart/?customer_id=' + encodeURIComponent(id) + '" class="header-link">Giỏ hàng</a> | ' +
                '<a href="#" id="logout-btn" class="header-link">Đăng xuất</a>';
        } else {
            el.innerHTML = '<a href="/login/" class="header-link">Đăng nhập</a> | ' +
                '<a href="/register/" class="header-link">Đăng ký</a>';
        }
        setupLogoutButton();
    }

    function setupLogoutButton() {
        var logoutBtn = document.getElementById('logout-btn');
        if (!logoutBtn) return;
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem(CUSTOMER_KEY);
            window.location.href = '/';
        });
    }

    function setupLoginForm() {
        var form = document.getElementById('login-form');
        var msg = document.getElementById('login-message');
        if (!form || !msg) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            msg.textContent = '';
            msg.className = 'message';
            var email = document.getElementById('login-email').value.trim();
            var id = document.getElementById('login-id').value.trim();
            if (id) {
                setCustomerId(id);
                renderUserBlock('#header-user');
                window.location.href = '/';
                return;
            }
            api('GET', '/api/customers/').then(function(customers) {
                var found = customers.find(function(c) { return c.email === email; });
                if (found) {
                    setCustomerId(found.id);
                    renderUserBlock('#header-user');
                    window.location.href = '/';
                } else {
                    msg.className = 'message error';
                    msg.textContent = 'Không tìm thấy khách hàng. Vui lòng đăng ký trước.';
                }
            }).catch(function() {
                msg.className = 'message error';
                msg.textContent = 'Lỗi khi đăng nhập. Vui lòng thử lại.';
            });
        });
    }

    function setupRegisterForm() {
        var form = document.getElementById('register-form');
        var msg = document.getElementById('register-message');
        if (!form || !msg) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            msg.textContent = '';
            msg.className = 'message';
            var name = document.getElementById('reg-name').value.trim();
            var email = document.getElementById('reg-email').value.trim();
            api('POST', '/api/customers/', { name: name, email: email })
                .then(function(data) {
                    setCustomerId(data.id);
                    renderUserBlock('#header-user');
                    msg.className = 'message success';
                    msg.textContent = 'Đăng ký thành công. Bạn là khách hàng #' + data.id + '. Giỏ hàng đã được tạo (FR1).';
                })
                .catch(function(err) {
                    msg.className = 'message error';
                    msg.textContent = (err.data && err.data.email) ? err.data.email[0] : (err.data && err.data.error) || 'Đăng ký thất bại.';
                });
        });
    }

    function loadCart(customerId) {
        var content = document.getElementById('cart-content');
        var itemsEl = document.getElementById('cart-items');
        var empty = document.getElementById('cart-empty');
        var prompt = document.getElementById('cart-customer-prompt');
        var link = document.getElementById('cart-checkout-link');
        if (!content || !itemsEl) return;
        prompt.style.display = 'none';
        api('GET', '/api/cart/view/' + customerId + '/').then(function(data) {
            var items = data.items || [];
            if (items.length === 0) {
                content.style.display = 'none';
                if (empty) empty.style.display = 'block';
                return;
            }
            if (empty) empty.style.display = 'none';
            content.style.display = 'block';
            itemsEl.innerHTML = items.map(function(it) {
                return '<div class="cart-item" data-item-id="' + it.id + '">' +
                    '<div><span class="title">' + escapeHtml(it.title || 'Sách #' + it.book_id) + '</span><br><span class="meta">SL: ' + it.quantity + ' × ' + formatPrice(it.price) + '</span></div>' +
                    '<div><input type="number" class="qty" min="1" value="' + it.quantity + '" data-item-id="' + it.id + '"> <button type="button" class="btn btn-danger btn-small btn-remove-cart" data-customer-id="' + customerId + '" data-item-id="' + it.id + '">Xóa</button></div>' +
                    '</div>';
            }).join('');
            if (link) link.href = '/checkout/?customer_id=' + customerId;
            itemsEl.querySelectorAll('.qty').forEach(function(input) {
                input.addEventListener('change', function() {
                    var id = this.dataset.itemId;
                    var qty = parseInt(this.value, 10);
                    if (qty < 1) return;
                    api('PATCH', '/api/cart/update/' + customerId + '/' + id + '/', { quantity: qty })
                        .then(function() { loadCart(customerId); });
                });
            });
            itemsEl.querySelectorAll('.btn-remove-cart').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    api('DELETE', '/api/cart/remove/' + this.dataset.customerId + '/' + this.dataset.itemId + '/')
                        .then(function() { loadCart(customerId); });
                });
            });
        }).catch(function() {
            content.style.display = 'none';
            if (empty) { empty.style.display = 'block'; empty.innerHTML = 'Không tìm thấy giỏ hàng hoặc chưa đăng ký.'; }
        });
    }

    function setupCartCustomerForm() {
        var form = document.getElementById('cart-customer-form');
        if (!form) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var id = document.getElementById('cart-customer-id').value;
            if (id) loadCart(id);
        });
    }

    function loadShipOptions() {
        var select = document.getElementById('checkout-shipper');
        if (!select) return;

        // Prefill with defaults cho trường hợp /api/ship chưa có
        var defaultOptions = [
            { id: 'fastship', name: 'FastShip (Nhanh)' },
            { id: 'standard', name: 'Standard Express' },
            { id: 'green', name: 'Green Delivery (Tiết kiệm)' }
        ];

        function render(options) {
            select.innerHTML = '<option value="">-- Vui lòng chọn --</option>' +
                options.map(function(s) {
                    return '<option value="' + s.id + '">' + s.name + '</option>';
                }).join('');
        }

        api('GET', '/api/ship/shippers/').then(function(data) {
            if (Array.isArray(data) && data.length) {
                render(data);
            } else {
                render(defaultOptions);
            }
        }).catch(function() {
            render(defaultOptions);
        });
    }

    function setupCheckoutForm() {
        var form = document.getElementById('checkout-form');
        var msg = document.getElementById('checkout-message');
        if (!form || !msg) return;
        var q = new URLSearchParams(window.location.search);
        if (q.get('customer_id')) document.getElementById('checkout-customer-id').value = q.get('customer_id');
        loadShipOptions();
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            msg.textContent = '';
            msg.className = 'message';
            var customerId = document.getElementById('checkout-customer-id').value;
            var address = document.getElementById('checkout-address').value.trim();
            var shipper = document.getElementById('checkout-shipper').value;
            if (!shipper) {
                msg.className = 'message error';
                msg.textContent = 'Vui lòng chọn đơn vị giao hàng.';
                return;
            }
            api('POST', '/api/orders/create/', { customer_id: parseInt(customerId, 10), address: address, shipper: shipper })
                .then(function(data) {
                    msg.className = 'message success';
                    msg.textContent = 'Đặt hàng thành công. Mã đơn: #' + data.id + ', trạng thái: ' + data.status + ' (FR4: Saga). ' +
                        'Đơn vị giao hàng: ' + (data.shipper || shipper);
                })
                .catch(function(err) {
                    msg.className = 'message error';
                    msg.textContent = (err.data && err.data.error) || 'Đặt hàng thất bại.';
                });
        });
    }

    function loadStaffBooks() {
        var el = document.getElementById('staff-books-list');
        if (!el) return;
        api('GET', '/api/staff/books/').then(function(list) {
            if (!list || list.length === 0) {
                el.innerHTML = '<p class="empty-state">Chưa có sách.</p>';
                return;
            }
            el.innerHTML = '<table class="staff-table"><thead><tr><th>ID</th><th>Tên sách</th><th>Tác giả</th><th>Giá</th><th>Tồn kho</th><th>Thao tác</th></tr></thead><tbody>' +
                list.map(function(b) {
                    return '<tr><td>' + b.id + '</td><td>' + escapeHtml(b.title) + '</td><td>' + escapeHtml(b.author) + '</td><td>' + formatPrice(b.price) + '</td><td>' + (b.stock || 0) + '</td><td class="actions"><button type="button" class="btn btn-primary btn-small btn-edit" data-id="' + b.id + '">Sửa</button> <button type="button" class="btn btn-danger btn-small btn-delete" data-id="' + b.id + '">Xóa</button></td></tr>';
                }).join('') + '</tbody></table>';
            el.querySelectorAll('.btn-edit').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var id = this.dataset.id;
                    var row = this.closest('tr');
                    document.getElementById('edit-book-id').value = id;
                    document.getElementById('edit-title').value = row.cells[1].textContent;
                    document.getElementById('edit-author').value = row.cells[2].textContent;
                    document.getElementById('edit-price').value = row.cells[3].textContent.replace(/[^\d.,]/g, '').replace(',', '.');
                    document.getElementById('edit-stock').value = row.cells[4].textContent;
                    document.getElementById('staff-edit-modal').style.display = 'flex';
                });
            });
            el.querySelectorAll('.btn-delete').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    if (!confirm('Xóa sách này?')) return;
                    api('DELETE', '/api/staff/books/' + this.dataset.id + '/').then(function() { app.loadStaffBooks(); });
                });
            });
        }).catch(function() {
            el.innerHTML = '<p class="message error">Lỗi tải danh sách.</p>';
        });
    }

    function setupStaffForms() {
        var addForm = document.getElementById('staff-add-form');
        if (addForm) {
            addForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var payload = {
                    title: document.getElementById('staff-title').value.trim(),
                    author: document.getElementById('staff-author').value.trim(),
                    price: document.getElementById('staff-price').value,
                    stock: parseInt(document.getElementById('staff-stock').value, 10) || 0
                };
                api('POST', '/api/staff/books/', payload).then(function() {
                    addForm.reset();
                    loadStaffBooks();
                }).catch(function(err) {
                    alert((err.data && (err.data.title && err.data.title[0]) || err.data.error) || 'Lỗi thêm sách.');
                });
            });
        }
        var editForm = document.getElementById('staff-edit-form');
        var modal = document.getElementById('staff-edit-modal');
        if (editForm && modal) {
            editForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var id = document.getElementById('edit-book-id').value;
                var payload = {
                    title: document.getElementById('edit-title').value.trim(),
                    author: document.getElementById('edit-author').value.trim(),
                    price: document.getElementById('edit-price').value,
                    stock: parseInt(document.getElementById('edit-stock').value, 10) || 0
                };
                api('PUT', '/api/staff/books/' + id + '/', payload).then(function() {
                    modal.style.display = 'none';
                    loadStaffBooks();
                });
            });
            modal.querySelector('.modal-close').addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }
    }

    function loadManagerDashboard() {
        var el = document.getElementById('manager-stats');
        if (!el) return;
        api('GET', '/api/manager/dashboard/').then(function(data) {
            el.innerHTML = '<div class="stat-card"><div class="value">' + (data.customers_count || 0) + '</div><div class="label">Khách hàng</div></div>' +
                '<div class="stat-card"><div class="value">' + (data.books_count || 0) + '</div><div class="label">Sách</div></div>' +
                '<div class="stat-card"><div class="value">' + (data.orders_count || 0) + '</div><div class="label">Đơn hàng</div></div>';
        }).catch(function() {
            el.innerHTML = '<p class="message error">Lỗi tải dashboard.</p>';
        });
    }

    function loadBookDetail(bookId) {
        var el = document.getElementById('book-detail');
        if (!el) return;
        api('GET', '/api/books/' + bookId + '/').then(function(b) {
            el.innerHTML = '<h1>' + escapeHtml(b.title) + '</h1><p class="author">' + escapeHtml(b.author) + '</p><p class="price">' + formatPrice(b.price) + '</p><p>Tồn kho: ' + (b.stock || 0) + '</p>';
        }).catch(function() {
            el.innerHTML = '<p class="message error">Không tìm thấy sách.</p>';
        });
    }

    function loadReviews(bookId) {
        var el = document.getElementById('reviews-list');
        if (!el) return;
        api('GET', '/api/reviews/book/' + bookId + '/').then(function(data) {
            var html = '';
            if (data.average_rating != null)
                html += '<p><strong>Điểm trung bình: ' + data.average_rating.toFixed(1) + '/5</strong></p>';
            (data.reviews || []).forEach(function(r) {
                html += '<div class="review-item"><span class="rating">' + r.rating + '/5</span> — ' + escapeHtml(r.comment || '(không nhận xét)') + '</div>';
            });
            el.innerHTML = html || '<p>Chưa có đánh giá.</p>';
        }).catch(function() {
            el.innerHTML = '<p>Không tải được đánh giá.</p>';
        });
    }

    function setupBookDetailForms(bookId) {
        var cid = getCustomerId();
        if (cid) {
            document.getElementById('detail-customer-id').value = cid;
        }
        var addForm = document.getElementById('add-to-cart-form');
        if (addForm) {
            addForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var customerId = document.getElementById('detail-customer-id').value;
                var quantity = document.getElementById('detail-quantity').value || 1;
                api('POST', '/api/cart/add/' + customerId + '/', { book_id: parseInt(bookId, 10), quantity: parseInt(quantity, 10) })
                    .then(function() {
                        alert('Đã thêm vào giỏ.');
                    })
                    .catch(function(err) {
                        alert((err.data && err.data.error) || 'Lỗi thêm vào giỏ.');
                    });
            });
        }
        var reviewForm = document.getElementById('review-form');
        if (reviewForm) {
            if (cid) document.getElementById('review-customer-id').value = cid;
            reviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                api('POST', '/api/reviews/rate/', {
                    book_id: parseInt(bookId, 10),
                    customer_id: parseInt(document.getElementById('review-customer-id').value, 10),
                    rating: parseInt(document.getElementById('review-rating').value, 10),
                    comment: document.getElementById('review-comment').value.trim()
                }).then(function() {
                    loadReviews(bookId);
                    reviewForm.reset();
                    document.getElementById('review-customer-id').value = cid || document.getElementById('review-customer-id').value;
                }).catch(function(err) {
                    alert((err.data && err.data.error) || 'Lỗi gửi đánh giá.');
                });
            });
        }
    }

    return {
        getCustomerId: getCustomerId,
        setCustomerId: setCustomerId,
        loadBooks: loadBooks,
        renderUserBlock: renderUserBlock,
        setupRegisterForm: setupRegisterForm,
        loadCart: loadCart,
        setupCartCustomerForm: setupCartCustomerForm,
        setupCheckoutForm: setupCheckoutForm,
        loadStaffBooks: loadStaffBooks,
        setupStaffForms: setupStaffForms,
        loadManagerDashboard: loadManagerDashboard,
        loadBookDetail: loadBookDetail,
        loadReviews: loadReviews,
        setupBookDetailForms: setupBookDetailForms
    };
})();
