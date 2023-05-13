from django.core import management

from celery import shared_task


@shared_task
def scrape_watches(max_pages, per_page):
    management.call_command("scrape_watches", max_pages, per_page)
