# Stolen from https://raw.githubusercontent.com/edx/edx-notes-api/8e05ad10f882b7037f466c761bdf858311a4b1fc/notesserver/highlight.py
# so we can actually configure Elasticsearch's highlighting.
import os
import subprocess

from django.conf import settings

import haystack
from haystack.backends.elasticsearch_backend import (
    ElasticsearchSearchEngine as OrigElasticsearchSearchEngine,
    ElasticsearchSearchQuery as OrigElasticsearchSearchQuery,
    ElasticsearchSearchBackend as OrigElasticsearchSearchBackend)
from haystack.query import SearchQuerySet as OrigSearchQuerySet


class SearchQuerySet(OrigSearchQuerySet):
    def highlight(self, **kwargs):
        """Adds highlighting to the results."""
        clone = self._clone()
        clone.query.add_highlight(**kwargs)
        return clone


class ElasticsearchSearchQuery(OrigElasticsearchSearchQuery):
    def add_highlight(self, **kwargs):
        """Adds highlighting to the search results."""
        self.highlight = kwargs or True


class ElasticsearchSearchBackend(OrigElasticsearchSearchBackend):
    """
    Subclassed backend that lets user modify highlighting options
    """
    def build_search_kwargs(self, *args, **kwargs):
        res = super().build_search_kwargs(*args, **kwargs)
        index = haystack.connections[self.connection_alias].get_unified_index()
        content_field = index.document_field
        highlight = kwargs.get('highlight')
        if highlight:
            highlight_options = {
                'fields': {
                    content_field: {'store': 'yes'},
                },
                'pre_tags': ['<span class="highlighted">'],
                'post_tags': ['</span>'],
            }
            if isinstance(highlight, dict):
                highlight_options.update(highlight)
            res['highlight'] = highlight_options
        return res

    def _process_results(
            self, raw_results, highlight=False, result_class=None, distance_point=None, geo_sort=False
    ):
        """
        Overrides _process_results from Haystack's ElasticsearchSearchBackend to add highlighted tags to the result
        """
        result = super()._process_results(
            raw_results, highlight, result_class, distance_point, geo_sort
        )

        for i, raw_result in enumerate(raw_results.get('hits', {}).get('hits', [])):
            if 'highlight' in raw_result:
                result['results'][i].highlighted_tags = raw_result['highlight'].get('tags', '')

        return result

    def extract_file_contents(self, file_path):
        text = subprocess.check_output([
            'java',
            '-Xmx384m',
            '-Djava.awt.headless=true',
            '-jar',
            os.path.join(settings.BASE_DIR, 'bin', 'tika-app-1.13.jar'),
            '--text-main',
            file_path
        ])
        # Convert to ascii to get rid of odd characters showing up in output, split on newlines so newlines don't show
        # up in output.
        try:
            text = text.decode('unicode_escape')
        except UnicodeDecodeError:
            text = text.decode('utf8')
        text = text.encode('ascii', 'ignore')
        return ' '.join(text.decode().split())


class ElasticsearchSearchEngine(OrigElasticsearchSearchEngine):
    backend = ElasticsearchSearchBackend
    query = ElasticsearchSearchQuery

