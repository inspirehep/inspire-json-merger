# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from inspire_json_merger.merger_config import (
    ArxivOnArxivOperations,
    PublisherOnArxivOperations,
    PublisherOnPublisherOperations,
)


from inspire_json_merger.inspire_json_merger import (
    _get_configuration,
    get_acquisition_source,
    get_head_source
)


def test_get_acquisition_source_non_arxiv():
    rec = {
        'acquisition_source': {
            'source': 'foo'
        }
    }
    assert get_acquisition_source(rec) == 'foo'
    validate_subschema(rec)


def test_get_acquisition_source_missing():
    rec = {
        'acquisition_source': {}
    }
    assert get_acquisition_source(rec) == 'arxiv'
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


def test_get_configuration_arxiv_on_arxiv():
    assert _get_configuration('arxiv', 'arxiv') == ArxivOnArxivOperations


def test_get_configuration_publisher_on_publisher():
    assert _get_configuration('publisher', 'publisher') == PublisherOnPublisherOperations


def test_get_configuration_publisher_on_arxiv():
    assert _get_configuration('arxiv', 'publisher') == PublisherOnArxivOperations


@pytest.mark.xfail(reason='Not implemented yet')
def test_get_configuration_arxiv_on_publisher():
    _get_configuration('publisher', 'arxiv')
