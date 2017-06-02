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

from inspire_json_merger.utils.filterout_utils import delete_from_nested_dict, \
    filter_out


@pytest.fixture()
def test_input():
    return {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
                'full_name': 'Sempronio',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'recid': 902867,
                    }, {
                        'value': 'MIT',
                        'recid': 123456,
                    }
                ]
            },
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
                'full_name': 'Tizio Caio',
                'record': {
                    '$ref': 'foobar'
                }
            },
        ]
    }


def test_delete_from_nested_dict_delete_field(test_input):
    delete_from_nested_dict(test_input, ['authors', 'uuid'])
    for item in test_input['authors']:
        if 'uuid' in item:
            pytest.fail('FAIL: field not removed')


def test_delete_from_nested_dict_delete_item_in_list(test_input):
    delete_from_nested_dict(test_input, ['authors', 'affiliations', 'recid'])
    for item in test_input['authors'][0]['affiliations']:
        if 'recid' in item:
            pytest.fail('FAIL: field not removed')


def test_delete_from_nested_dict_delete_item_in_dict(test_input):
    delete_from_nested_dict(test_input, ['authors', 'record', '$ref'])
    for item in test_input['authors'][1]['record']:
        if '$ref' in item:
            pytest.fail('FAIL: field not removed')


def test_delete_from_nested_dict_empty_list(test_input):
    original_input = test_input
    delete_from_nested_dict(test_input, [])
    assert test_input == original_input


def test_delete_from_nested_dict_none_list(test_input):
    original_input = test_input
    delete_from_nested_dict(test_input, None)
    assert test_input == original_input


def test_delete_from_nested_dict_empty_dict():
    empty_dict = {}
    delete_from_nested_dict({}, ['authors'])
    assert empty_dict == {}
