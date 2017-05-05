import logging
import re

import requests

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from Bio import Entrez
from taggit.managers import TaggableManager
from taggit.models import Tag

from rlp.accounts.models import User
from rlp.core.models import SharedObjectMixin
from rlp.discussions.models import ThreadedComment
from rlp.projects.models import Project
from . import choices

logger = logging.getLogger(__name__)

# From http://blog.crossref.org/2015/08/doi-regular-expressions.html
DOI_RE = re.compile(r'^10.\d{4,9}/[-._;()/:A-Za-z0-9]+$')
PMID_RE = re.compile(r'^\d+$')
CROSSREF_BASE_URL = "https://api.crossref.org/works"


class Reference(SharedObjectMixin):
    title = models.CharField(max_length=500)
    pubmed_id = models.CharField(max_length=100, blank=True, db_index=True)
    doi = models.CharField(max_length=100, blank=True, db_index=True)
    source = models.CharField(max_length=25, db_index=True, choices=choices.SOURCE_CHOICES)
    authors = models.ManyToManyField(User, through='Publication')
    raw_data = JSONField()
    parsed_data = JSONField(default=dict)
    upload = models.FileField('Upload file', upload_to='references', blank=True, max_length=255)
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(blank=True, max_length=1000)
    discussions = GenericRelation(
        ThreadedComment,
        object_id_field='object_pk',
    )
    tags = TaggableManager()

    class Meta:
        verbose_name = 'Raw Reference'

    def __str__(self):
        return self.title

    def get_source_url(self):
        if self.doi:
            return "http://dx.doi.org/{}".format(self.doi)
        elif self.pubmed_id:
            return "http://www.ncbi.nlm.nih.gov/pubmed/{}".format(self.pubmed_id)
        elif 'url' in self.parsed_data and self.parsed_data['url']:
            return self.parsed_data['url']
        elif 'upload_url' in self.parsed_data and self.parsed_data['upload_url']:
            return self.parsed_data['upload_url']
        # Should be safe to assume this is a user-generated reference and that this lives under exactly one project.
        # Add the domain since this url may be used in email templates when shared.
        return 'https://{}{}'.format(
            Site.objects.get_current().domain,
            self.get_absolute_url(),
        )

    def get_absolute_url(self):
        return reverse('bibliography:reference_detail', kwargs={
            'reference_pk': self.pk,
        })

    def get_edit_url(self):
        # Don't provide an edit url for Pubmed/Crossref if there aren't any tags to add (there's nothing else to edit)
        if self.source != choices.MEMBER and not Tag.objects.count():
            return
        return reverse('bibliography:reference_edit', kwargs={
            'reference_pk': self.pk,
        })

    def get_delete_url(self):
        return reverse('bibliography:reference_delete', kwargs={
            'reference_pk': self.pk,
        })

    @property
    def display_type(self):
        return 'Reference'


class ReferenceShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_references')
    group = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    recipients = models.ManyToManyField(User, blank=True, limit_choices_to={'is_staff': False})
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250)

    @property
    def display_type(self):
        return 'Reference'


class Publication(models.Model):
    reference = models.ForeignKey(Reference)
    author = models.ForeignKey(User)

    class Meta:
        unique_together = ('reference', 'author')


