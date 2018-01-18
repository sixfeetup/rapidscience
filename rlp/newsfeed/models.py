from jsonfield_compat.fields import JSONField
from django.db import models

from cms.models.pluginmodel import CMSPlugin

NEWS_ITEM_EXCLUDE_TYPES = ['attachment', 'note']


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(itemType__in=NEWS_ITEM_EXCLUDE_TYPES)


class NewsItem(models.Model):
    key = models.CharField(max_length=100, db_index=True, unique=True)
    itemType = models.CharField(max_length=100, db_index=True)
    version = models.IntegerField()
    date_added = models.DateTimeField(db_index=True)
    meta = JSONField()
    data = JSONField()
    library = JSONField()
    links = JSONField()

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        if self.itemType in NEWS_ITEM_EXCLUDE_TYPES:
            return "<{}: {}>".format(self.itemType, self.key)
        return "<{}>: {} {}".format(self.itemType, self.key, self.data['title'])

    @property
    def title(self):
        try:
            return self.data['title']
        except KeyError:
            return str(self)

    def _get_creators(self, creator_type):
        creators = []
        if 'creators' in self.data:
            for creator in [c for c in self.data['creators'] if c['creatorType'] == creator_type]:
                last_name = ''
                initials = ''
                if 'lastName' in creator and creator['lastName']:
                    last_name = creator['lastName']

                if 'firstName' in creator and creator['firstName']:
                    try:
                        initials = [s[0] for s in creator['firstName'].split(' ')]
                    except Exception:
                        # If we can't parse the first initial out of the first name, just show the full first name
                        # The data sometimes provides things like 'BT  - Progress in Brain' as a first name.
                        initials = creator['firstName']

                if 'name' in creator and creator['name']:
                    try:
                        last_name, initials = creator['name'].split()
                    except ValueError:
                        last_name = creator['name']
                    initials = list(initials)
                name = ' '.join([last_name + ','] + initials)
                if creator_type == 'editor':
                    name = "{} (ed)".format(name)
                creators.append(name)
        return ', '.join(creators)

    @property
    def authors(self):
        return self._get_creators('author')

    @property
    def editors(self):
        return self._get_creators('editor')

    @property
    def pmid(self):
        if 'extra' in self.data and self.data['extra'][:5] == 'PMID:':
            return self.data['extra'][6:]

    @property
    def url(self):
        if 'url' in self.data and self.data['url']:
            return self.data['url']
        elif self.pmid is not None:
            return "http://www.ncbi.nlm.nih.gov/pubmed/{}".format(self.pmid)
        try:
            return self.links['alternate']['href']
        except KeyError:
            pass
