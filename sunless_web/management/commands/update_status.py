"""
rest_entiries_by_entities 커맨드용 클래스 파일
"""
import tqdm
from django.core.management.base import BaseCommand
from django.db import transaction

from sunless_web.models import Entry, EntryPath


class Command(BaseCommand):
    help = 'Update all status for Entry & EntityPath'

    @transaction.atomic
    def handle(self, *args, **options):
        for entry in tqdm.tqdm(Entry.objects.all()):
            entry.update_status()

        for entry_path in tqdm.tqdm(EntryPath.objects.all()):
            entry_path.update_status()
