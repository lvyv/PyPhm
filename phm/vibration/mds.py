# Copyright 2021 The CASICloud Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

"""
=========================
Multi-dimensional scaling
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import pandas as pd
import numpy as np
from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA


def dev_age_compute(vectors, freqs, segment):
    """
    This function label all the frequence domain vectors.
    ----------
    vectors : array of frequency vectors
        Each vector in vectors is nd.array type in frequency domain.
        One device's vectors begin at good health condition and run to failue,
        and then followed by another device's vectors.
    freqs : array of frequency components of a vector
        This is often used as x axis values.
    segment: list
        The segment is a list that indicates which device the vectors belong to.
    Returns
    -------
    out: DataFrame object
        Dataframe's columns are frequency components, dev, and age.
    """
    df = pd.DataFrame(vectors, columns=freqs)

    devs = []
    for iii, devnums in enumerate(segment):
        devs = devs + [iii for idx in range(devnums)]
    df['dev'] = devs

    age_factor = 20
    ptsize = []
    for iii, devnums in enumerate(segment):
        ptsize = ptsize + list(range(devnums))
    ptsize = [(pt + 1) * age_factor for pt in ptsize]
    df['age'] = ptsize
    return df


def compute_mds_pos(vectors):
    similarities = euclidean_distances(vectors)
    # vecs = np.array([list(vec) for vec in vectors])
    mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9,
                       dissimilarity="precomputed", n_jobs=1)
    pos = mds.fit(similarities).embedding_

    # Rescale the data
    # pos *= np.sqrt((vecs ** 2).sum()) / np.sqrt((pos ** 2).sum())

    # Rotate the data
    clf = PCA(n_components=2)
    # vecs = clf.fit_transform(vecs)

    pos = clf.fit_transform(pos)
    return pos
