PUBMED = 'pubmed'
CROSSREF = 'crossref'
MEMBER = 'member'
ORCID = 'orcid'
SOURCE_CHOICES = [
    [PUBMED, 'PubMed'],
    [CROSSREF, 'CrossRef'],
    [MEMBER, 'Uploaded by member'],
    [ORCID, 'ORCID API']
]

JOURNAL_ARTICLE = 'journal-article'
BOOK = 'book'
BOOK_SECTION = 'book-section'

CROSSREF_TYPES = [
    BOOK,
    'book-chapter',
    'book-part',
    BOOK_SECTION,
    'book-series',
    'book-set',
    'book-track',
    'component',
    'dataset',
    'dissertation',
    'edited-book',
    # 'journal',
    JOURNAL_ARTICLE,
    # 'journal-issue',
    'journal-volume',
    'monograph',
    'other',
    'proceedings',
    'proceedings-article',
    'reference-book',
    'reference-entry',
    'report',
    'report-series',
    'standard',
    'standard-series'
]
