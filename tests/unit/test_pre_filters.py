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

from inspire_json_merger.utils import filter_records
from inspire_json_merger.pre_filters import filter_documents_same_source


def test_filter_documents_same_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'new_file.pdf',
                'url': '/files/5678-5678-5678-5678/new_file.pdf',
            },
        ],
    }
    expected_head = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected


def test_filter_documents_same_source_multiple_sources_in_update():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, head, update

    assert result == expected


def test_filter_documents_remove_head_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'publisher',
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },

        ],
    }
    expected_head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'old_file.pdf',
                'url': '/files/5678-5678-5678-5678/old_file.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected


def test_filter_documents_same_source_is_case_insensitive_on_source():
    root = {}
    head = {
        'documents': [
            {
                'source': 'arXiv',
                'key': 'file1.pdf',
                'url': '/files/1234-1234-1234-1234/file1.pdf',
            },
            {
                'source': 'arXiv',
                'key': 'file2.pdf',
                'url': '/files/1234-1234-1234-1234/file2.pdf',
            },
            {
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }
    update = {
        'documents': [
            {
                'source': 'arxiv',
                'key': 'new_file.pdf',
                'url': '/files/5678-5678-5678-5678/new_file.pdf',
            },
        ],
    }
    expected_head = {
        'documents': [
            {
                'key': 'file3.pdf',
                'url': '/files/1234-1234-1234-1234/file3.pdf',
            },
        ],
    }

    result = filter_records(root, head, update, filters=[filter_documents_same_source])
    expected = root, expected_head, update

    assert result == expected