def parse_orcid_data(raw_data):
    parsed_data = get_parsed_data_container()
    if 'work-external-identifiers' in raw_data and raw_data['work-external-identifiers']:
        for identifier in raw_data['work-external-identifiers']['work-external-identifier']:
            if identifier['work-external-identifier-type'] == 'DOI':
                parsed_data['doi'] = identifier['work-external-identifier-id']['value']
            elif identifier['work-external-identifier-type'] == 'ISSN':
                parsed_data['issn'] = identifier['work-external-identifier-id']['value']
            elif identifier['work-external-identifier-type'] == 'ISBN':
                parsed_data['isbn'] = identifier['work-external-identifier-id']['value']
            elif identifier['work-external-identifier-type'] == 'PMID':
                parsed_data['pubmed_id'] = identifier['work-external-identifier-id']['value']

    parsed_data['title'] = raw_data['work-title']['title']['value']

    if 'url' in raw_data and raw_data['url']:
        parsed_data['url'] = raw_data['url']['value']

    if 'publication-date' in raw_data and raw_data['publication-date']:
        date_parts = []
        if raw_data['publication-date']['year']:
            date_parts.append(raw_data['publication-date']['year']['value'])
        if raw_data['publication-date']['month']:
            date_parts.append(raw_data['publication-date']['month']['value'])
        if raw_data['publication-date']['day']:
            date_parts.append(raw_data['publication-date']['day']['value'])
        parsed_data['publication_date'] = '-'.join([str(d) for d in date_parts])

    if 'journal-title' in raw_data and raw_data['journal-title']:
        parsed_data['journal_title'] = raw_data['journal-title']['value']

    if 'short-description' in raw_data and raw_data['short-description']:
        parsed_data['abstract'] = raw_data['short-description']

    author_names = []
    if 'work-contributors' in raw_data and raw_data['work-contributors']:
        for author in raw_data['work-contributors']['contributor']:
            if author['credit-name']:
                author_names.append(author['credit-name']['value'])
    parsed_data['authors'] = ', '.join(author_names)
    return parsed_data


def get_or_create_reference_from_orcid(result):
    # We do a get_or_create by DOI here because this item may have been created by a Pubmed entry and we don't want
    # duplicates. We do not update the record because, ugh, who wants to get into that.
    parsed_data = parse_orcid_data(result)
    # First, check if this reference already exists from Pubmed
    if parsed_data['doi']:
        ref, created = Reference.objects.get_or_create(
            doi=parsed_data['doi'],
            defaults={
                'source': choices.ORCID,
                'title': parsed_data['title'],
                'raw_data': result,
                'parsed_data': parsed_data,
            }
        )
    elif parsed_data['pubmed_id']:
        ref, created = Reference.objects.get_or_create(
            pubmed_id=parsed_data['pubmed_id'],
            defaults={
                'source': choices.ORCID,
                'title': parsed_data['title'],
                'raw_data': result,
                'parsed_data': parsed_data,
            }
        )
    else:
        # TODO: figure out some sort of unique identifier for ORCID results
        # We can't look up by title since these can be generic ('Introduction' is a real-world example).
        # Looking up by JSON is very finicky and will lead to duplicates if the underlying record changes.
        try:
            ref, created = Reference.objects.get_or_create(
                raw_data=result,
                defaults={
                    'title': parsed_data['title'],
                    'source': choices.ORCID,
                    'parsed_data': parsed_data,
                }
            )
        except Reference.MultipleObjectsReturned:
            return None, False
    return ref, created


def fetch_publications_for_user(user):
    if not user.orcid:
        return
    token_headers = {
        'Accept': 'application/json',
    }
    token_data = {
        'client_id': settings.ORCID_CLIENT_ID,
        'client_secret': settings.ORCID_SECRET_KEY,
        'scope': '/read-public',
        'grant_type': 'client_credentials',
    }
    token_response = requests.post('https://pub.orcid.org/oauth/token', data=token_data, headers=token_headers)
    access_token = token_response.json()['access_token']
    headers = {
        'Content-Type': 'application/orcid+json',
        'Authorization': 'Bearer {}'.format(access_token),
    }
    r = requests.get("https://pub.orcid.org/v1.2/{}/orcid-works/".format(user.orcid), headers=headers)
    # Not all ORCID's will be valid, so we can't expect results
    try:
        results = r.json()['orcid-profile']['orcid-activities']['orcid-works']['orcid-work']
    except (KeyError, TypeError):
        return
    for result in results:
        reference, created = get_or_create_reference_from_orcid(result)
        if reference:
            Publication.objects.get_or_create(reference=reference, author=user)


