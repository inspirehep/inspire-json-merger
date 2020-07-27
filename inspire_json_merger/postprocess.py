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

from json_merger.conflict import Conflict

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
        list(itertools.chain.from_iterable(conflicts_as_json)))
    merged = remove_ordering_from_authors_merged(merged)

    return merged, flat_conflicts_as_json


def remove_ordering_from_conflicts(conflicts):
    """Cleans up ordering information in conflicts."""
    for conflict in conflicts:
        if isinstance(conflict['value'], dict):
            conflict["value"].pop(ORDER_KEY, None)
    return conflicts


def remove_ordering_from_authors_merged(merged):
    """Cleans up ordering information in merged record."""
    if 'authors' in merged:
        for author in merged["authors"]:
            author.pop(ORDER_KEY, None)
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
    possible_duplicates = []
    for conflict in conflicts:
        conflict_type, conflict_location, conflict_content = conflict
        if conflict_type == "MANUAL_MERGE" and conflict_location[0] == "authors":
            new_conflict, merged, head = _process_author_manual_merge_conflict(conflict, merged)
            if new_conflict:
                new_conflicts.append(new_conflict)
                possible_duplicates.append(head)
        else:
            new_conflicts.append(conflict)
    new_conflicts = _remove_duplicates(new_conflicts, set(possible_duplicates))
    return new_conflicts, merged


def _remove_duplicates(conflicts, possible_duplicates):
    new_conflicts = []
    for conflict in conflicts:
        conflict_type, conflict_location, conflict_content = conflict
        if conflict_type == "ADD_BACK_TO_HEAD" and conflict_location[0] == "authors" and conflict_content in possible_duplicates:
            continue
        else:
            new_conflicts.append(conflict)
    return new_conflicts


def _process_author_manual_merge_conflict(conflict, merged):
    """Process author `MANUAL_MERGE` conflict

    Conflict object is an tuple containing
    (conflict_type, conflict_location, conflict_data)
    where `conflict_data` is a tuple of: (ROOT, HEAD, UPDATE)
    """
    _, _, (root, head, update) = conflict
    if head not in merged["authors"]:
        position, merged['authors'] = _insert_author(dict(head), merged['authors'])
        new_conflict = Conflict("SET_FIELD", ("authors/{position}".format(position=position),), update)
        return new_conflict, merged, head
    return None, merged, head


def _insert_author(head, merged):
    position = head[ORDER_KEY]
    for idx, element in enumerate(merged):
        if ORDER_KEY in element and element[ORDER_KEY] > position:
            merged.insert(idx, head)
            return idx, merged
    merged.append(head)
    return len(merged) - 1, merged
