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

from __future__ import absolute_import, division, print_function

from inspire_utils.record import get_value
from inspire_utils.helpers import force_list
from json_merger.merger import MergeError, Merger

from inspire_json_merger.config import (
    ArxivOnArxivOperations,
    ArxivOnPublisherOperations,
    ErratumOnPublisherOperations,
    ManualMergeOperations,
    PublisherOnArxivOperations,
    PublisherOnPublisherOperations,
)
from inspire_json_merger.postprocess import postprocess_results

from inspire_json_merger.utils import filter_conflicts, filter_records


def merge(root, head, update, head_source=None, configuration=None):
    """
    This function instantiate a ``Merger`` object using a configuration in
    according to the ``source`` value of head and update params.
    Then it run the merger on the three files provided in input.

    Params
        root(dict): the last common parent json of head and update
        head(dict): the last version of a record in INSPIRE
        update(dict): the update coming from outside INSPIRE to merge
        head_source(string): the source of the head record. If ``None``,
            heuristics are used to derive it from the metadata. This is useful
            if the HEAD came from legacy and the acquisition_source does not
            reflect the state of the record.

    Return
        A tuple containing the resulted merged record in json format and a
        an object containing all generated conflicts.
    """
    if not configuration:
        configuration = get_configuration(head, update, head_source)
    conflicts = []
    root, head, update = filter_records(root, head, update, filters=configuration.pre_filters)
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
    conflicts = filter_conflicts(conflicts, configuration.conflict_filters)
    merged = merger.merged_root

    return postprocess_results(merged, conflicts)


def get_configuration(head, update, head_source=None):
    """
    This function return the right configuration for the inspire_merge
    function in according to the given sources. Both parameters can not be None.

    Params:
        head(dict): the HEAD record
        update(dict): the UPDATE record
        head_source(string): the source of the HEAD record

    Returns:
        MergerConfigurationOperations: an object containing
        the rules needed to merge HEAD and UPDATE
    """
    head_source = (head_source or get_head_source(head))
    update_source = get_acquisition_source(update)

    if is_manual_merge(head, update):
        return ManualMergeOperations

    if is_erratum(update):
        return ErratumOnPublisherOperations

    if head_source == 'arxiv':
        if update_source == 'arxiv':
            return ArxivOnArxivOperations
        else:
            return PublisherOnArxivOperations
    else:
        if update_source == 'arxiv':
            return ArxivOnPublisherOperations
        else:
            return PublisherOnPublisherOperations


def get_head_source(json_obj):
    def no_freetext_in_publication_info(obj):
        return 'publication_info' in obj and \
            any('pubinfo_freetext' not in pubinfo for pubinfo in obj.get('publication_info'))

    def no_arxiv_in_dois(obj):
        return 'dois' in obj and \
            any(source.lower() != 'arxiv' for source in force_list(get_value(obj, 'dois.source')))

    if no_freetext_in_publication_info(json_obj) or no_arxiv_in_dois(json_obj):
        return 'publisher'

    elif 'arxiv_eprints' in json_obj:
        return 'arxiv'

    else:
        return 'publisher'


def get_acquisition_source(json_obj):
    source = get_value(json_obj, 'acquisition_source.source')
    return source.lower() if source else None


def is_manual_merge(head, update):
    return ('control_number' in update and 'control_number' in head and update['control_number'] != head['control_number'])


def is_erratum(update):
    erratum_keywords = {"erratum", "corrigendum", "publisher's note", "publisher correction"}
    journal_titles_list = get_value(update, "titles.title", [])
    journal_titles_string = " ".join(journal_titles_list).lower()
    title_contains_erratum_keyword = any([keyword in journal_titles_string for keyword in erratum_keywords])
    title_starts_with_correction_to = any(journal_title.lower().startswith('correction to:') for journal_title in journal_titles_list)
    erratum_in_dois_material = 'erratum' in get_value(update, "dois.material", [])
    if title_contains_erratum_keyword or title_starts_with_correction_to or erratum_in_dois_material:
        return True
