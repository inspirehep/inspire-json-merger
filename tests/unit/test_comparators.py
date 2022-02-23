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

from inspire_schemas.api import load_schema, validate

from json_merger.config import UnifierOps

from inspire_json_merger.comparators import IDNormalizer
from inspire_json_merger.api import merge
from inspire_json_merger.config import ArxivOnArxivOperations

from utils import assert_ordered_conflicts

ArxivOnArxivOperations.list_merge_ops['references'] = UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST
ArxivOnArxivOperations.list_merge_ops['publication_info'] = UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST


def add_arxiv_source(*json_obj):
    # This function add a source object to the given json file list
    for obj in json_obj:
        source = {
            'acquisition_source': {
                'source': 'arxiv'
            }
        }
        obj.update(source)
    return json_obj if len(json_obj) > 1 else json_obj[0]


def validate_subschema(obj):
    if len(obj.keys()) > 1:
        del obj['acquisition_source']
    schema = load_schema('hep')
    key = list(obj.keys())[0]  # python 3 compatibility
    sub_schema = schema['properties'].get(key)
    assert validate(obj.get(key), sub_schema) is None


def test_id_normalizer():
    normalizer = IDNormalizer('INSPIRE BAI')
    author = {
        'full_name': 'Smith, John',
        'ids': [
            {
                'schema': 'INSPIRE ID',
                'value': '123456',
            },
            {
                'schema': 'INSPIRE BAI',
                'value': 'J.Smith.1',
            },
        ],
    }

    assert normalizer(author) == 'J.Smith.1'


def test_comparing_authors_unicode_name():
    root = {}
    head = {
        'authors': [
            {'full_name': 'Ortín, Tomás'},
        ],
    }
    update = {
        'authors': [
            {'full_name': 'Ortin, Tomas'},
        ],
    }

    expected_conflict = []
    expected_merged = head

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = merge(root, head, update, head_source='arxiv')

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_comparing_publication_info():
    root = {}
    head = {
        'publication_info': [
            {
                'journal_title': 'J. Testing',
                'journal_volume': '42',
            }
        ]
    }
    update = {
        'publication_info': [
            {
                'journal_title': 'J. Testing',
                'journal_volume': '42',
                'artid': 'foo',
            }
        ]
    }

    expected_conflict = []
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = merge(root, head, update, head_source='arxiv')

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_comparing_publication_info_with_cnum():
    root = {}
    head = {
        'publication_info': [
            {
                "artid": "WEPAB127",
                "cnum": "C21-05-24.3",
                "conf_acronym": "IPAC2021",
                "year": 2021
            }
        ]
    }
    update = {
        'publication_info': [
            {
                "artid": "WEPAB127",
                "cnum": "C21-05-24.3",
                "conf_acronym": "IPAC2021",
                "conference_record": {
                    "$ref": "https://inspirehep.net/api/conferences/1853162"
                },
                "year": 2021
            }
        ]
    }

    expected_conflict = []
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = merge(root, head, update, head_source='arxiv')

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_comparing_keywords():
    root = {}
    head = {
        'keywords': [
            {
                'value': 'shielding',
                'schema': 'JACOW',
            },
            {
                'value': 'test',
                'schema': 'JACOW',
            }
        ]
    }
    update = {
        'keywords': [
            {
                'value': 'shielding',
                'schema': 'INSPIRE',
            },
            {
                'value': 'shielding',
                'schema': 'JACOW',
            }
        ]
    }

    expected_conflict = []
    expected_merged = {
        'keywords': [
            {
                'value': 'shielding',
                'schema': 'INSPIRE',
            },
            {
                'value': 'shielding',
                'schema': 'JACOW',
            },
            {
                'value': 'test',
                'schema': 'JACOW',
            },
        ]
    }

    merged, conflict = merge(root, head, update, head_source='arxiv')

    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)
