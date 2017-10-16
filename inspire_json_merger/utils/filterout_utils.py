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


def filter_out(fields, obj):
    """
    Use this function to automatically filter all the entries defined for a
    given rule.

    Params:
        fields(List[List[str]]): fields to filter out from obj.
        obj(dict): the dict to filter.
    """
    for field in fields:
        delete_from_nested_dict(obj, fields)


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
        ...     'authors': [
        ...         {
        ...             'full_name': 'Sempronio',
        ...             'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
        ...         },
        ...         {
        ...             'full_name': 'Tizio Caio',
        ...             'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
        ...         },
        ...     ]
        ... }
        >>> delete_from_nested_dict(obj, ['authors', 'full_name'])
        >>> 'full_name' not in obj['authors'][0]
        True

    """
    if not obj or not keys_path:
        return

    if isinstance(obj, dict):
        root = keys_path.pop(0)
        if root in obj.keys():
            if keys_path == []:
                del obj[root]
            else:
                delete_from_nested_dict(obj[root], copy.copy(keys_path))

    elif isinstance(obj, list):
        for el in obj:
            delete_from_nested_dict(el, copy.copy(keys_path))

    else:
        del obj
