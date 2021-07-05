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

"""Pre-filters to transform the records before the merger operates."""

from __future__ import absolute_import, division, print_function

from functools import partial

import pyrsistent
from inspire_utils.record import get_value
from pyrsistent import freeze, thaw
from six.moves import zip

from inspire_json_merger.utils import ORDER_KEY


def remove_elements_with_source(source, field):
    """Remove all elements matching ``source`` in ``field``."""
    return freeze(
        [element for element in field if element.get('source', '').lower() != source]
    )


def keep_only_update_source_in_field(field, root, head, update):
    """Remove elements from root and head where ``source`` matches the update.

    This is useful if the update needs to overwrite all elements with the same
    source.

    .. note::
        If the update doesn't contain exactly one source in ``field``, the
        records are returned with no modifications.

    Args:
        field (str): the field to filter out.
        root (pmap): the root record, whose ``field`` will be cleaned.
        head (pmap): the head record, whose ``field`` will be cleaned.
        update (pmap): the update record, from which the ``source`` is read.

    Returns:
        tuple: ``(root, head, update)`` with some elements filtered out from
            ``root`` and ``head``.
    """
    update_thawed = thaw(update)
    update_sources = {source.lower() for source in get_value(update_thawed, '.'.join([field, 'source']), [])}
    if not update_sources:
        # If there is no field or source then fallback for source to `aquisition_source.source`
        source = get_value(update_thawed, "acquisition_source.source")
        if source:
            update_sources = {source.lower()}
    if len(update_sources) != 1:
        return root, head, update
    source = update_sources.pop()

    if field in root:
        root = root.set(field, remove_elements_with_source(source, root[field]))
    if field in head:
        head = head.set(field, remove_elements_with_source(source, head[field]))

    return root, head, update


def filter_curated_references(root, head, update):
    """Remove references from either ``head`` or ``update`` depending on curation.

    If references have been curated, then it removes all references from the
    update to keep the existing ones. Otherwise, it removes all references from
    the head to force replacement with the update ones.

    Args:
        root (pmap): the root record.
        head (pmap): the head record.
        update (pmap): the update record.

    Returns:
        tuple: ``(root, head, update)`` with ``references`` removed from ``root`` and either
        ``head`` or ``update``.
    """
    if 'references' not in head or 'references' not in update:
        return root, head, update

    references_curated = are_references_curated(root.get('references', []), head.get('references', []))
    if 'references' in root:
        root = root.remove('references')
    if references_curated:
        update = update.remove('references')
    else:
        head = head.remove('references')

    return root, head, update


def filter_publisher_references(root, head, update):
    """Remove references from ``update`` if there are any in ``head``.

    This is useful when merging a record from a publisher with an update form arXiv,
    as arXiv should never overwrite references from the publisher.
    """
    if 'references' in head:
        root = _remove_if_present(root, 'references')
        update = _remove_if_present(update, 'references')

    return root, head, update


def update_authors_with_ordering_info(root, head, update):
    """Adds ordering information into authors entries.

    This is helpful so we won't loose correct ordering on conflicts.
    Args:
        root (pmap): the root record.
        head (pmap): the head record.
        update (pmap): the update record.

    Returns: A tuple containing root, head and update with authors data
        enriched with ordering information

    """
    if 'authors' in head:
        head = head.update({"authors": _update_authors_list_with_ordering_data(head["authors"])})
    return root, head, update


def _update_authors_list_with_ordering_data(input_list):
    positions = iter(range(len(input_list)))
    return input_list.transform([pyrsistent.ny], lambda element: element.set(ORDER_KEY, (next(positions))))


def are_references_curated(root_refs, head_refs):
    if not root_refs:
        return any('legacy_curated' in head_ref for head_ref in head_refs)

    if len(root_refs) != len(head_refs):
        return True

    if all(ref_almost_equal(root, head) for (root, head) in zip(root_refs, head_refs)):
        return False

    return True


def ref_almost_equal(root_ref, head_ref):
    return _normalize_ref(root_ref) == _normalize_ref(head_ref)


def _normalize_ref(ref):
    ref = _remove_if_present(ref, 'record')
    ref = _remove_if_falsy(ref, 'curated_relation')
    ref = _remove_if_present(ref, 'raw_refs')
    ref = ref.transform(['reference'], lambda reference: _remove_if_present(reference, 'misc'))
    ref = ref.transform(['reference'], lambda reference: _remove_if_present(reference, 'authors'))
    return ref


def _remove_if_present(pmap, key):
    try:
        return pmap.remove(key)
    except KeyError:
        return pmap


def _remove_if_falsy(pmap, key):
    try:
        if not pmap[key]:
            return pmap.remove(key)
        return pmap
    except KeyError:
        return pmap


def remove_references_from_update(root, head, update):
    update = _remove_if_present(update, "references")
    return root, head, update


def clean_root_for_acquisition_source(root, head, update):
    if root.get("acquisition_source"):
        root = root.remove("acquisition_source")
    return root, head, update


filter_documents_same_source = partial(keep_only_update_source_in_field, 'documents')
filter_figures_same_source = partial(keep_only_update_source_in_field, 'figures')
