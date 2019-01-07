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

from inspire_json_merger.utils import filter_records
from inspire_json_merger.pre_filters import (filter_documents_same_source,
                                             filter_curated_references,
                                             filter_publisher_references)


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
                },
                'raw_refs': [
                    {
                        'source': 'arXiv',
                        'schema': 'text',
                        'value': 'foo 1810.12345',
                    },
                ]
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
