# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2020 CERN.
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

from inspire_json_merger.postprocess import _insert_to_list, _additem, _process_author_manual_merge_conflict
from inspire_json_merger.utils import ORDER_KEY


def test_insert_to_list_when_position_provided_insode_item():
    item_to_insert = {
        "full_name": "INSERTED",
        ORDER_KEY: 1
    }

    objects_list = [
        {"full_name": "First", ORDER_KEY: 0},
        {"full_name": "Second", ORDER_KEY: 1},
        {"full_name": "Third", ORDER_KEY: 2},
    ]

    expected_insert_position = 2
    expected_merged = [
        {'full_name': 'First', ORDER_KEY: 0},
        {'full_name': 'Second', ORDER_KEY: 1},
        {'full_name': 'INSERTED', ORDER_KEY: 1},
        {'full_name': 'Third', ORDER_KEY: 2}
    ]
    insert_position, merged_objects_list = _insert_to_list(item_to_insert, objects_list)

    assert insert_position == expected_insert_position
    assert merged_objects_list == expected_merged


def test_insert_to_list_when_position_provided_as_parameter():
    item_to_insert = {
        "full_name": "INSERTED",
    }

    objects_list = [
        {"full_name": "First", ORDER_KEY: 0},
        {"full_name": "Second", ORDER_KEY: 1},
        {"full_name": "Third", ORDER_KEY: 2},
    ]

    expected_insert_position = 2
    expected_merged = [
        {'full_name': 'First', ORDER_KEY: 0},
        {'full_name': 'Second', ORDER_KEY: 1},
        {'full_name': 'INSERTED'},
        {'full_name': 'Third', ORDER_KEY: 2}
    ]
    insert_position, merged_objects_list = _insert_to_list(item_to_insert, objects_list, 1)

    assert insert_position == expected_insert_position
    assert merged_objects_list == expected_merged


def test_insert_to_list_when_list_without_order_key_but_item_has_it():
    item_to_insert = {
        "full_name": "INSERTED",
        ORDER_KEY: 1
    }

    objects_list = [
        {"full_name": "First"},
        {"full_name": "Second"},
        {"full_name": "Third"},
    ]

    expected_insert_position = 2
    expected_merged = [
        {'full_name': 'First'},
        {'full_name': 'Second'},
        {'full_name': 'INSERTED', ORDER_KEY: 1},
        {'full_name': 'Third'}
    ]
    insert_position, merged_objects_list = _insert_to_list(item_to_insert, objects_list)

    assert insert_position == expected_insert_position
    assert merged_objects_list == expected_merged


def test_insert_to_list_when_item_is_withour_order_key():
    item_to_insert = {
        "full_name": "INSERTED",
    }

    objects_list = [
        {"full_name": "First", ORDER_KEY: 0},
        {"full_name": "Second", ORDER_KEY: 1},
        {"full_name": "Third", ORDER_KEY: 2},
    ]
    expected_position = 3
    expected_merged = [
        {"full_name": "First", ORDER_KEY: 0},
        {"full_name": "Second", ORDER_KEY: 1},
        {"full_name": "Third", ORDER_KEY: 2},
        {"full_name": "INSERTED"},
    ]
    insert_position, merged_objects_list = _insert_to_list(item_to_insert, objects_list)

    assert insert_position == expected_position
    assert merged_objects_list == expected_merged


def test_insert_to_list_when_position_exceeds_lists_elements_count():
    item_to_insert = {
        "full_name": "INSERTED",
        ORDER_KEY: 10
    }

    objects_list = [
        {"full_name": "First", ORDER_KEY: 0},
        {"full_name": "Second", ORDER_KEY: 1},
        {"full_name": "Third", ORDER_KEY: 2},
    ]

    expected_insert_position = 3
    expected_merged = [
        {'full_name': 'First', ORDER_KEY: 0},
        {'full_name': 'Second', ORDER_KEY: 1},
        {'full_name': 'Third', ORDER_KEY: 2},
        {'full_name': 'INSERTED', ORDER_KEY: 10},
    ]
    insert_position, merged_objects_list = _insert_to_list(item_to_insert, objects_list)

    assert insert_position == expected_insert_position
    assert merged_objects_list == expected_merged


