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

import itertools
import json
from collections import Iterable

from json_merger.conflict import Conflict
from pyrsistent import thaw

from inspire_json_merger.utils import ORDER_KEY


def postprocess_results(merged, conflicts):
    """Run all postprocessing to provide output understandable by record-editor.

    Args:
        merged(dict): Merged document
        conflicts(list): List of all possible conflicts

    Returns: A tuple containing the resulted merged record in json format and a
        an list containing all generated conflicts.

    """

    conflicts, merged = postprocess_conflicts(conflicts, merged)
    conflicts_as_json = [json.loads(c.to_json()) for c in conflicts]
    flat_conflicts_as_json = remove_ordering_from_conflicts(
        list(itertools.chain.from_iterable(conflicts_as_json))
    )
    merged = remove_ordering_from_authors_merged(merged)

    return merged, flat_conflicts_as_json


def remove_ordering_from_conflicts(conflicts):
    """Cleans up ordering information in conflicts."""
    for conflict in conflicts:
        if isinstance(conflict["value"], dict):
            conflict["value"].pop(ORDER_KEY, None)
    return conflicts


def remove_ordering_from_authors_merged(merged):
    """Cleans up ordering information in merged record."""
    authors = []
    if "authors" in merged:
        for author in merged["authors"]:
            author = thaw(author)
            author.pop(ORDER_KEY, None)
            authors.append(author)
        merged["authors"] = authors
    return merged


def postprocess_conflicts(conflicts, merged):
    """Postprocessing conflicts to display only useful conflicts.

    Before flattening and serializing to JSON patch, MERGE conflict looks like this:
    ('MANUAL_MERGE', ('authors',), ( pmap(<ROOT>), pmap(<HEAD>), pmap(<UPDATE>) )),
    This function takes out all MANUAL_MERGE and do as follows:
        - Ignore ROOT
        - Update merged result with HEAD from conflict by inserting the author
            from HEAD at the right position.
        - Look for ADD_BACK_TO_HEAD conflict with identical content as HEAD
            change and remove it as it's already added to HEAD
    Args:
        conflicts(list): List of all possible conflicts
        merged(dict): Merged document

    Returns: A tuple containing the resulted merged record in json format and a
        an list containing all generated conflicts.
    """
    new_conflicts = []
    possible_duplicates = set()
    conflicts = sorted(conflicts, key=lambda conflict: conflict[0])
    # Sort by conflict type so we could process "ADD_BACK_TO_HEAD" after "MANUAL_MERGE"
    while conflicts:
        conflict = conflicts.pop()
        conflict_type, conflict_location, conflict_content = conflict
        if conflict_type == "MANUAL_MERGE" and conflict_location[0] == "authors":
            new_conflict, merged, head = _process_author_manual_merge_conflict(
                conflict, merged
            )
            if new_conflict:
                new_conflicts, conflicts = add_conflict(
                    new_conflict, new_conflicts, conflicts
                )
                possible_duplicates.add(head)
        elif not _is_conflict_duplicated(conflict, possible_duplicates):
            if conflict_type == "ADD_BACK_TO_HEAD":
                new_conflict, merged = _process_add_back_to_head(conflict, merged)
                new_conflicts, conflicts = add_conflict(
                    new_conflict, new_conflicts, conflicts
                )
            else:
                new_conflicts.append(conflict)
    return new_conflicts, merged


def add_conflict(conflict, processed_conflicts, unprocessed_conflicts):
    """Adds conflict which added something to `merged` dict so positions for other conflicts should be updated

    Args:
        conflict(Conflict): curently added conflict
        processed_conflicts(list): List of conflicts already added
        unprocessed_conflicts(list): List of conflicts which will be added
    """
    processed_conflicts = update_conflicts_list(conflict, processed_conflicts)
    unprocessed_conflicts = update_conflicts_list(conflict, unprocessed_conflicts)
    processed_conflicts.append(conflict)

    return processed_conflicts, unprocessed_conflicts


