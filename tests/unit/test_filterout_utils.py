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


from inspire_json_merger.utils.filterout_utils import (
    filter_conflicts_by_path,
    filter_out,
    is_to_delete,
    conflict_to_list
)

from json_merger.conflict import Conflict


def test_conflict_to_list():
    c = Conflict('SET_FIELD', ('figures', 0, 'key'), 'figure1.png')
    assert conflict_to_list(c) == ['figures', 'key']


def test_is_to_delete_false():
    c = Conflict('SET_FIELD', ('figures', 0, 'key'), 'figure1.png')
    to_delete = 'authors'
    assert is_to_delete(c, to_delete) is False


def test_is_to_delete_true():
    c = Conflict('SET_FIELD', ('figures', 0, 'key'), 'figure1.png')
    to_delete = 'figures'
    assert is_to_delete(c, to_delete) is True


def test_is_to_delete_true_longer_path():
    c = Conflict('SET_FIELD', ('figures', 0, 'key'), 'figure1.png')
    to_delete = 'figures.key'
    assert is_to_delete(c, to_delete) is True


def test_is_to_delete_wrong_path():
    c = Conflict('SET_FIELD', ('figures', 0, 'key'), 'figure1.png')
    to_delete = 'figures.keys'
    assert is_to_delete(c, to_delete) is False


def test_delete_conflict_with_path_prefix():
    conflict_list = [
        ('SET_FIELD', ('authors', 0, 'full_name'), 'John Ellis'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure.png')
    ]
    conflict_list = filter_conflicts_by_path(conflict_list, 'authors')
    assert conflict_list == [('SET_FIELD', ('figures', 1, 'key'), 'figure.png')]


def test_delete_conflicts_wrong_path():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name'), 'John Smith')
    ]
    assert len(filter_conflicts_by_path(conflicts, 'authors.source')) is 3


def test_delete_conflicts_good_path():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name'), 'John Smith')
    ]
    assert len(filter_conflicts_by_path(conflicts, 'authors.full_name')) is 2


def test_delete_conflicts_longer_path():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name', 0, 'foo'), 'John Smith')
    ]
    assert len(filter_conflicts_by_path(conflicts, 'authors.full_name')) is 2


def test_delete_conflicts_path_too_long():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name'), 'John Smith')
    ]
    assert len(filter_conflicts_by_path(conflicts, 'figures.key.foo')) is 3


def test_delete_conflicts_more_deletion():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name'), 'John Smith')
    ]
    assert len(filter_conflicts_by_path(conflicts, 'figures')) is 1


def test_filter_out():
    conflicts = [
        ('SET_FIELD', ('figures', 0, 'key'), 'figure1.png'),
        ('SET_FIELD', ('figures', 1, 'key'), 'figure2.png'),
        ('SET_FIELD', ('authors', 1, 'full_name'), 'John Smith'),
        ('SET_FIELD', ('references', 0, 'reference', 'authors', 0, 'inspire_role'), 'John Smith'),
        ('SET_FIELD', ('report_numbers'), 'DESY-17-036')
    ]
    fiels = [
        'authors.affiliations',
        'authors.full_name',
        'report_numbers'
    ]
    assert len(filter_out(conflicts, fiels)) is 4
