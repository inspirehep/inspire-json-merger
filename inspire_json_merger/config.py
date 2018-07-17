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

from json_merger.config import DictMergerOps as D, UnifierOps as U

from inspire_json_merger.utils import PRE_FILTERS
from .comparators import COMPARATORS

"""
This module provides different sets of rules that `inspire_json_merge`
"""


class MergerConfigurationOperations(object):
    default_dict_merge_op = D.FALLBACK_KEEP_UPDATE
    default_list_merge_op = U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST
    conflict_filters = None
    comparators = None
    pre_filters = None
    list_dict_ops = None
    list_merge_ops = None


class ArxivOnArxivOperations(MergerConfigurationOperations):
    comparators = COMPARATORS
    pre_filters = PRE_FILTERS
    conflict_filters = [
        '_collections',
        '_files',
        'abstracts',
        'acquisition_source',
        'arxiv_eprints',
        'authors.affiliations',
        'authors.full_name',
        'authors.raw_affiliations',
        'citeable',
        'core',
        'curated',
        'dois',
        'license',
        'number_of_pages',
        'persistent_identifiers',
        'preprint_date',
        'public_notes',
        'publication_info',
    ]

    list_merge_ops = {
        '_collections': U.KEEP_ONLY_HEAD_ENTITIES,
        '_files': U.KEEP_ONLY_UPDATE_ENTITIES,
        'authors': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'authors.ids': U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST,
        'authors.raw_affiliations': U.KEEP_ONLY_UPDATE_ENTITIES,
        'collaborations': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'document_type': U.KEEP_ONLY_HEAD_ENTITIES,
        'inspire_categories': U.KEEP_ONLY_HEAD_ENTITIES,
    }

    # these rules are meaningless for fields which are arrays and have no comparator
    list_dict_ops = {
        'authors.full_name': D.keep_longest,
        'authors.ids': D.FALLBACK_KEEP_HEAD,
        'authors.raw_affiliations': D.FALLBACK_KEEP_UPDATE,
        'core': D.FALLBACK_KEEP_HEAD,
        'curated': D.FALLBACK_KEEP_HEAD,
        'persistent_identifiers': D.FALLBACK_KEEP_HEAD,
        'preprint_date': D.FALLBACK_KEEP_HEAD,
        'publication_info': D.FALLBACK_KEEP_HEAD,
    }


class ArxivOnPublisherOperations(MergerConfigurationOperations):
    comparators = COMPARATORS
    pre_filters = PRE_FILTERS
    default_dict_merge_op = D.FALLBACK_KEEP_HEAD
    default_list_merge_op = U.KEEP_ONLY_HEAD_ENTITIES
    conflict_filters = [
        '_files',
        'abstracts',
        'acquisition_source',
        'arxiv_eprints',
        'authors.affiliations',
        'authors.full_name',
        'authors.raw_affiliations',
        'citeable',
        'core',
        'curated',
        'dois',
        'inspire_categories',
        'license',
        'number_of_pages',
        'persistent_identifiers',
        'preprint_date',
        'public_notes',
        'publication_info',
    ]
    list_merge_ops = {
        'abstracts': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'arxiv_eprints': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'arxiv_eprints.categories': U.KEEP_ONLY_UPDATE_ENTITIES,
        'authors': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'authors.ids': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'authors.raw_affiliations': U.KEEP_ONLY_HEAD_ENTITIES,
        'core': D.FALLBACK_KEEP_HEAD,
        'dois': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'external_system_identifiers': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'figures': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'license': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'public_notes': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'publication_info': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'report_numbers': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
        'titles': U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    }
    list_dict_ops = {
        'abstracts': D.FALLBACK_KEEP_UPDATE,
        'acquisition_source': D.FALLBACK_KEEP_UPDATE,
        'authors.full_name': D.keep_longest,
        'license': D.FALLBACK_KEEP_UPDATE,
        'public_notes': D.FALLBACK_KEEP_UPDATE,
    }


class ManualMergeOperations(MergerConfigurationOperations):
    default_dict_merge_op = D.FALLBACK_KEEP_HEAD
    default_list_merge_op = U.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST
    comparators = COMPARATORS
    pre_filters = []  # don't delete files with the same source
    conflict_filters = [
        '_collections',
        '_desy_bookkeeping',
        '_files',
        'acquisition_source',
        'control_number',
        'self',
    ]
    list_merge_ops = {}
    list_dict_ops = {
        'acquisition_source': D.FALLBACK_KEEP_UPDATE,
        'authors.full_name': D.keep_longest,
    }


class PublisherOnArxivOperations(MergerConfigurationOperations):
    comparators = COMPARATORS
    pre_filters = PRE_FILTERS
    conflict_filters = [
        '_collections',
        '_files',
        'acquisition_source',
        'authors.full_name',
        'authors.raw_affiliations',
        'citeable',
        'copyright',
        'core',
        'curated',
        'imprints',
        'inspire_categories',
        'license',
        'number_of_pages',
        'preprint_date',
    ]

    list_merge_ops = {
        '_collections': U.KEEP_ONLY_HEAD_ENTITIES,
        'authors': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'authors.ids': U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST,
        'authors.raw_affiliations': U.KEEP_ONLY_UPDATE_ENTITIES,
        'collaborations': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'corporate_author': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'documents': U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST,
        'document_type': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'inspire_categories': U.KEEP_ONLY_HEAD_ENTITIES,
    }

    list_dict_ops = {
        'arxiv_eprints': D.FALLBACK_KEEP_HEAD,
        'authors.full_name': D.keep_longest,
        'core': D.FALLBACK_KEEP_HEAD,
        'curated': D.FALLBACK_KEEP_HEAD,
        'preprint_date': D.FALLBACK_KEEP_HEAD,
        'report_numbers': D.FALLBACK_KEEP_HEAD,
    }


class PublisherOnPublisherOperations(MergerConfigurationOperations):
    comparators = COMPARATORS
    pre_filters = PRE_FILTERS
    conflict_filters = [
        '_collections',
        '_files',
        'acquisition_source',
        'authors.full_name',
        'authors.raw_affiliations',
        'citeable',
        'copyright',
        'core',
        'curated',
        'imprints',
        'inspire_categories',
        'license',
        'number_of_pages',
        'preprint_date',
    ]

    list_merge_ops = {
        '_collections': U.KEEP_ONLY_HEAD_ENTITIES,
        'authors': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'authors.ids': U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST,
        'authors.raw_affiliations': U.KEEP_ONLY_UPDATE_ENTITIES,
        'collaborations': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'corporate_author': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'documents': U.KEEP_UPDATE_AND_HEAD_ENTITIES_UPDATE_FIRST,
        'document_type': U.KEEP_UPDATE_ENTITIES_CONFLICT_ON_HEAD_DELETE,
        'inspire_categories': U.KEEP_ONLY_HEAD_ENTITIES,
    }

    list_dict_ops = {
        'arxiv_eprints': D.FALLBACK_KEEP_HEAD,
        'authors.full_name': D.keep_longest,
        'core': D.FALLBACK_KEEP_HEAD,
        'curated': D.FALLBACK_KEEP_HEAD,
        'preprint_date': D.FALLBACK_KEEP_HEAD,
        'report_numbers': D.FALLBACK_KEEP_HEAD,
    }