def test_add_item_on_position():
    item = {"path": "new"}
    object = {
        "some": [
            {"path": "1"},
            {"path": "2"},
            {"path": "3"}
        ]
    }
    path = ("some", 1)

    expected_path = ('some', 2)
    expected_merged = {
        'some': [
            {'path': '1'},
            {'path': '2'},
            {'path': 'new'},
            {'path': '3'}
        ]
    }
    new_path, merged_object = _additem(item, object, path)

    assert new_path == expected_path
    assert merged_object == expected_merged


def test_add_item_at_the_end():
    item = {"path": "new"}
    object = {
        "some": [
            {"path": "1"},
            {"path": "2"},
            {"path": "3"}
        ]
    }
    path = ("some", "-")

    expected_path = ('some', 3)
    expected_merged = {
        'some': [
            {'path': '1'},
            {'path': '2'},
            {'path': '3'},
            {'path': 'new'},
        ]
    }
    new_path, merged_object = _additem(item, object, path)

    assert new_path == expected_path
    assert merged_object == expected_merged


def test_add_item_on_position_in_dictionary():
    item = {"inside": "new"}
    object = {
        "some": [
            {"path": "1"},
            {"path": "2"},
            {"path": "3"}
        ]
    }
    path = ("some", 1, "path")

    expected_path = ('some', 1, 'path')
    expected_merged = {
        'some': [
            {'path': '1'},
            {'path': {"inside": "new"}},
            {'path': '3'}
        ]
    }
    new_path, merged_object = _additem(item, object, path)

    assert new_path == expected_path
    assert merged_object == expected_merged


def test_add_item_process_single_item_without_index_when_adding_to_list():
    whole_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key': ['a', 'b', 'c']
    }
    item = 'd'
    path = ("key",)

    expected_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key': ['a', 'b', 'c', 'd']
    }
    expected_new_path = ("key", 3)

    new_path, new_object = _additem(item, whole_object, path)

    assert new_path == expected_new_path
    assert new_object == expected_object


def test_add_item_overwrites_whole_key_when_needed():
    whole_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key': ['a', 'b', 'c']
    }
    item = ['d']
    path = ("key",)

    expected_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key': ['d']
    }
    expected_new_path = ("key",)

    new_path, new_object = _additem(item, whole_object, path)

    assert new_path == expected_new_path
    assert new_object == expected_object


def test_add_item_process_deep_item_without_index_when_adding_to_list():
    whole_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key1': {'key2': ['a', 'b', 'c']}
    }
    item = 'd'
    path = ("key1", "key2", )

    expected_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key1': {'key2': ['a', 'b', 'c', 'd']}
    }
    expected_new_path = ("key1", "key2", 3)

    new_path, new_object = _additem(item, whole_object, path)

    assert new_path == expected_new_path
    assert new_object == expected_object


def test_add_deep_item_overwrites_whole_key_when_needed():
    whole_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key1': {'key2': ['a', 'b', 'c']}
    }
    item = ['d']
    path = ("key1", "key2", )

    expected_object = {
        'something': {'not_important': ['should', 'be', 'unchanged']},
        'key1': {'key2': ['d']}
    }
    expected_new_path = ("key1", "key2", )

    new_path, new_object = _additem(item, whole_object, path)

    assert new_path == expected_new_path
    assert new_object == expected_object


def test_process_author_manual_merge_conflict_when_head_in_conflict_is_none():
    conflict = (None, None, ({"conflict": "root value"}, None, {"conflict": "update value"}))
    merged = {"authors": []}

    expected_output = (None, merged, None)
    output = _process_author_manual_merge_conflict(conflict, merged)

    assert output == expected_output
