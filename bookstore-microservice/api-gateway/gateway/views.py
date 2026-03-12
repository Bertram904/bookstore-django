import logging
import os

import requests
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Base URLs từ environment (Docker Compose truyền vào)
BASE = {
    "customer": os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8000"),
    "staff": os.environ.get("STAFF_SERVICE_URL", "http://staff-service:8000"),
    "manager": os.environ.get("MANAGER_SERVICE_URL", "http://manager-service:8000"),
    "catalog": os.environ.get("CATALOG_SERVICE_URL", "http://catalog-service:8000"),
    "book": os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000"),
    "cart": os.environ.get("CART_SERVICE_URL", "http://cart-service:8000"),
    "order": os.environ.get("ORDER_SERVICE_URL", "http://order-service:8000"),
    "ship": os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8000"),
    "pay": os.environ.get("PAY_SERVICE_URL", "http://pay-service:8000"),
    "comment": os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000"),
    "recommender": os.environ.get("RECOMMENDER_SERVICE_URL", "http://recommender-ai-service:8000"),
}

TIMEOUT = 30
logger = logging.getLogger(__name__)


def proxy_request(service_key, request):
    base = BASE.get(service_key, "")
    if not base:
        return HttpResponse('{"error":"Unknown service"}', status=502, content_type="application/json")
    path = request.path
    if request.GET:
        path += "?" + request.GET.urlencode()
    url = f"{base.rstrip('/')}{path}"
    method = request.method
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "connection", "content-length")
    }
    logger.info("Proxy %s %s -> %s", method, request.path, url)
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            r = requests.post(url, data=request.body, headers=headers, timeout=TIMEOUT)
        elif method == "PUT":
            r = requests.put(url, data=request.body, headers=headers, timeout=TIMEOUT)
        elif method == "PATCH":
            r = requests.patch(url, data=request.body, headers=headers, timeout=TIMEOUT)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return HttpResponse('{"error":"Method not allowed"}', status=405, content_type="application/json")
    except requests.RequestException as e:
        logger.exception("Proxy error for %s %s: %s", method, request.path, e)
        return HttpResponse(f'{{"error":"{str(e)}"}}', status=502, content_type="application/json")
    logger.info("Proxy response %s %s -> %s", method, request.path, r.status_code)
    resp_headers = {k: v for k, v in r.headers.items() if k.lower() in ("content-type",)}
    return HttpResponse(r.content, status=r.status_code, headers=resp_headers)


@method_decorator(csrf_exempt, name="dispatch")
class ProxyView(View):
    service_key = None

    def get(self, request, path=""):
        return proxy_request(self.service_key, request)

    def post(self, request, path=""):
        return proxy_request(self.service_key, request)

    def put(self, request, path=""):
        return proxy_request(self.service_key, request)

    def patch(self, request, path=""):
        return proxy_request(self.service_key, request)

    def delete(self, request, path=""):
        return proxy_request(self.service_key, request)
