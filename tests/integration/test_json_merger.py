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

import pytest

from inspire_json_merger.merger_config import ARXIV_TO_ARXIV, \
    PUBLISHER_TO_ARXIV, factory, json_merger


@pytest.mark.parametrize('scenario, merger_configuration_type', [
    ('arxiv2arxiv', ARXIV_TO_ARXIV),
    ('pub2arxiv', PUBLISHER_TO_ARXIV)
])
def test_complete_merge(update_fixture_loader, scenario, merger_configuration_type):
    root, head, update, expected_conflict, expected_merged = update_fixture_loader.load_test(scenario)

    merger_configuration = factory(merger_configuration_type)
    merged, conflict = json_merger(root, head, update, merger_configuration)

    assert merged == expected_merged
    assert conflict == expected_conflict
