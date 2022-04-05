# -*- coding: utf-8 -*-
# The DiverseSelector library provides a set of tools to select molecule
# subset with maximum molecular diversity.
#
# Copyright (C) 2022 The QC-Devs Community
#
# This file is part of DiverseSelector.
#
# DiverseSelector is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# DiverseSelector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

"""Dissimilarity based diversity subset selection."""

from DiverseSelector.base import SelectionBase
from DiverseSelector.metric import ComputeDistanceMatrix
import numpy as np

__all__ = [
    "DissimilaritySelection",
]


class DissimilaritySelection(SelectionBase):
    """Dissimilarity based diversity subset selection."""

    def __init__(self,
                 initialization="medoid",
                 metric="Tanimoto",
                 random_seed=42,
                 feature_type=None,
                 mol_file=None,
                 feature_file=None,
                 num_selected=None,
                 arr_dist=None,
                 **kwargs,
                 ):
        """Base class for dissimilarity based subset selection."""
        super().__init__(metric, random_seed, feature_type, mol_file, feature_file, num_selected)
        self.initialization = initialization
        self.arr_dist = arr_dist

        # super(DissimilaritySelection, self).__init__(**kwargs)
        self.__dict__.update(kwargs)

        # the initial compound index
        self.arr_dist, self.starting_idx = self.pick_initial_compounds()

    def pick_initial_compounds(self):
        """Pick the initial compounds."""
        # todo: current version only works for molecular descriptors
        # pair-wise distance matrix
        if self.arr_dist is None:
            dist_1 = ComputeDistanceMatrix(feature=self.features_norm,
                                           metric="euclidean")
            arr_dist_init = dist_1.compute_distance()

        # use the molecule with maximum distance to initial medoid as  the starting molecule
        if self.initialization.lower() == "medoid":
            # https://www.sciencedirect.com/science/article/abs/pii/S1093326399000145?via%3Dihub
            # J. Mol. Graphics Mod., 1998, Vol. 16,
            # DISSIM: A program for the analysis of chemical diversity
            medoid_idx = np.argmin(self.arr_dist.sum(axis=0))
            # selected molecule with maximum distance to medoid
            starting_idx = np.argmax(self.arr_dist[medoid_idx, :])
            arr_dist_init = self.arr_dist

        elif self.initialization.lower() == "random":
            rng = np.random.default_rng(self.random_seed)
            starting_idx = rng.choice(np.arange(self.features_norm.shape[0]), 1)
            arr_dist_init = self.arr_dist

        return arr_dist_init, starting_idx

    def compute_diversity(self):
        """Compute the distance metrics."""
        # for iterative selection and final subset both
        pass

    def select(self, selected=None):
        """Select the subset molecules with optimal diversity.

        Algorithm is adapted from https://doi.org/10.1016/S1093-3263(98)80008-9
        """
        if selected is None:
            selected = [self.starting_idx]
            return self.select(selected)

        # if we all selected all n_selected molecules then return list of selected mols
        if len(selected) == self.num_selected:
            return selected

        else:
            # calculate min distances from each mol to the selected mols
            min_distances = np.min(self.arr_dist[selected], axis=0)

            # find molecules distance minimal distance of which is the maximum among all
            new_id = np.argmax(min_distances)

            # add selected molecule to the selected list
            selected.append(new_id)

            # call method again with an updated list of selected molecules
            return self.select(selected)
