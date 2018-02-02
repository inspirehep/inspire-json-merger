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

import pytest

from utils import validate_subschema

from inspire_json_merger.api import (
    get_acquisition_source,
    get_configuration,
    get_head_source,
)
from inspire_json_merger.config import (
    ArxivOnArxivOperations,
    ArxivOnPublisherOperations,
    PublisherOnArxivOperations,
    PublisherOnPublisherOperations,
    ManualMergeOperations
)


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
        'acquisition_source': {'source': 'arxiv'}
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
    assert get_head_source(rec_publication_info) is 'arxiv'


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
    assert get_head_source(rec_dois) is 'publisher'


def test_get_head_source_arxiv_dois(rec_dois):
    # record has dois with arxiv source and arxiv_eprint, no publication_info
    rec_dois.get('dois')[0]['source'] = 'arxiv'
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'arxiv'


def test_get_head_source_arxiv_dois_no_eprint(rec_dois):
    # record has dois without arxiv source but no arxiv_eprint, no publication_info
    del rec_dois['arxiv_eprints']
    validate_subschema(rec_dois)
    assert get_head_source(rec_dois) == 'publisher'


def test_get_head_source_arxiv_dois_and_freetext(rec_dois, rec_publication_info):
    rec = rec_dois
    rec.get('dois')[0]['source'] = 'arxiv'
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
    rec.get('dois')[0]['source'] = 'arxiv'
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
    rec.get('dois')[0]['source'] = 'arxiv'
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
