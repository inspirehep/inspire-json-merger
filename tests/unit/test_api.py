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

import json
import operator
import os
from operator import itemgetter

import pytest

from utils import validate_subschema

from inspire_json_merger.api import (
    get_acquisition_source,
    get_configuration,
    get_head_source,
    merge,
)
from inspire_json_merger.config import (
    ArxivOnArxivOperations,
    ArxivOnPublisherOperations,
    PublisherOnArxivOperations,
    PublisherOnPublisherOperations,
    ManualMergeOperations
)


def get_file(file_path):
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, file_path)
    return open(path, 'r')


def load_test_data(file_path):
    return json.load(get_file(file_path))


def test_get_acquisition_source_non_arxiv():
    rec = {
        'acquisition_source': {
            'source': 'foo'
        }
    }
    assert get_acquisition_source(rec) == 'foo'
    validate_subschema(rec)


@pytest.fixture
def rec_dois():
    return \
        {
            'dois': [
                {
                    'material': 'publication',
                    'source': 'elsevier',
                    'value': '10.3847/2041-8213/aa9110'
                }
            ],
            'arxiv_eprints': [
                {
                    'categories': [
                        'gr-qc',
                        'astro-ph.HE'
                    ],
                    'value': '1710.05832'
                }
            ]
        }


@pytest.fixture
def rec_publication_info():
    return \
        {
            'publication_info': [
                {
                    'artid': '161101',
                    'journal_record': {
                        '$ref': 'http://labs.inspirehep.net/api/journals/1214495'
                    },
                    'journal_title': 'Phys.Rev.Lett.',
                    'journal_volume': '119',
                    'pubinfo_freetext': 'Phys. Rev. Lett. 119 161101 (2017)',
                    'year': 2017
                }
            ],
            'arxiv_eprints': [
                {
                    'categories': [
                        'gr-qc',
                        'astro-ph.HE'
                    ],
                    'value': '1710.05832'
                }
            ]
        }


@pytest.fixture
def arxiv_record():
    return {
        '_collections': ['literature'],
        'document_type': ['article'],
        'titles': {'title': 'Superconductivity'},
        'arxiv_eprints': [{'value': '1710.05832'}],
        'acquisition_source': {'source': 'arXiv'}
    }


@pytest.fixture
def publisher_record():
    return {
        '_collections': ['literature'],
        'document_type': ['article'],
        'titles': {'title': 'Superconductivity'},
        'dois': [{'value': '10.1023/A:1026654312961'}],
        'acquisition_source': {'source': 'ejl'}
    }


def test_get_head_source_freetext_pub_info_with_eprint(rec_publication_info):
    # record has pubinfo_freetext and arxiv_eprints, no dois
    validate_subschema(rec_publication_info)
    assert get_head_source(rec_publication_info) == 'arxiv'


def test_get_head_source_freetext_pub_info_with_no_eprint(rec_publication_info):
    # record has pubinfo_freetext but not arxiv_eprints, no dois
    del rec_publication_info['arxiv_eprints']
    validate_subschema(rec_publication_info)
    assert get_head_source(rec_publication_info) == 'publisher'


def test_get_head_source_no_freetext_pub_info(rec_publication_info):
    # record has no pubinfo_freetext, no dois
    del rec_publication_info['publication_info'][0]['pubinfo_freetext']
    validate_subschema(rec_publication_info)
    assert get_head_source(rec_publication_info) == 'publisher'


def test_get_head_source_no_arxiv_dois(rec_dois):
    # record has dois without arxiv source, no publication_info
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_arxiv_dois(rec_dois):
    # record has dois with arxiv source and arxiv_eprint, no publication_info
    rec_dois.get('dois')[0]['source'] = 'arXiv'
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'arxiv'


def test_get_head_source_arxiv_dois_no_eprint(rec_dois):
    # record has dois without arxiv source but no arxiv_eprint, no publication_info
    del rec_dois['arxiv_eprints']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_arxiv_dois_and_freetext(rec_dois, rec_publication_info):
    rec = rec_dois
    rec.get('dois')[0]['source'] = 'arXiv'
    rec['publication_info'] = rec_publication_info['publication_info']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'arxiv'


