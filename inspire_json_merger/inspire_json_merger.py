# -*- coding: utf-8 -*-
#
# This file is part of Inspire.
# Copyright (C) 2017 CERN.
#
# Inspire is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Inspire is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inspire; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


from __future__ import absolute_import, print_function

from inspire_utils.helpers import get_value
from json_merger.merger import MergeError, Merger

from inspire_json_merger.merger_config import ARXIV_TO_ARXIV, \
    ARXIV_TO_PUBLISHER, PUBLISHER_TO_ARXIV, PUBLISHER_TO_PUBLISHER, \
    ArxivToArxivOperations, PublisherToArxivOperations, \
    PublisherToPublisherOperations


# mapping between configuration names and their relative classes.
_MERGER_CONFIGS = {
    ARXIV_TO_ARXIV: ArxivToArxivOperations(),
    PUBLISHER_TO_ARXIV: PublisherToArxivOperations(),
    ARXIV_TO_PUBLISHER: None,
    PUBLISHER_TO_PUBLISHER: PublisherToPublisherOperations()
}


def inspire_json_merge(root, head, update, head_source=None):
    """
    This function instantiate a ``Merger`` object using a configuration in
    according to the ``source`` value of head and update params.
    Then it run the merger on the three files provided in input.

    Params
        root(dict): the last common parent json of head and update
        head(dict): the last version of a record in INSPIRE
        update(dict): the update coming from outside INSPIRE to merge
        head_source(string): the source of the head record. If ``None``,
            heuristics are used to derive it from the metadata.

    Return
        A tuple containing the resulted merged record in json format and a
        an object containing all generated conflicts.
    """
    configuration = _get_configuration(
        head or get_head_source(head),
        get_acquisition_source(update)
    )

    conflicts = None
    merger = Merger(
        root=root, head=head, update=update,
        default_dict_merge_op=configuration.default_dict_merge_op,
        default_list_merge_op=configuration.default_list_merge_op,
        list_dict_ops=configuration.list_dict_ops,
        list_merge_ops=configuration.list_merge_ops,
        comparators=configuration.comparators,
    )

    try:
        merger.merge()
    except MergeError as e:
        conflicts = e.content

    merged = merger.merged_root
    return merged, conflicts


def _get_configuration(head_source, update_source):
    """
    This function return the right configuration for the inspire_merge
    function in according to the given sources. Both parameters can not be None.

    Params
        head_source(string): the source of the HEAD file
        update_source(string): the source of the UPDATE file

    Return
        configuration(MergerConfigurationOperations): an object containing
        the rules needed to merge HEAD and UPDATE
    """
    if head_source is None or update_source is None:
        raise ValueError('Can\'t get any configuration:\n\tHEAD SOURCE: {0}'
                         '\n\tUPDATE SOURCE: {1}'
                         .format(head_source, update_source))
    if head_source.lower() == 'arxiv':
        if update_source.lower() == 'arxiv':
            return _MERGER_CONFIGS.get(ARXIV_TO_ARXIV)
        else:
            return _MERGER_CONFIGS.get(PUBLISHER_TO_ARXIV)
    else:
        if update_source.lower() == 'arxiv':
            raise Exception('Not yet implemented')
            # return _MERGER_CONFIGS.get(ARXIV_TO_PUBLISHER)
        else:
            return _MERGER_CONFIGS.get(PUBLISHER_TO_PUBLISHER)


def get_head_source(json_obj):
    def _has_non_arxiv_field(field_name):
        source = '{}.source'.format(field_name)
        return (
            json_obj.get(field_name) and not get_value(json_obj, source)
            or any(source.lower() != 'arxiv' for source in get_value(json_obj, source))
    )

    if _has_non_arxiv_field('publication_info') or _has_non_arxiv_field('dois'):
        return 'publisher'
    elif 'arxiv_eprints' in json_obj:
        return 'arxiv'
    else:
        return 'publisher'


def get_acquisition_source(json_obj):
    # in case of missing acquisition source, it returns the ARXIV one
    try:
        return json_obj['acquisition_source']['source']
    except KeyError:
        return 'arxiv'
