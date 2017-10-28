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

"""Configuration and tools to clean hep literatures before inspire merging"""

from __future__ import absolute_import, division, print_function


def filter_out(conflicts_list, fields):
    """Use this function to automatically filter all the entries defined for a
    given rule.

    Params:
        conflicts_list(List[Conflict]): the list of conflicts to filter.
        fields(List[str]): fields to filter out, using an accessor syntax of
            the form ``field.subfield.subsubfield``.

    Return:
        List[Conflict]: the given list filtered by `fields`
    """
    for field in fields:
        conflicts_list = filter_conflicts_by_path(conflicts_list, field)

    return conflicts_list


def filter_conflicts_by_path(conflict_list, to_delete_path):
    """Filter a list of conflict for the given string. The string represents
    the path of the conflict in the form ``field.subfield.subsubfield``.

    Example:
        conflict_list = [
            ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
            ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png')
        ]

        to_delete_path = 'figures.keys'
    """
    return [conf for conf in conflict_list if not is_to_delete(conf, to_delete_path)]


def is_to_delete(conflict, keys_path):
    to_delete = keys_path.split('.')
    conflict_path = conflict_to_list(conflict)

    if len(to_delete) > len(conflict_path):
        return False

    i = 0
    while i < len(conflict_path) and i < len(to_delete):
        c = conflict_path[i]
        d = to_delete[i]

        if c != d:
            return False
        i += 1

    return True


def conflict_to_list(conflict):
    path = conflict[1]
    return [p for p in path if not isinstance(p, int)]