def get_parsed_data_container():
    return dict([
        ('doi', ''),
        ('isbn', ''),
        ('issn', ''),
        ('pubmed_id', ''),
        ('abstract', ''),
        ('authors', ''),
        ('container_title', ''),
        ('editors', ''),
        ('journal_title', ''),
        ('journal_issue', ''),
        ('journal_volume', ''),
        ('page_range', ''),
        ('pages', ''),
        ('publication_date', ''),
        ('publisher', ''),
        ('retrieval_date', ''),
        ('title', ''),
        ('upload_url', ''),
        ('url', ''),
    ])


def parse_pubmed_data(raw_data):
    parsed_data = get_parsed_data_container()
    for key in ['PubmedData', 'PubmedBookData']:
        if key not in raw_data:
            continue
        for raw_id in raw_data[key]['ArticleIdList']:
            if raw_id.attributes['IdType'] == 'doi':
                parsed_data['doi'] = str(raw_id)
            elif raw_id.attributes['IdType'] == 'pubmed':
                parsed_data['pubmed_id'] = str(raw_id)
    if 'BookDocument' in raw_data:
        try:
            parsed_data['abstract'] = raw_data['BookDocument']['Abstract']['AbstractText'][0]
        except (KeyError, IndexError):
            pass
        parsed_data['title'] = str(raw_data['BookDocument']['Book']['BookTitle'])
        for author_list in raw_data['BookDocument']['Book']['AuthorList']:
            if author_list.attributes['Type'] != 'authors':
                continue
            parsed_data['authors'] = ', '.join([' '.join([a['LastName'], a['Initials']]) for a in author_list])
        parsed_data['publication_date'] = raw_data['BookDocument']['Book']['PubDate']['Year']
        parsed_data['isbn'] = ', '.join(raw_data['BookDocument']['Book']['Isbn'])
    elif 'MedlineCitation' in raw_data:
        try:
            parsed_data['abstract'] = raw_data['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        except (KeyError, IndexError):
            pass
        parsed_data['title'] = raw_data['MedlineCitation']['Article']['ArticleTitle']
        parsed_data['authors'] = ', '.join(
            ' '.join([a['LastName'], a['Initials']]) for a in raw_data['MedlineCitation']['Article']['AuthorList']
            if 'LastName' in a  # There may be a 'CollectiveName' in the list, omit for now
        )
        parsed_data['journal_title'] = raw_data['MedlineCitation']['Article']['Journal'].get('Title', '')
        pub_date = raw_data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']
        if 'Day' in pub_date and 'Month' in pub_date:
            parsed_data['publication_date'] = "{} {} {}".format(pub_date['Day'], pub_date['Month'], pub_date['Year'])
        elif 'MedlineDate' in pub_date:
            parsed_data['publication_date'] = pub_date['MedlineDate']
        elif 'Year' in pub_date:
            parsed_data['publication_date'] = pub_date['Year']
        parsed_data['journal_issue'] = raw_data['MedlineCitation']['Article']['Journal']['JournalIssue'].get('Issue', '')
        parsed_data['journal_volume'] = raw_data['MedlineCitation']['Article']['Journal']['JournalIssue'].get('Volume', '')
        parsed_data['issn'] = raw_data['MedlineCitation']['Article']['Journal']['ISSN']
    else:
        logger.error('Unknown Pubmed result type: {}'.format(', '.join(raw_data.keys())))
        return None
    return parsed_data


def parse_crossref_data(raw_data):
    parsed_data = get_parsed_data_container()
    parsed_data['doi'] = raw_data['DOI']
    parsed_data['title'] = ' '.join(raw_data['title'])
    # Apparently some items don't have authors. Causa sui FTW!!!
    try:
        parsed_data['authors'] = ', '.join(' '.join([a['family'], a['given'][0]]) for a in raw_data['author'])
    except KeyError:
        pass
    parsed_data['publisher'] = raw_data['publisher']
    if 'published-online' in raw_data and raw_data['published-online']:
        date_parts = raw_data['published-online']['date-parts'][0]
        parsed_data['publication_date'] = '-'.join([str(d) for d in date_parts])
    elif 'published-print' in raw_data and raw_data['published-print']:
        date_parts = raw_data['published-print']['date-parts'][0]
        parsed_data['publication_date'] = '-'.join([str(d) for d in date_parts])
    try:
        parsed_data['container_title'] = raw_data['container-title'][0]
    except (KeyError, IndexError):
        pass
    return parsed_data


def parse_user_submission(cleaned_data):
    parsed_data = get_parsed_data_container()
    for key in parsed_data:
        parsed_data[key] = cleaned_data.get(key, '')
    return parsed_data


def get_or_create_reference_from_pubmed(result):
    # Do a get_or_create by PMID
    parsed_data = parse_pubmed_data(result)
    if not parsed_data:
        return None, False
    # First, check if this reference already exists from Pubmed
    if parsed_data['doi']:
        try:
            ref = Reference.objects.get(doi=parsed_data['doi'])
            return ref, False
        except Reference.DoesNotExist:
            pass
    ref, created = Reference.objects.get_or_create(
        pubmed_id=parsed_data['pubmed_id'],
        defaults={
            'source': choices.PUBMED,
            'doi': parsed_data['doi'],
            'title': parsed_data['title'],
            'raw_data': result,
            'parsed_data': parsed_data,
        }
    )
    return ref, created


def get_or_create_reference_from_crossref(result):
    # We do a get_or_create by DOI here because this item may have been created by a Pubmed entry and we don't want
    # duplicates. We do not update the record because, ugh, who wants to get into that.
    parsed_data = parse_crossref_data(result)
    ref, created = Reference.objects.get_or_create(
        doi=parsed_data['doi'],
        defaults={
            'source': choices.CROSSREF,
            'title': parsed_data['title'],
            'raw_data': result,
            'parsed_data': parsed_data,
        }
    )
    return ref, created


def fetch_crossref_by_doi(doi):
    doi_url = "{}/{}".format(CROSSREF_BASE_URL, doi)
    r = requests.get(doi_url)
    return r.json()['message']


def fetch_crossref_by_query(query=None, orcid=None):
    filters = ['type:{}'.format(t) for t in choices.CROSSREF_TYPES]
    if orcid:
        filters.append('orcid:{}'.format(orcid))
    params = {
        'filter': ','.join(filters),
        'rows': 100,
    }
    if query:
        params['query'] = query
    results = requests.get(
        CROSSREF_BASE_URL,
        params=params
    )
    return results.json()['message']['items']


def get_or_create_reference(query):
    # Remove any leading/trailing whitespace
    query = query.strip()
    # check the db first and bail if we have a match
    references = Reference.objects.filter(
        Q(pubmed_id__icontains=query) | Q(doi__icontains=query))
    if references:
        return references
    # Otherwise, check against the services, but only if the query matches regex
    if DOI_RE.match(query):
        # fetch from crossref
        result = fetch_crossref_by_doi(query)
        reference, created = get_or_create_reference_from_crossref(result)
        return [reference]
    elif PMID_RE.match(query):
        Entrez.email = settings.PUBMED_EMAIL
        results = Entrez.read(
            Entrez.efetch(db='pubmed', retmode='xml', id=query)
        )
        references = []
        for result in results:
            reference, created = get_or_create_reference_from_pubmed(result)
            references.append(reference)
        if references:
            return references
    else:
        results = fetch_crossref_by_query(query=query)
        references = []
        for result in results:
            reference, created = get_or_create_reference_from_crossref(result)
            references.append(reference)
        if references:
            return references
    return Reference.objects.filter(Q(pubmed_id__icontains=query) | Q(doi__icontains=query) | Q(title__icontains=query))

