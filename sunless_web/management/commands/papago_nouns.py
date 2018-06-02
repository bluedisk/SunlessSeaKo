from django.core.management.base import BaseCommand
from sunless_web.models import Noun

from tqdm import tqdm
from modules.papago import papago


class Command(BaseCommand):

    def handle(self, *args, **options):
        translate_count = 0
        error_count = 0
        for noun in tqdm(Noun.objects.all()):
            if not noun.papago:

                transed = papago(noun.nema, True)

                translate_count += 1
                noun.papago = transed
                noun.save()

        print("succ", translate_count, "err", error_count)
