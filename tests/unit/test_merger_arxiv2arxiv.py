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

"""
This test check the correctness of the merger rules on all the schema's keys.
Important: in order to check the schema's coverage, please add the `cover`
decorator to each test, referring to the schema's key under test.
"""

from __future__ import absolute_import, division, print_function

from mock import MagicMock
import pytest

from inspire_json_merger import api
from inspire_json_merger.api import merge

from utils import assert_ordered_conflicts, validate_subschema


@pytest.fixture(autouse=True, scope='module')
def mock_get_acquisition_source():
    original_func = api.get_acquisition_source
    api.get_acquisition_source = MagicMock(return_value='arxiv')
    yield
    api.get_acquisition_source = original_func


def test_merging_acquisition_source_field():
    root = {}
    # record_id: 1517095
    head = {
        'acquisition_source': {
            'method': 'submitter',
            'source': 'arxiv'
        }
    }
    update = {
        'acquisition_source': {
            'method': 'batchuploader',
            'source': 'arxiv'
        }
    }

    expected_merged = update
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_full_name_field_keeps_longest_name():
    root = {
        'authors': [
            {
                'full_name': 'Pitts Kevin',
            }
        ]
    }
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin John',
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin',
            }
        ]
    }

    expected_merged = head

    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_raw_affiliations_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'raw_affiliations': [
                    {
                        'source': 'arxiv',
                        'value': 'Department of Physics, Indiana University, Bloomington, IN 47405, USA'
                    }
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'raw_affiliations': [
                    {
                        'source': 'arxiv',
                        'value': 'Department of Physics, Indiana University, Bloomington, IN 47405, US'
                    },
                    {
                        'source': 'arxiv',
                        'value': 'Padua U',
                    }
                ]
            }
        ]
    }

    expected_merged = update
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_dois_field_handles_repeated_values():
    root = {
        'dois': [
            {
                'material': 'preprint',
                'value': '10.1023/A:1026654312961'
            }
        ]
    }
    head = {
        'dois': [
            {
                'material': 'preprint',
                'source': 'nowhere',
                'value': '10.1023/A:1026654312961'
            },
            {
                'source': 'nowhere',
                'value': '10.1023/B:1026654312961'
            },
        ]
    }
    update = {
        'dois': [
            {
                'material': 'publication',
                'value': '10.1023/A:1026654312961'
            },
            {
                'material': 'erratum',
                'source': 'nowhere',
                'value': '10.1023/B:1026654312961'
            },
        ]
    }

    expected_merged = {
        'dois': [
            {
                'material': 'preprint',
                'source': 'nowhere',
                'value': '10.1023/A:1026654312961'
            },
            {
                'material': 'publication',
                'value': '10.1023/A:1026654312961'
            },
            {
                'material': 'erratum',
                'source': 'nowhere',
                'value': '10.1023/B:1026654312961'
            },
        ]
    }
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_inspire_categories_field():
    root = {'inspire_categories': [
        {
            'source': 'INSPIRE',
            'term': 'Theory-HEP'
        }
    ]}
    head = {'inspire_categories': [
        {
            'source': 'curator',
            'term': 'Theory-HEP'
        }, {
            'source': 'curator',
            'term': 'Theory-Nucl'
        }
    ]}
    update = {'inspire_categories': [
        {
            'source': 'arxiv',
            'term': 'Computing'
        }, {
            'source': 'arxiv',
            'term': 'Other'
        }
    ]}

    expected_merged = head
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_license_field():
    root = {
        'license': [
            {
                'imposing': 'Elsevier',
                'url': 'http://creativecommons.org/licenses/by/4.0/',
                'license': 'elsevier foo bar'
            }
        ]
    }
    head = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar'
        },
        {
            'imposing': 'arXiv',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'arxiv foo bar'
        }
    ]}
    update = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar updated!'
        }
    ]}

    expected_merged = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar updated!'
        },
        {
            'imposing': 'arXiv',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'arxiv foo bar'
        }
    ]}
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_publication_info_field():
    root = {
        'publication_info': [
            {
                "hidden": True,
                "journal_title": "Adv.Theor.Math.Phys.",
                "journal_volume": "12",
                "page_end": "979",
                "page_start": "948",
                "year": 2008
            }
        ]
    }  # record 697133
    head = {
        'publication_info': [
            {
                "hidden": True,
                "journal_title": "Adv.Theor.Math.Phys.",
                "journal_record": {
                    "$ref": "http://labs.inspirehep.net/api/journals/1212914"
                },
                "journal_volume": "12",
                "page_end": "979",
                "page_start": "948",
                "year": 2008
            }
        ]
    }
    update = {
        'publication_info': [
            {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': '1',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            },
        ]
    }

    expected_merged = {
        'publication_info': [
            {
                'artid': '948-979',
                'cnum': 'C12-03-10',
                'curated_relation': True,
                'journal_title': 'Adv.Theor.Math.Phys.',
                "journal_volume": "12",
                'journal_issue': '1',
                "journal_record": {
                    "$ref": "http://labs.inspirehep.net/api/journals/1212914"
                },
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
                "year": 2008,
            }
        ]
    }
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_report_numbers_field_repeated_values():
    root = {'report_numbers': [
        {
            'source': 'arXiv',
            'value': 'CERN-CMS-2018-001',
        },
    ]}  # record: 1598022
    head = {'report_numbers': [
        {
            'hidden': True,
            'source': 'arXiv',
            'value': 'CERN-CMS-2018-001',
        },
        {
            'value': 'CERN-CMS-2018-001',
        },
    ]}
    update = {'report_numbers': [
        {
            'source': 'arXiv',
            'value': 'CERN-CMS-2018-001',
        },
    ]}

    expected_merged = head
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_merging_titles_field():
    root = {'titles': [
        {
            'source': 'arXiv',
            'title': 'ANTARES: An observatory at the seabed '
                      'to the confines of the Universe'
        }  # record: 1519935
    ]}
    head = {'titles': [
        {
            'source': 'arXiv',
            'subtitle': 'this subtitle has been added by a curator',
            'title': 'ANTARES: An observatory at the seabed '
                        'to the confines of the Universe'
        }
    ]}
    update = {'titles': [
        {
            'source': 'arXiv',
            'title': 'ANTARES: Un osservatorio foo bar'
        },
    ]}

    expected_merged = {'titles': [
        {
            'source': 'arXiv',
            'subtitle': 'this subtitle has been added by a curator',
            'title': 'ANTARES: An observatory at the seabed '
                        'to the confines of the Universe'
        },
        {
            'source': 'arXiv',
            'title': 'ANTARES: Un osservatorio foo bar'
        },
    ]}
    expected_conflict = []

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_figures():
    root = {}
    head = {
        'figures': [
            {
                'key': 'figure1.png',
                'caption': 'Figure 1',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/figure1.png',
            },
            {
                'key': 'figure2.png',
                'caption': 'Figure 2',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/figure2.png',
            }
        ]
    }
    update = {
        'figures': [
            {
                'key': 'new_figure1.png',
                'caption': 'Figure 1',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure1.png',
            },
            {
                'key': 'new_figure2.png',
                'caption': 'Figure 2',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure2.png',
            }
        ]
    }

    expected_merged = update
    expected_conflict = []

    merged, conflict = merge(root, head, update,
                             head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_figures_dont_duplicate_keys_even_from_different_sources():
    root = {}
    head = {
        'figures': [
            {
                'key': 'figure1.png',
                'caption': 'Figure 1',
                'source': 'arXiv',
                'url': '/files/1234-1234-1234-1234/figure1.png',
            },
            {
                'key': 'figure2.png',
                'caption': 'Figure 2',
                'source': 'APS',
                'url': '/files/1234-1234-1234-1234/figure2.png',
            },
            {
                'key': 'figure3.png',
                'caption': 'Figure 3',
                'source': 'APS',
                'url': '/files/1234-1234-1234-1234/figure3.png',
            },
        ],
    }
    update = {
        'figures': [
            {
                'key': 'new_figure1.png',
                'caption': 'Figure 1',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure1.png',
            },
            {
                'key': 'figure2.png',
                'caption': 'Figure 2',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure2.png',
            },
        ],
    }

    expected_merged = {
        'figures': [
            {
                'key': 'new_figure1.png',
                'caption': 'Figure 1',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure1.png',
            },
            {
                'key': 'figure2.png',
                'caption': 'Figure 2',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/figure2.png',
            },
            {
                'key': 'figure3.png',
                'caption': 'Figure 3',
                'source': 'APS',
                'url': '/files/1234-1234-1234-1234/figure3.png',
            },
        ],
    }

    expected_conflict = []

    merged, conflict = merge(root, head, update,
                             head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_documents():
    root = {}
    head = {
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
    update = {
        'documents': [
            {
                'key': 'pdf.pdf',
                'description': 'paper',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/pdf.pdf',
            },
            {
                'key': 'foo.xml',
                'description': 'some xml files',
                'source': 'arXiv',
                'url': '/files/5678-5678-5678-5678/foo.xml',
            }
        ]
    }

    expected_merged = update
    expected_conflict = []

    merged, conflict = merge(root, head, update,
                             head_source='arxiv')
    assert merged == expected_merged
    assert_ordered_conflicts(conflict, expected_conflict)
    validate_subschema(merged)


def test_head_curates_author_no_duplicate():
    # https://labs.inspirehep.net/api/holdingpen/1268973
    root = {
        'authors': [
            {
                "full_name": "Li, Zhengxiang"
            },
        ]
    }
    head = {
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Beijing Normal U."
                    }
                ],
                "full_name": "Li, Zheng-Xiang",
            }
        ]
    }
    update = {
        'authors': [
            {
                "full_name": "Li, Zhengxiang"
            },
        ]
    }

    expected_merged = {
        'authors': [
            {'full_name': 'Li, Zhengxiang'},
            {
                'full_name': 'Li, Zheng-Xiang', 'affiliations': [
                    {'value': 'Beijing Normal U.'}
                ]
            }
        ]
    }

    expected_conflict = [{
        'path': '/authors/1',
        'op': 'remove',
        'value': None,
        '$type': 'REMOVE_FIELD'
    }]

    merged, conflict = merge(root, head, update, head_source='arxiv')
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)
