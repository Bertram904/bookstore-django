set -e
python manage.py migrate --noinput
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'); password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123'); email='admin@bookstore.local'; User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"
python manage.py runserver 0.0.0.0:8000
