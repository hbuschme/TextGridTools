# -*- coding: utf-8 -*-

# Calculate various agreement measures.
# Copyright (C) 2012-2013 Marcin Włodarczak
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

from __future__ import division, print_function

import itertools
import re

import numpy as np

from .core import IntervalTier, PointTier, Time

# --------------
# Fleiss's kappa
# --------------


def fleiss_observed_agreement(a):
    '''Return the observed agreement for the input array.'''

    def per_subject_agreement(row):
        '''Return the observed agreement for the i-th subject.'''
        number_of_objects = np.sum(row)
        return (np.sum(np.square(row)) - number_of_objects) / (number_of_objects * (number_of_objects - 1))

    row_probabilities = np.apply_along_axis(per_subject_agreement, axis=1, arr=a)
    return np.mean(row_probabilities)


def fleiss_chance_agreement(a):
    '''Returns the chance agreement for the input array.'''

    def per_category_probabilities(a):
        '''The proportion of all assignments which were to the j-th category.'''
        cat_sums = np.sum(a, axis=0)
        return cat_sums / np.sum(cat_sums)

    return np.sum(np.square(per_category_probabilities(a)))


def fleiss_kappa(a):
    '''Calculates Fleiss's kappa for the input array (with categories
    in columns and items in rows).'''

    p = fleiss_observed_agreement(a)
    p_e = fleiss_chance_agreement(a)
    return (p - p_e) / (1 - p_e)

# -------------
# Cohen's kappa
# -------------


def cohen_kappa(a):
    '''Calculates Cohen's kappa for the input array.'''

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
    '''Calculates Scott's Pi for the input array.'''

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

def align_labels(tiers_list, regex=r'[^\s]+', precision=None):
    '''Create a list of lists for all time-aligned Interval
    or Point object in tiers_list, whose text matches regex.
    For example:

    [[label_1-tier_1, label_1-tier_2, label_1-tier_3],
     [label_2-tier_1, label_2-tier_2, label_2-tier_3],
     ...
     [label_n-tier_n, label_n-tier_n, label_n-tier_n]]

    The allowed mismatch between object's timestamps can be
    controlled via the precision parameter.
    '''

    # If precision is supplied, temporarily change
    # the value of Time._precision
    if precision is not None:
        precision_old = Time._precision
        Time._precision = precision

    if len(tiers_list) < 2:
        raise Exception('At least two Tier objects need to be provided.')
    # Check if all elements of tiers_list are either 
    # either PointTiers or IntervalTiers.
    elif (not (all([isinstance(x, IntervalTier) for x in tiers_list])
               or all([isinstance(x, PointTier) for x in tiers_list]))):
        raise TypeError('Only objects of types IntervalTier or PointTier can be aligned.')
    elif len(set([len(x) for x in tiers_list])) > 1:
        raise Exception('Input tiers differ in the number of objects.')

    labels_aligned = []
    for intervals in itertools.izip(*[x for x in tiers_list]):
        start_times = [x.start_time for x in intervals]
        end_times = [x.end_time for x in intervals]
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

    # Reset Time._precision to its original value
    if precision is not None:
        Time._precision = precision_old

    return labels_aligned

def cont_table(tiers_list, regex, precision):
    '''Produce a contingency table from annotations in tiers_list
    whose text matches regex, and whose time stamps are not
    misaligned by more than precision.
    '''

    labels_aligned = align_labels(tiers_list, regex, precision)

    # List of unique labels from both lists.
    categories = list(set(itertools.chain(*labels_aligned)))

    # A 2-by-2 array
    if len(labels_aligned[0]) == 2:
        categories_product = itertools.product(categories, categories)
        cont_table = np.array([labels_aligned.count(list(x)) for x in categories_product])
        cont_table.shape = (len(categories), len(categories))
    # An n-by-m array
    else:
        cont_table = np.array([x.count(y) for x in labels_aligned for y in categories])
        cont_table.shape = (len(labels_aligned), len(categories))
    return cont_table
