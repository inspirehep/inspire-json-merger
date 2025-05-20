# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspire_json_merger.pre_filters import (
    clean_root_for_acquisition_source,
    filter_curated_references,
    filter_documents_same_source,
    filter_figures_same_source,
    filter_publisher_references,
    remove_root,
    update_material,
)
from inspire_json_merger.utils import filter_records


def test_filter_documents_same_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'new_file.pdf',
                'url': '/files/5678-5678-5678-5678/new_file.pdf',
            },
        ],
    }
    expected_head = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected


def test_filter_documents_same_source_multiple_sources_in_update():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, head, update

    assert result == expected


def test_filter_documents_remove_head_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }
    expected_head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected


def test_filter_documents_same_source_is_case_insensitive_on_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arxiv',
                'key': 'new_file.pdf',
                'url': '/files/5678-5678-5678-5678/new_file.pdf',
            },
        ],
    }
    expected_head = {
        'documents': [
            {
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected


def test_filter_curated_references_takes_update_if_not_curated():
    root = {}
    head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_head = {}
    expected_update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_curated_references])
    expected = root, expected_head, expected_update

    assert result == expected


def test_filter_curated_references_keeps_head_if_legacy_curated():
    root = {}
    head = {
        'references': [
            {
                'legacy_curated': True,
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_head = {
        'references': [
            {
                'legacy_curated': True,
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    expected_update = {}

    result = filter_records(root, head, update, filters=[filter_curated_references])
    expected = root, expected_head, expected_update

    assert result == expected


def test_filter_curated_references_keeps_update_if_head_almost_equal_to_root():
    root = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
                'curated_relation': False,
            },
        ],
    }
    head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                    'misc': ['foo'],
                    'authors': ['Smith, J.'],
                },
                'raw_refs': [
                    {
                        'source': 'arXiv',
                        'schema': 'text',
                        'value': 'foo 1810.12345',
                    },
                ],
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_root = {}
    expected_head = {}
    expected_update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_curated_references])
    expected = expected_root, expected_head, expected_update

    assert result == expected


def test_filter_curated_references_keeps_head_if_almost_equal_to_root_with_curated():
    root = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
                'curated_relation': True,
            },
        ],
    }
    head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                    'misc': ['foo'],
                },
                'raw_refs': [
                    {
                        'source': 'arXiv',
                        'schema': 'text',
                        'value': 'foo 1810.12345',
                    },
                ],
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_root = {}
    expected_head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                    'misc': ['foo'],
                },
                'raw_refs': [
                    {
                        'source': 'arXiv',
                        'schema': 'text',
                        'value': 'foo 1810.12345',
                    },
                ],
            },
        ],
    }
    expected_update = {}

    result = filter_records(root, head, update, filters=[filter_curated_references])
    expected = expected_root, expected_head, expected_update

    assert result == expected


def test_filter_curated_references_keeps_head_if_differs_from_root():
    root = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                    'dois': ['10.1234/5678'],
                },
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_root = {}
    expected_head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                    'dois': ['10.1234/5678'],
                },
            },
        ],
    }
    expected_update = {}

    result = filter_records(root, head, update, filters=[filter_curated_references])
    expected = expected_root, expected_head, expected_update

    assert result == expected


def test_filter_publisher_references_keeps_head():
    root = {}
    head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_head = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.12345',
                },
            },
        ],
    }
    expected_update = {}

    result = filter_records(root, head, update, filters=[filter_publisher_references])
    expected = root, expected_head, expected_update

    assert result == expected


def test_filter_publisher_references_keeps_update_if_no_refs_in_head():
    root = {}
    head = {}
    update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }
    expected_update = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': '1810.56789',
                },
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_publisher_references])
    expected = root, head, expected_update

    assert result == expected


