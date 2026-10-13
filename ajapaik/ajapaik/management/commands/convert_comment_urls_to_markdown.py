import json
import logging
import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from ajapaik.ajapaik.models import MyXtdComment
from ajapaik.ajapaik_comments.utils import convert_raw_urls_to_markdown

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Convert raw unformatted URLs in comments to Markdown links [url](url)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate changes without saving to the database",
        )
        parser.add_argument(
            "--backup-file",
            type=str,
            default=None,
            help="Path to JSON file to save original comment backups",
        )
        parser.add_argument(
            "--comment-id",
            type=int,
            default=None,
            help="Process a specific comment by ID",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of comments to process",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        backup_file = options["backup_file"]
        comment_id = options["comment_id"]
        limit = options["limit"]

        if dry_run:
            self.stdout.write(self.style.WARNING("=== DRY RUN MODE: No database changes will be saved ==="))

        queryset = MyXtdComment.objects.all().order_by("id")
        if comment_id:
            queryset = queryset.filter(id=comment_id)
        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        self.stdout.write(f"Total comments to check: {total}")

        backup_data = []
        modified_count = 0

        # Collect changes
        updates = []
        for c in queryset.iterator():
            new_text, is_mod = convert_raw_urls_to_markdown(c.comment)
            if is_mod:
                modified_count += 1
                backup_data.append({
                    "id": c.id,
                    "submit_date": str(c.submit_date),
                    "user_id": c.user_id,
                    "original_comment": c.comment,
                    "new_comment": new_text,
                })
                updates.append((c, new_text))

        self.stdout.write(f"Found {modified_count} comments containing unformatted URLs.")

        # Show samples
        sample_count = min(5, len(backup_data))
        if sample_count > 0:
            self.stdout.write(self.style.NOTICE(f"\n--- Showing {sample_count} sample conversions: ---"))
            for item in backup_data[:sample_count]:
                self.stdout.write(f"ID {item['id']}:")
                self.stdout.write(self.style.ERROR("OLD: " + item["original_comment"].strip()))
                self.stdout.write(self.style.SUCCESS("NEW: " + item["new_comment"].strip()))
                self.stdout.write("-" * 40)

        # Save backup file
        if backup_data:
            if not backup_file:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"comment_urls_backup_{ts}.json"

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Saved backup of {len(backup_data)} comments to: {backup_file}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run finished. Database was not modified."))
            return

        if not updates:
            self.stdout.write("Nothing to update.")
            return

        # Perform atomic update
        self.stdout.write(f"Applying updates to {len(updates)} comments...")
        with transaction.atomic():
            for comment_obj, new_text in updates:
                comment_obj.comment = new_text
                comment_obj.save(update_fields=["comment"])

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(updates)} comments!"))
