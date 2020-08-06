from __future__ import absolute_import, division, print_function

from mock import patch

from inspire_json_merger.api import merge

from utils import assert_ordered_conflicts, validate_subschema

from inspire_json_merger.config import PublisherOnPublisherOperations, \
    PublisherOnArxivOperations, ArxivOnArxivOperations, \
    ArxivOnPublisherOperations


@patch('inspire_json_merger.api.get_configuration', return_value=PublisherOnPublisherOperations)
def test_merging_same_documents_publisher_on_publisher(fake_get_config):
    root = {
        'documents': [
            {
                'key': 'pdf1.pdf',
                'description': 'paper',
                'source': 'arXiv',
                'fulltext': True,
                'url': '/files/1234-1234-1234-1234/pdf1.pdf',
            },
            {
                'key': 'pdf.tex',
                'description': 'latex version',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/pdf.tex',
            },
        ]
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch('inspire_json_merger.api.get_configuration', return_value=PublisherOnArxivOperations)
def test_merging_same_documents_publisher_on_arxiv(fake_get_config):
    root = {
        'documents': [
            {
                'key': 'pdf1.pdf',
                'description': 'paper',
                'source': 'arXiv',
                'fulltext': True,
                'url': '/files/1234-1234-1234-1234/pdf1.pdf',
            },
            {
                'key': 'pdf.tex',
                'description': 'latex version',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/pdf.tex',
            },
        ]
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch('inspire_json_merger.api.get_configuration', return_value=ArxivOnArxivOperations)
def test_merging_same_documents_arxiv_on_arxiv(fake_get_config):
    root = {
        'documents': [
            {
                'key': 'pdf1.pdf',
                'description': 'paper',
                'source': 'arXiv',
                'fulltext': True,
                'url': '/files/1234-1234-1234-1234/pdf1.pdf',
            },
            {
                'key': 'pdf.tex',
                'description': 'latex version',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/pdf.tex',
            },
        ]
    }
    head = root
    update = root
    expected_merged = head
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


@patch('inspire_json_merger.api.get_configuration', return_value=ArxivOnPublisherOperations)
def test_merging_same_documents_arxiv_on_publisher(fake_get_config):
    root = {
        'documents': [
            {
                'key': 'pdf1.pdf',
                'description': 'paper',
                'source': 'arXiv',
                'fulltext': True,
                'url': '/files/1234-1234-1234-1234/pdf1.pdf',
            },
            {
                'key': 'pdf.tex',
                'description': 'latex version',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/pdf.tex',
            },
        ],
    }
    head = root
    update = root
    expected_merged = update
    expected_conflict = []
    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)
