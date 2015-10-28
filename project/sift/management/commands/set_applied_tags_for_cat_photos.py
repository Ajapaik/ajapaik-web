from django.core.management.base import BaseCommand
from project.sift.models import CatTagPhoto, CatRealTag, CatAppliedTag


class Command(BaseCommand):
    help = "Will apply tags to photos based on criteria"

    def handle(self, *args, **options):
        tags = CatTagPhoto.objects.prefetch_related('tag')
        real_tags = CatRealTag.objects.all()
        tag_tally = {}
        for t in tags:
            if t.photo_id not in tag_tally:
                tag_tally[t.photo_id] = {}
            if t.tag.name not in tag_tally[t.photo_id]:
                tag_tally[t.photo_id][t.tag.name] = [0, 0, 0]
            if t.value == 1:
                tag_tally[t.photo_id][t.tag.name][2] += 1
            elif t.value == 0:
                tag_tally[t.photo_id][t.tag.name][1] += 1
            elif t.value == -1:
                tag_tally[t.photo_id][t.tag.name][0] += 1

        CatAppliedTag.objects.all().delete()
        for pk, pv in tag_tally.items():
            for tk, tv in pv.items():
                parts = tk.split('_')
                if tv[0] > 1:
                    CatAppliedTag(
                        photo_id=pk,
                        tag=real_tags.filter(name=parts[0]).first()
                    ).save()
                if tv[1] > 1:
                    CatAppliedTag(
                        photo_id=pk,
                        tag=real_tags.filter(name=tk + '_NA').first()
                    ).save()
                if tv[2] > 1:
                    CatAppliedTag(
                        photo_id=pk,
                        tag=real_tags.filter(name=parts[-1]).first()
                    ).save()