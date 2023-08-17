from django.core import management

from celery import shared_task


@shared_task
def scrape_watches(task_id: int):
    management.call_command("scrape_watches_country_task", task_id)
