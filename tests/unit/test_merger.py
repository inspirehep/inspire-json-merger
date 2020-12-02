from __future__ import absolute_import, division, print_function

import pytest
from operator import itemgetter

from mock import patch

from inspire_json_merger.api import merge

from utils import assert_ordered_conflicts, validate_subschema

from inspire_json_merger.config import (
    PublisherOnPublisherOperations,
    PublisherOnArxivOperations,
    ArxivOnArxivOperations,
    ArxivOnPublisherOperations,
)


@patch(
    "inspire_json_merger.api.get_configuration",
    return_value=PublisherOnPublisherOperations,
)
def test_merging_same_documents_publisher_on_publisher(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
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


@patch(
    "inspire_json_merger.api.get_configuration", return_value=PublisherOnArxivOperations
)
def test_merging_same_documents_publisher_on_arxiv(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
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


@patch("inspire_json_merger.api.get_configuration", return_value=ArxivOnArxivOperations)
def test_merging_same_documents_arxiv_on_arxiv(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
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


@patch(
    "inspire_json_merger.api.get_configuration", return_value=ArxivOnPublisherOperations
)
def test_merging_same_documents_arxiv_on_publisher(fake_get_config):
    root = {
        "documents": [
            {
                "key": "pdf1.pdf",
                "description": "paper",
                "source": "arXiv",
                "fulltext": True,
                "url": "http://example.com/files/1234-1234-1234-1234/pdf1.pdf",
            },
            {
                "key": "pdf.tex",
                "description": "latex version",
                "source": "arXiv",
                "url": "http://example.com/files/1234-1234-1234-1234/pdf.tex",
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


def test_real_record_merge_regression_1_authors_mismatch_on_update():
    root = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [
            {"full_name": "Elliott"},
            {"full_name": "Chris"},
            {"full_name": "Gwilliam"},
            {"full_name": "Owen"},
        ],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }

    head = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [
            {
                "affiliations": [
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/945696"
                        },
                        "value": "UMass Amherst",
                    },
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/1272963"
                        },
                        "value": "UMASS, Amherst, Dept. Math. Stat.",
                    },
                ],
                "emails": ["celliott@math.umass.edu"],
                "full_name": "Elliott",
                "ids": [{"schema": "INSPIRE BAI", "value": "Elliott.1"}],
                "signature_block": "ELAT",
                "uuid": "65aa01c7-99ec-4c35-ac6b-bbc667a4343e",
            },
            {
                "full_name": "Chris",
                "ids": [{"schema": "INSPIRE BAI", "value": "Chris.1"}],
                "signature_block": "CHR",
                "uuid": "36b3a255-f8f2-46a6-bfae-9e9d00335434",
            },
            {
                "affiliations": [
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/945696"
                        },
                        "value": "UMass Amherst",
                    },
                    {
                        "record": {
                            "$ref": "https://inspirehep.net/api/institutions/1272963"
                        },
                        "value": "UMASS, Amherst, Dept. Math. Stat.",
                    },
                ],
                "emails": ["gwilliam@math.umass.edu"],
                "full_name": "Gwilliam",
                "ids": [{"schema": "INSPIRE BAI", "value": "Gwilliam.1"}],
                "signature_block": "GWALAN",
                "uuid": "66f5722f-e649-4438-a7f5-d01247371f22",
            },
            {
                "full_name": "Owen",
                "ids": [{"schema": "INSPIRE BAI", "value": "Owen.1"}],
                "signature_block": "OWAN",
                "uuid": "27de5ee5-d21a-47b2-b22c-fd44231128f9",
            },
        ],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }

    update = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [{"full_name": "Elliott, Chris"}, {"full_name": "Gwilliam, Owen"}],
        "titles": [
            {
                "source": "arXiv",
                "title": "Spontaneous symmetry breaking: a view from derived "
                "geometry",
            }
        ],
    }
    expected_merged = dict(head)

    expected_conflicts = [
        {
            "path": "/authors/3",
            "op": "replace",
            "value": {"full_name": "Gwilliam, Owen"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/2",
            "op": "replace",
            "value": {"full_name": "Gwilliam, Owen"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/0",
            "op": "replace",
            "value": {"full_name": "Elliott, Chris"},
            "$type": "SET_FIELD",
        },
        {
            "path": "/authors/1",
            "op": "replace",
            "value": {"full_name": "Elliott, Chris"},
            "$type": "SET_FIELD",
        },
    ]

    merged, conflict = merge(root, head, update)
    assert merged == expected_merged
    assert sorted(conflict, key=itemgetter("path")) == sorted(
        expected_conflicts, key=itemgetter("path")
    )


@pytest.mark.parametrize(
    "root, head, update, expected_conflicts, expected_merge",
    [
        (
            {},
            {"titles": [{"source": 1, "title": "Title 1"}, {"source": 2, "title": "Title 2"}]},
            {"titles": [{"source": 3, "title": "Title 3"}]},
            [{'path': '/titles/0', 'op': 'add', 'value': {'title': 'Title 3', 'source': 3}, '$type': 'INSERT'}],
            {'titles': [{'source': 1, 'title': 'Title 1'}, {'source': 2, 'title': 'Title 2'}]}
        ),
        (
            {},
            {"titles": [{"source": 1, "title": "Title 1"}, {"source": 1, "title": "Title 3"}]},
            {"titles": [{"source": 1, "title": "Title 3"}]},
            [],
            {'titles': [{'source': 1, 'title': 'Title 1'}, {'source': 1, 'title': 'Title 3'}]},
        ),
        (
            {"titles": [{"source": 1, "title": "Title 1"}]},
            {"titles": [{"source": 1, "title": "Title 1"}, {"source": 1, "title": "Title 3"}]},
            {"titles": [{"source": 1, "title": "Title 2"}]},
            [{'path': '/titles/0', 'op': 'add', 'value': {'title': 'Title 2', 'source': 1}, '$type': 'INSERT'}],
            {'titles': [{'source': 1, 'title': 'Title 1'}, {'source': 1, 'title': 'Title 3'}]}
        ),
        (
            {"titles": [{"source": 1, "title": "Title 1"}, {"source": 1, "title": "Title 2"}]},
            {"titles": [{"source": 1, "title": "Title 1"}, {"source": 1, "title": "Title 2"}]},
            {"titles": [{"source": 1, "title": "Title 3"}]},
            [{'path': '/titles/0', 'op': 'add', 'value': {'title': 'Title 3', 'source': 1}, '$type': 'INSERT'}],
            {'titles': [{'source': 1, 'title': 'Title 1'}, {'source': 1, 'title': 'Title 2'}]}
        ),
        (
            {"titles": [{"source": 1, "title": "Title 1"}]},
            {"titles": [{"source": 1, "title": "Title 2"}]},
            {"titles": [{"source": 1, "title": "Title 21"}]},
            [{'path': '/titles/0', 'op': 'add', 'value': {'title': 'Title 21', 'source': 1}, '$type': 'INSERT'}],
            {'titles': [{'source': 1, 'title': 'Title 2'}]}
        )

    ]
)
def test_titles_change(root, update, head, expected_conflicts, expected_merge):
    merged, conflict = merge(root, head, update)

    assert conflict == expected_conflicts
    assert merged == expected_merge
