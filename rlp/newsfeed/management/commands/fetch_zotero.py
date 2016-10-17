import sys

from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from django.utils import timezone

import iso8601
from pyzotero import zotero

from rlp.newsfeed.models import NewsItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            self.process()
        except Exception as err:
            subject = "{}".format(sys.argv[1])
            message = "{}".format(err)
            mail_admins(subject, message)
            raise

    def process(self):
        client = zotero.Zotero(settings.ZOTERO_GROUP_ID, 'group')
        self.stdout.write("{}: Fetching all items".format(str(timezone.now())))
        all_items = client.everything(client.items())
        for item in all_items:
            defaults = {
                # '2014-10-30T18:45:14.000Z'
                'date_added': iso8601.parse_date(item['data']['dateAdded']),
                'itemType': item['data']['itemType'],
                'version': item['version'],
                'meta': item['meta'],
                'data': item['data'],
                'library': item['library'],
                'links': item['links'],
            }
            news_item, created = NewsItem.objects.get_or_create(key=item['key'], defaults=defaults)
            if created:
                self.stdout.write("{}: Created {} version {}".format(
                    str(timezone.now()), news_item.key, news_item.version))
            if not created and item['version'] != news_item.version:
                old_version = news_item.version
                updated = False
                for field, value in defaults.items():
                    if getattr(news_item, field) != value:
                        setattr(news_item, field, value)
                        updated = True
                if updated:
                    self.stdout.write("{}: Updated {} from version {} to {}".format(
                        str(timezone.now()), news_item.key, old_version, item['version']))
                    news_item.save()
        remote_keys = set([item['key'] for item in all_items])
        local_keys = set(NewsItem.objects.values_list('key', flat=True))
        keys_to_be_deleted = local_keys - remote_keys
        for key in keys_to_be_deleted:
            news_item = NewsItem.objects.get(key=key)
            self.stdout.write("{}: Deleted {} which is no longer in Zotero".format(str(timezone.now()), key))
            news_item.delete()
