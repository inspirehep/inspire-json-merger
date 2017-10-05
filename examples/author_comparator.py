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

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from json_merger.config import UnifierOps

from inspire_json_merger.inspire_json_merger import inspire_json_merge
from inspire_json_merger.merger_config import ArxivToArxivOperations

# Editing this, so that it is easier to identify whether two names were matched or not. Using this authors.full_name
# will have two entries if the names didn't match.
ArxivToArxivOperations.list_merge_ops['authors'] = UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST

# Enable verbose if you want to see "head", "update", "merged" and "conflict" records.
VERBOSE = False


def demo_author_comparator(name, updated_name=None, verbose=False):
    """Receives two names or a list of two names and prints whether they matched or not."""

    # Pre process input
    if not updated_name:
        assert len(name) == 2
        name, updated_name = name

    root = {'authors': [{}]}
    head = {'authors': [{'full_name': name}]}
    update = {'authors': [{'full_name': updated_name}]}

    merged, conflict = inspire_json_merge(root, head, update)

    def _are_merged():
        """Predicate check for whether two records where merged.

        This is based on the edit of the merger configuration that we did on top of this module.
        """
        return len(merged.get('authors')) == 1

    # ##### Print helper closures #####
    def _emit_head_update_merged():
        return "[\n" + \
                "\tHEAD: \t\t" + str(head) + ',\n' + \
                "\tUPDATE: \t" + str(update) + ',\n' + \
                "\tMERGED: \t" + str(merged) + ',\n' + \
               "\tCONFLICT: \t" + str(conflict) + '\n]'

    def _emit_names():
        return '"' + name + '", "' + updated_name + '"'

    # ##### Result printing #####
    color = '\033[32m' if _are_merged() else '\033[31m'
    if verbose:
        print(color + '[' + ('' if _are_merged() else 'NO ') + 'match]: ' + _emit_head_update_merged() + '\033[0m')
    else:
        print(color + '[' + ('' if _are_merged() else 'NO ') + 'match]: ' + _emit_names() + '\033[0m')


if __name__ == '__main__':
    names_tests = [
        ['Cox, Brian', 'Cox, Brian'],
        ['O Brien, Dara', 'O Briain, Dara'],
        ['O Brien, Dara', 'Christos Aslanoglou'],

        ['John, Ellis', 'John ellis'],
        ['John, Ellis', 'John, Richard Ellis'],
        ['John, Ellis', 'John, R. Ellis'],
        ['John, Ellis', 'Ellis, R. John'],
        ['John, Ellis', 'Ellis, R. J'],
        ['John, Ellis', 'j, r. ellis'],
        ['John, Ellis', 'j, r, ellis'],  # should this work (since the one above does)?
        ['John, Ellis', 'j r ellis'],
        ['John, Ellis', 'j richard ellis'],

        ['J Ellis', 'john r e'],
        ['Ellis J', 'john r e'],
        ['Ellis, J.', 'Ellis, John'],

        ['John R. Ellis', 'j richard ellis'],
        ['John R. Ellis', 'j r ellis'],
        ['John R. Ellis', 'john rich. e'],

        # This follows the format [Last name, (Father's name,) First name]
        ['Παπαδόπουλος, Γ', 'Παπαδόπουλος Γιώργος'],
        ['Παπαδόπουλος, Γ', 'Παπαδόπουλος Μ Γιώργος'],
        ['Παπαδόπουλος, Γ', 'Παπαδόπουλος Μιχάλη Γ'],

        ['Jhon Brian', 'John Brian'],
        ['John Brian', 'John C'],

        ['Gaspari M', 'Gaspari, Massimo'],

        ['Gaspari', 'Gaspari, Maria'],
        ['Gaspari M', 'Gaspari, Maria'],
        ['Gaspari Maria', 'Gaspari, Maria'],
        ['M Gaspari', 'Gaspari, Maria'],
        ['Maria Gaspari', 'Gaspari, Maria'],

        ['Sunje, Dallmeier-Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Suenje, Dallmeier-Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Sünje, Dallmeier-Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Sunje, Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Sünje, Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Suenje, Tiessen', 'Dallmeier-Tiessen, Sunje'],
        ['Sunje, Dallmeier', 'Dallmeier-Tiessen, Sunje'],
        ['Sünje, Dallmeier', 'Dallmeier-Tiessen, Sunje'],
        ['Suenje, Dallmeier', 'Dallmeier-Tiessen, Sunje'],
    ]
    for names in names_tests:
        demo_author_comparator(names, verbose=VERBOSE)
        if VERBOSE:
            print("_"*80)
