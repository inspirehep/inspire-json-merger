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

"""Configuration and tools to clean hep literatures before inspire merging"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import copy

from inspire_json_merger.merger_config import ARXIV_TO_ARXIV, \
    ARXIV_TO_PUBLISHER, PUBLISHER_TO_ARXIV, PUBLISHER_TO_PUBLISHER

AA_FILTER_OUT = [
    ['_collections'],
    ['_files'],
    ['authors', 'uuid'],
    ['authors', 'signature_block'],
]


PA_FILTER_OUT = [
    ['_desy_bookkeeping'],
    ['_export_to'],
    ['authors', 'curated_relation'],
    ['control_number'],
    ['deleted'],
    ['deleted_records'],
    ['energy_ranges'],
    ['funding_info'],
    ['inspire_categories'],
    ['legacy_creation_date'],
    ['new_record'],
    ['persistent_identifiers'],
    ['preprint_date'],
    ['references', 'reference', 'texkey'],
    ['report_numbers'],
    ['self'],
    ['special_collections'],
    ['succeeding_entry'],
    ['texkeys'],
    ['thesis_info'],
    ['withdrawn'],
]


PP_FILTER_OUT = [
    ['_collections'],
    ['authors', 'uuid'],
    ['authors', 'signature_block'],
]


AP_FILTER_OUT = []


# maps the configuration to the list of fields to filter out
MAPPING = {
    ARXIV_TO_ARXIV: AA_FILTER_OUT,
    PUBLISHER_TO_ARXIV: PUBLISHER_TO_ARXIV,
    PUBLISHER_TO_PUBLISHER: PP_FILTER_OUT,
    ARXIV_TO_PUBLISHER: AP_FILTER_OUT
}


def filter_out(rule, obj):
    """
    Use this function to automatically filter all the entries defined for a
    given rule.

    Params:
        rule(string): one of hte `inspire-json-merger` rules.
        obj(dict): the dict to filter.
    """
    if rule in MAPPING:
        to_delete = MAPPING[rule]
        deleted_values = []
        for keys_path in to_delete:
            delete_from_nested_dict(obj, keys_path)

    else:
        raise KeyError('The specified rule `{}` is not allowed.'.format(rule))


def delete_from_nested_dict(obj, keys_path):
    """
    This function removes entries from a nested dictionary.
    The entry to remove is defined by specifying the path of keys to reach
    the object from the root of the dictionary itself. In case of the
    specified key belongs to objects in a list, all items of the list will be
    affected by cancellation.

    Params:
        dictionary(dict): the dictionary containing the entries to delete
        keys_path(list): a list of strings containing the path to reach the
        entry to delete.

    Example:

        >>> obj = {
            'authors': [
                {
                    'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
                    'full_name': 'Sempronio',
                },
                {
                    'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
                    'full_name': 'Tizio Caio',
                },
            ]
        }

        >>> delete_from_nested_dict(obj, ['authors', 'full_name'])
        >>> 'full_name' not in obj['authors'][0]
        True
    """
    if not obj or not keys_path or len(keys_path) is 0:
        return

    if isinstance(obj, dict):
        root = keys_path.pop(0)
        if root in obj.keys():

            if len(keys_path) is 0:
                del obj[root]

            else:
                delete_from_nested_dict(obj[root], copy.copy(keys_path))

    elif isinstance(obj, list):
        for el in obj:
            delete_from_nested_dict(el, copy.copy(keys_path))

    else:
        del obj


if __name__ == '__main__':
    obj = {
        'authors': [
            {
                'uuid':         '160b80bf-7553-47f0-b40b-327e28e7756c',
                'full_name':    'Sempronio',
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
                'uuid':      '160b80bf-7553-47f0-b40b-327e28e7756c',
                'full_name': 'Tizio Caio',
                'record':    {
                    '$ref': 'foobar'
                }
            },
        ]
    }

    delete_from_nested_dict(obj, ['authors', 'uuid'])
    assert 'uuid' not in obj['authors'][0]
    assert 'uuid' not in obj['authors'][1]

    delete_from_nested_dict(obj, ['authors', 'record', '$ref'])
    assert '$ref' not in obj['authors'][1]['record']
