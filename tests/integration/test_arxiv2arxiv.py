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
import json
import pytest
from json_merger.errors import MergeError
from json_merger.merger import Merger
from inspire_json_merger.merger_config import (
    MergerConfigurationOperations,
    ARXIV_TO_ARXIV
)

arxiv_to_arxiv_configuration = MergerConfigurationOperations.factory(
    ARXIV_TO_ARXIV
)


def json_merger_arxiv_to_arxiv(root, head, update, merger_operations):
    merger = Merger(
        root, head, update,
        merger_operations.default_dict_merge_op,
        merger_operations.default_list_merge_op,
        merger_operations.comparators,
        merger_operations.list_merge_ops,
        merger_operations.list_dict_ops
    )
    conflicts = None
    try:
        merger.merge()
    except MergeError as e:
        conflicts = [json.loads(c.to_json()) for c in e.content]
    merged = merger.merged_root

    return merged, conflicts


@pytest.mark.xfail()
@pytest.mark.parametrize('scenario', ['arxiv2arxiv'])
def test_complete_merge(update_fixture_loader, scenario):
    root, head, update = update_fixture_loader.load_test(scenario)

    merged, conflict = json_merger_arxiv_to_arxiv(root, head, update, arxiv_to_arxiv_configuration)

    expected_merged = {}
    expected_conflict = []

    assert merged == expected_merged
    assert conflict == expected_conflict
