#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Calculate various agreement measures.
# Copyright (C) 2012 Marcin Włodarczak
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import itertools
import numpy as np
import re
import tgt

# --------------
# Fleiss's kappa
# --------------


def fleiss_observed_agreement(a):
    """Return the observed agreement for the input array."""

    def per_subject_agreement(row):
        """Return the observed agreement for the i-th subject."""
        number_of_objects = np.sum(row)
        return (np.sum(np.square(row)) - number_of_objects) / (number_of_objects * (number_of_objects - 1))

    row_probabilities = np.apply_along_axis(per_subject_agreement, axis=1, arr=a)
    return np.mean(row_probabilities)


def fleiss_chance_agreement(a):
    """Returns the chance agreement for the input array."""

    def per_category_probabilities(a):
        """The proportion of all assignments which were to the j-th category."""
        cat_sums = np.sum(a, axis=0)
        return cat_sums / np.sum(cat_sums)

    return np.sum(np.square(per_category_probabilities(a)))


def fleiss_kappa(a):
    """Calculates Fleiss's kappa for the input array (with categories
    in columns and items in rows)."""

    p = fleiss_observed_agreement(a)
    p_e = fleiss_chance_agreement(a)
    return (p - p_e) / (1 - p_e)

# -------------
# Cohen's kappa
# -------------


def cohen_kappa(a):
    """Calculates Cohen's kappa for the input array."""

    totsum = np.sum(a)
    colsums = np.sum(a, 0)
    rowsums = np.sum(a, 1)
    # Observed agreement.
    p = np.sum(np.diagonal(a)) / totsum
    # Chance agreement.
    p_e = np.sum((colsums * rowsums) / totsum ** 2)
    return (p - p_e) / (1 - p_e)

# ----------
# Scott's pi
# ----------


def scott_pi(a):
    """Calculates Scott's Pi for the input array."""

    totsum = np.sum(a)
    colsums = np.sum(a, 0)
    rowsums = np.sum(a, 1)
    # Observed agreement.
    p = np.sum(np.diagonal(a)) / totsum
    # Chance agreement.
    joint_marginal_props = (colsums + rowsums) / (2 * totsum)
    p_e = np.sum(joint_marginal_props ** 2)
    return (p - p_e) / (1 - p_e)

# ----------------------------------------------------------
# Functions producing contingency tables from lists of labels
# ----------------------------------------------------------


def two_raters_table(l):
    """Returns a contingency matrix for two raters given a list of
    time-aligned labels."""

    sublists_lengths = [len(x) for x in l]
    if any([x != 2 for x in sublists_lengths]):
        raise Exception('The length of sublists must be equal to 2')
    if sublists_lengths.count(sublists_lengths[0]) != len(sublists_lengths):
        raise Exception('The lengths of sublists differ.')
    # List of unique labels from both lists.
    categories = list(set(itertools.chain(*l)))
    cont_table = np.array([l.count(list(x)) for x in itertools.product(categories, categories)])
    print(cont_table)
    cont_table.shape = (len(categories), len(categories))
    return cont_table

def n_raters_table(l):
    """Returns a contingency matrix for n >= 2 raters (with categories
    in columns and items in rows) given a list of time-aligned labels."""

    sublists_lengths = [len(x) for x in l]
    if any([x < 2 for x in sublists_lengths]):
        raise Exception('The length of sublists must be at least 2')
    if sublists_lengths.count(sublists_lengths[0]) != len(sublists_lengths):
        raise Exception('The lengths of sublists differ')
    # List of unique labels from all lists.
    categories = list(set(itertools.chain(*l)))
    cont_table = np.array([x.count(y) for x in l for y in categories])
    cont_table.shape = (len(l), len(categories))
    return cont_table

def produce_aligned_labels_lists(tiers_list, regex=r'[^\s]+'):
    '''Creates a list of lists of labels matching the specified
    regular expression from time-aligned intervals or points
    in the input interval tiers.'''

    if not tiers_list:
        raise Exception('The input list is empty.')
    # Check if all elements of tiers_list are either 
    # either PointTiers or IntervalTiers.
    elif (not (all([isinstance(x, tgt.IntervalTier) for x in tiers_list])
               or all([isinstance(x, tgt.PointTier) for x in tiers_list]))):
        raise TypeError('Only objects of types IntervalTier or PointTier can be aligned.')
    elif len(set([len(x) for x in tiers_list])) > 1:
        raise Exception('Input tiers differ in the number of objects.')

    labels_aligned = []
    for intervals in itertools.izip(*[x for x in tiers_list]):
        start_times = [x.start_time for x in intervals]
        end_times = [x.end_time for x in intervals]
        labels = [x.text for x in intervals]
        if any([not re.search(regex, x) for x in labels]):
            # Only go on if labels of all intervals match the regular expression.
            continue
        # Check if start and end times match.
        elif start_times.count(start_times[0]) != len(start_times):
            raise Exception('Objects\' time stamps do not match: {0}'.format(start_times))
        elif end_times.count(end_times[0]) != len(end_times):
            raise Exception('Objects\' time stamps do not match: {0}'.format(end_times))
        else:
            labels_aligned.append([x.text for x in intervals])
    return labels_aligned