def test_filter_missing_figures_on_update_are_properly_handled():
    fig_1 = {
        'caption': 'CC',
        'key': 'w0_bflow.png',
        'label': 'fig:bflow',
        'material': 'preprint',
        'source': 'arxiv',
        'url': '/api/files/8e2b4d59-6870-4517-8580-35822bf12edb/w0_bflow.png',
    }
    fig_2 = {
        'caption': 'CC2',
        'key': 'w1_bflow.png',
        'label': 'fig2:bflow',
        'material': 'preprint',
        'source': 'other',
        'url': '/api/files/8e2b4d59-6870-4517-8888-35822bf12edb/w1_bflow.png',
    }
    fig_3 = {
        'caption': 'CC',
        'key': '627d2caea8059d8875281ebed455a714',
        'label': 'fig:bflow',
        'material': 'preprint',
        'source': 'arxiv',
        'url': '/api/files/8e2b4d59-6870-4517-8580-35822bf12edb/w0_bflow.png',
    }
    root = {"figures": [fig_1, fig_2]}
    head = {"figures": [fig_2, fig_3]}

    update = {'acquisition_source': {'source': 'arXiv'}}

    expected_root = {"figures": [fig_2]}
    expected_head = {"figures": [fig_2]}
    expected_update = update

    new_root, new_head, new_update = filter_records(
        root, head, update, filters=[filter_figures_same_source]
    )
    assert new_root == expected_root
    assert new_head == expected_head
    assert new_update == expected_update


def test_acquisition_source_is_removed_from_root():
    root = {
        "acquisition_source": {"source": "desy"},
        "references": [
            {
                "reference": {
                    "arxiv_eprint": "1810.12345",
                },
            },
        ],
    }

    head = {
        "acquisition_source": {"source": "desy"},
        "references": [
            {
                "reference": {
                    "arxiv_eprint": "1810.12345",
                },
            },
        ],
    }

    update = {
        "acquisition_source": {"source": "desy"},
        "references": [
            {
                "reference": {
                    "arxiv_eprint": "1810.12345",
                },
            },
        ],
    }

    new_root, new_head, new_update = filter_records(
        root, head, update, filters=[clean_root_for_acquisition_source]
    )

    assert not new_root.get("acquisition_source")


def test_update_material():
    update = {
        "dois": [{"value": "10.2172/1827837"}],
        "documents": [
            {
                "key": "999",
                "url": "https://test.net/999",
                "filename": "fermilab-slides-21-053-td.pdf",
                "fulltext": True,
            },
        ],
        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
        "license": [
            {
                "url": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
                "license": "arXiv nonexclusive-distrib 1.0",
            }
        ],
        "copyright": [
            {
                "year": 2021,
                "holder": "Elsevier B.V.",
                "material": "publication",
                "statement": "© 2021 Elsevier B.V. All rights reserved.",
            }
        ],
        "figures": [
            {
                "key": "999",
                "url": "https://inspirehep.net/999",
                "label": "fig1",
                "source": "arxiv",
            }
        ],
    }

    root, head, update = filter_records({}, {}, update, filters=[update_material])

    assert 'material' in update['dois'][0]
    assert 'material' in update['documents'][0]
    assert 'material' in update['publication_info'][0]
    assert 'material' in update['publication_info'][1]
    assert 'material' in update['license'][0]
    assert 'material' in update['copyright'][0]
    assert 'material' in update['figures'][0]


def test_update_material_when_erratum_in_dois_material():
    update = {
        "dois": [{"value": "10.2172/1827837", 'material': 'erratum'}],
        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
    }

    root, head, update = filter_records({}, {}, update, filters=[update_material])

    assert root == {}
    assert head == {}

    assert 'material' in update['dois'][0]
    assert 'material' not in update['publication_info'][0]
    assert 'material' not in update['publication_info'][1]


def test_update_material_when_erratum_no_dois_material():
    update = {

        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
    }

    root, head, update = filter_records({}, {}, update, filters=[update_material])

    assert root == {}
    assert head == {}

    assert 'dois' not in update


def test_remove_root():
    root = {
        "dois": [{"value": "10.2172/1827837", 'material': 'erratum'}],
        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
    }
    head = {
        "dois": [{"value": "10.2172/1827837", 'material': 'erratum'}],
        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
    }
    update = {
        "dois": [{"value": "10.2172/1827837", 'material': 'erratum'}],
        "publication_info": [
            {
                "cnum": "C21-07-19.3",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1919279"
                },
            },
            {
                "year": 2020,
                "artid": "032",
                "page_start": "032",
                "journal_title": "JHEP",
                "journal_volume": "11",
            },
        ],
    }
    root, head, update = filter_records(root, head, update, filters=[remove_root])

    assert root == {}
    assert head == head
    assert root == root