def update_conflicts_list(conflict, conflict_list):
    """Updates positions in provided conflict_list for conflict which will be added

    Args:
        conflict(Conflict): New conflict
        conflict_list(list): List of conflicts where positions should be updated
    """
    new_type, new_path, new_content = conflict
    for idx, processed_conflict in enumerate(conflict_list):
        path = processed_conflict[1]
        if path[0] == new_path[0] and len(path) > 1 and len(new_path) > 1 and path[1] >= new_path[1]:
            path = list(path)
            path[1] += 1
            path = tuple(path)
            conflict_list[idx] = Conflict(
                processed_conflict[0], path, processed_conflict[2]
            )
    return conflict_list


def _process_add_back_to_head(conflict, merged):
    """Process ADD_BACK_TO_HEAD conflicts differently than other conflicts.

    Replace all ADD_BACK_TO_HEAD conflicts to became REMOVE_FIELD conflicts
    also adds value from conflict back to merged_root
    REMOVE_FIELD conflict now points to proper element on list.
    """
    conflict_type, conflict_location, conflict_content = conflict
    if conflict_location[0] == "authors":
        position, merged["authors"] = _insert_to_list(
            conflict_content, merged["authors"]
        )
        insert_path = ("authors", position)
        new_conflict = Conflict("REMOVE_FIELD", insert_path, None)
        return new_conflict, merged
    else:
        insert_path, merged = _additem(conflict_content, merged, conflict_location)
        new_conflict = Conflict("REMOVE_FIELD", insert_path, None)
        return new_conflict, merged


def _additem(item, object, path):
    """Adds item to object on path.

    Args:
        item: Item to add
        object: List or Dictionary to which item should be added
        path(tuple): Path on which item should be added, every element of path is a separate element.
        Path represents place after which item should be added.

    Returns(tuple): Tuple containing path and item merged with item under proper path.
    """
    if path[0]:
        if path[0] == "-":
            position, object = _insert_to_list(item, object)
            return (position,), object
        else:
            try:
                idx = int(path[0])
                if len(path) == 1:
                    idx, object = _insert_to_list(item, object, idx)
                    return (idx,), object
                else:
                    new_path, object[idx] = _additem(item, object[idx], path[1:])
            except ValueError:
                if len(path) == 1:
                    if isinstance(item, list) or not isinstance(object[path[0]], list):
                        object[path[0]] = thaw(item)
                        return (path[0],), object
                    elif item not in object[path[0]]:
                        object[path[0]].append(thaw(item))
                        return (path[0], (len(object[path[0]]) - 1)), object
                else:
                    new_path, object[path[0]] = _additem(
                        item, object[path[0]], path[1:]
                    )
    return (path[0],) + new_path, object


def _is_conflict_duplicated(conflict, possible_duplicates):
    conflict_type, conflict_location, conflict_content = conflict
    if conflict_type == "ADD_BACK_TO_HEAD" and conflict_location[0] == "authors" and conflict_content in possible_duplicates:
        return True
    return False


def _process_author_manual_merge_conflict(conflict, merged):
    """Process author `MANUAL_MERGE` conflict.

    Conflict object is an tuple containing:
    (conflict_type, conflict_location, conflict_data)
    where `conflict_data` is a tuple of: (ROOT, HEAD, UPDATE).
    """
    _, _, (root, head, update) = conflict
    if head and head not in merged["authors"]:
        position, merged["authors"] = _insert_to_list(head, merged["authors"])
        new_conflict = Conflict("SET_FIELD", ("authors", position), update)
        return new_conflict, merged, head
    return None, merged, head


def _insert_to_list(item, objects_list, position=None):
    """Inserts value into list at proper position (as close to requested position as possible but not before it).

    If no position provided element will be added at the end of the list.
    Args:
        item: Value to insert into objects_list with `ORDER_KEY` key
        objects_list(list): List where value should be inserted
        position(int): If set then use this position instead `ORDER_KEY` key

    Returns(tuple): (position on which it was placed, merged objects_list).
    """
    item = thaw(item)
    if not position and ORDER_KEY in item:
        position = item[ORDER_KEY]
    if position is not None:
        for idx, element in enumerate(objects_list):
            if isinstance(element, Iterable) and ORDER_KEY in element:
                if element[ORDER_KEY] > position:
                    objects_list.insert(idx, item)
                    return idx, objects_list
            elif idx > position:
                objects_list.insert(idx, item)
                return idx, objects_list
    objects_list.append(item)
    return len(objects_list) - 1, objects_list
