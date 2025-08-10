echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Running migrations..."
python manage.py migrate