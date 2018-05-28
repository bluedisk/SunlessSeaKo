from django.core.management.base import BaseCommand
from sunless_web.models import Entity
from tqdm import tqdm


class Command(BaseCommand):

    def handle(self, *args, **options):
        for e in tqdm(Entity.objects.all()):
            e.save()
