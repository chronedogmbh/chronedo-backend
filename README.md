# Chronedo App

celery -A chronoapp worker -l info --pool=solo
celery -A chronoapp worker -l info

celery -A chronoapp beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