def test_get_head_source_no_arxiv_dois_and_freetext(rec_dois, rec_publication_info):
    rec = rec_dois
    rec['publication_info'] = rec_publication_info['publication_info']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_arxiv_dois_and_no_freetext(rec_dois, rec_publication_info):
    rec = rec_dois
    rec.get('dois')[0]['source'] = 'arXiv'
    rec['publication_info'] = rec_publication_info['publication_info']
    del rec['publication_info'][0]['pubinfo_freetext']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_no_arxiv_dois_and_no_freetext(rec_dois, rec_publication_info):
    rec = rec_dois
    rec['publication_info'] = rec_publication_info['publication_info']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_arxiv_dois_and_freetext_but_no_arxiv_eprint(rec_dois, rec_publication_info):
    rec = rec_dois
    rec.get('dois')[0]['source'] = 'arXiv'
    rec['publication_info'] = rec_publication_info['publication_info']
    del rec['arxiv_eprints']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_configuration(arxiv_record, publisher_record):
    assert get_configuration(arxiv_record, arxiv_record) == ArxivOnArxivOperations
    assert get_configuration(arxiv_record, publisher_record) == PublisherOnArxivOperations
    assert get_configuration(publisher_record, arxiv_record) == ArxivOnPublisherOperations
    assert get_configuration(publisher_record, publisher_record) == PublisherOnPublisherOperations

    arxiv1 = arxiv_record
    arxiv1['control_number'] = 1

    arxiv2 = dict(arxiv_record)
    arxiv2['control_number'] = 2

    pub1 = publisher_record
    pub1['control_number'] = 3

    pub2 = dict(publisher_record)
    pub2['control_number'] = 4

    assert get_configuration(arxiv1, arxiv2) == ManualMergeOperations
    assert get_configuration(pub1, pub2) == ManualMergeOperations

    # even if both have a ``control_number`` arxiv-publisher
    # will give always the configuration ArxivOnPublisherOperations
    assert get_configuration(arxiv1, pub1) == PublisherOnArxivOperations
    assert get_configuration(pub1, arxiv1) == ArxivOnPublisherOperations

    arxiv2['control_number'] = 1  # same of the other arxiv record
    assert get_configuration(arxiv1, arxiv2) == ArxivOnArxivOperations


def test_get_configuration_without_acquisition_source(arxiv_record, publisher_record):
    arxiv1 = dict(arxiv_record)
    arxiv1['control_number'] = 1
    del arxiv1['acquisition_source']

    arxiv2 = dict(arxiv_record)
    arxiv2['control_number'] = 2
    del arxiv2['acquisition_source']

    assert get_configuration(arxiv1, arxiv2) == ManualMergeOperations

    # arxiv2 is a publisher because doesn't have acquisition source
    assert get_configuration(arxiv_record, arxiv2) == PublisherOnArxivOperations

    # first one is arxiv because has arxiv_eprint
    assert get_configuration(arxiv1, arxiv_record) == ArxivOnArxivOperations

    assert get_configuration(arxiv1, arxiv2) == ManualMergeOperations


def test_merger_handles_list_deletions():
    root = {
        'book_series': [
            {
                'title': 'IEEE Nucl.Sci.Symp.Conf.Rec.',
                'volume': '1'
            },
            {
                'title': 'CMS Web-Based Monitoring',
                'volume': '2'
            },
            {
                'title': 'Lectures in Testing',
                'volume': '3',
            },
        ]
    }
    head = {}
    update = {
        'book_series': [
            {
                'title': 'Lectures in Testing',
                'volume': '3',
            },
        ]
    }

    expected_merged = head
    expected_conflict = [
        {'path': '/book_series/0/volume', 'op': 'replace', 'value': '3', '$type': 'SET_FIELD'},
        {'path': '/book_series/0/title', 'op': 'replace', 'value': 'Lectures in Testing', '$type': 'SET_FIELD'},
        {'path': '/book_series/2', 'op': 'remove', 'value': None, '$type': 'REMOVE_FIELD'},
        {'path': '/book_series/1', 'op': 'remove', 'value': None, '$type': 'REMOVE_FIELD'}
    ]

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert sorted(conflict, key=operator.itemgetter("path")) == sorted(expected_conflict, key=operator.itemgetter("path"))


def test_merger_handles_authors_with_correct_ordering():
    root = {}
    head = {
        "authors": [
            {
                'full_name': 'Janeway, Kathryn',
                'age': 44
            },
            {
                'full_name': 'Picard, Jean-Luc',
                'age': 55
            },
            {
                "full_name": "Archer, Jonathan",
            }
        ],
    }
    update = {
        "authors": [
            {
                "full_name": "Kirk, James"
            },
            {
                'full_name': 'Janeway Kathryn, Picard Jean-Luc', 'age': 66
            },
            {
                "full_name": "Archer, Jonathan",
            }
        ],
    }

    expected_conflict = [
        {
            'path': '/authors/1',
            'op': 'replace',
            'value': {'full_name': 'Janeway Kathryn, Picard Jean-Luc', 'age': 66},
            '$type': 'SET_FIELD'
        },
        {
            'path': '/authors/2',
            'op': 'replace',
            'value': {'full_name': 'Janeway Kathryn, Picard Jean-Luc', 'age': 66},
            '$type': 'SET_FIELD'
        },
    ]
    expected_merged = {'authors': [
        {"full_name": "Kirk, James"},
        {'age': 44, 'full_name': 'Janeway, Kathryn'},
        {'age': 55, 'full_name': 'Picard, Jean-Luc'},
        {"full_name": "Archer, Jonathan"}
    ]}

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert conflict.sort(key=itemgetter('path')) == expected_conflict.sort(key=itemgetter('path'))


def test_ordering_conflicts():

    root = load_test_data("test_data/root.json")
    head = load_test_data("test_data/head.json")
    update = load_test_data("test_data/update.json")

    expected_conflicts = load_test_data("test_data/conflicts.json")
    expected_merged = load_test_data("test_data/merged.json")

    merged, conflicts = merge(root, head, update)

    assert sorted(merged) == sorted(expected_merged)
    assert conflicts.sort(key=itemgetter('path')) == expected_conflicts.sort(key=itemgetter('path'))
