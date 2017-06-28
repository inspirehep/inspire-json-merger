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

from inspire_json_merger.merger_config import PublisherToArxivOperations
from inspire_json_merger.utils.utils import filter_conflicts_by_path


def test_filter_conflicts_by_path_empty():
    expected_conflicts = None
    conflicts = filter_conflicts_by_path(
        [],
        PublisherToArxivOperations.relevant_conflicts
    )

    assert expected_conflicts == conflicts


def test_filter_conflicts_by_path_empty(update_fixture_loader):
    input_conflicts = update_fixture_loader.load_single(
        'pub2arxiv',
        'expected_conflict.json'
    )
    expected_conflicts = update_fixture_loader.load_single(
        'pub2arxiv',
        'expected_conflict_filtered.json'
    )
    conflicts = filter_conflicts_by_path(
        input_conflicts,
        PublisherToArxivOperations.relevant_conflicts
    )

    assert expected_conflicts == conflicts
