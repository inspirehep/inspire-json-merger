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

"""Helper functions for authors."""

from __future__ import absolute_import, division, print_function

import re

import six

split_on_re = re.compile(r'[\.\s-]')


def scan_author_string_for_phrases(s):
    """Scan a name string and output an object representing its structure.
    Example:
        Sample output for the name 'Jingleheimer Schmitt, John Jacob, XVI.' is::
            {
                'TOKEN_TAG_LIST' : ['lastnames', 'nonlastnames', 'titles', 'raw'],
                'lastnames'      : ['Jingleheimer', 'Schmitt'],
                'nonlastnames'   : ['John', 'Jacob'],
                'titles'         : ['XVI.'],
                'raw'            : 'Jingleheimer Schmitt, John Jacob, XVI.'
            }
    :param s: the input to be lexically tagged
    :type s: string
    :returns: dict of lexically tagged input items.
    :rtype: dict
    """

    if not isinstance(s, six.text_type):
        s = s.encode('utf-8')

    retval = {
        'TOKEN_TAG_LIST': [
            'lastnames',
            'nonlastnames',
            'titles',
            'raw'],
        'lastnames': [],
        'nonlastnames': [],
        'titles': [],
        'raw': s}
    l = s.split(',')
    if len(l) < 2:
        # No commas means a simple name
        new = s.strip()
        new = s.split(' ')
        if len(new) == 1:
            retval['lastnames'] = new        # rare single-name case
        else:
            retval['lastnames'] = new[-1:]
            retval['nonlastnames'] = new[:-1]
            for tag in ['lastnames', 'nonlastnames']:
                retval[tag] = [x.strip() for x in retval[tag]]
                retval[tag] = [re.split(split_on_re, x)
                               for x in retval[tag]]
                # flatten sublists
                retval[tag] = [item for sublist in retval[tag]
                               for item in sublist]
                retval[tag] = [x for x in retval[tag] if x != '']
    else:
        # Handle lastname-first multiple-names case
        retval['titles'] = l[2:]             # no titles? no problem
        retval['nonlastnames'] = l[1]
        retval['lastnames'] = l[0]
        for tag in ['lastnames', 'nonlastnames']:
            retval[tag] = retval[tag].strip()
            retval[tag] = re.split(split_on_re, retval[tag])
            # filter empty strings
            retval[tag] = [x for x in retval[tag] if x != '']
        retval['titles'] = [x.strip() for x in retval['titles'] if x != '']

    return retval


def sort_conflicts(conflicts):
    """It sorts a list of conflicts in according with the second element of each item of the list.

        :param conflicts: all the merge conflicts
        :type conflicts: list
        :returns: sorted list of conflicts
        :rtype: list
        """
    if conflicts:
        return sorted(
            conflicts,
            key=lambda conflict: conflict[1]
        )
    return None
