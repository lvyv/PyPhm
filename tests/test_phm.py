#!/usr/bin/env python

"""Tests for `phm` package."""


import unittest
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from phm.modules import utils
from phm.vibration import cluster


class TestPhm(unittest.TestCase):
    """Tests for `phm` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        self.assertTrue(True)


# if __name__ == "__main__":
#     unittest.main()

mypath = '../../phm-model/hvac/data/'  # 'data/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# Set figure size for matplotlib
plt.rcParams['figure.figsize'] = [10, 8]
files = onlyfiles  # [0:6]

data = []
for file in files:
    x = utils.load_dat(file, mypath)
    # plt.plot(x[0])
    data.append(x[0])

sr = 20480  # sample rate
ws = 2048   # window size
freqs, spectra = cluster.ts2fft(data, sr, 2048)

cluster_, df = cluster.cluster_vectors(spectra, False)

fig, ax = plt.subplots()

ax.set_xlabel('Frequency')
ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
ax.set_title('Frequency Domain Representation of Each Signal')

for elem in spectra:
    ax.plot(freqs, elem)

plt.show()
# in order to show the age of different round trips.
# standard benchmark for rotation machine used to measure a new spectrum.
# 1st 0 - 27
# 2nd 28 - 39
# 3rd 40 - 91
# age_factor = 20
# pt_size = list(range(28)) + list(range(12)) + list(range(52))
# pt_size = [ (pt+1) * age_factor for pt in pt_size]
#
# fig2, ax2 = plt.subplots()
# # for spectra_id, color in enumerate(['red','blue','green','cyan', 'magenta', 'yellow']):
# categories = {}
# for spectra_id in np.unique(clusterer.labels_): #range(K_cnt): #enumerate([1,1'blue','green','cyan', 'magenta', 'yellow']):
#     mask = list(np.where(predictions==spectra_id)[0])
#     categories[spectra_id] = mask
#     for elem in mask:
#         ax2.plot(freqs, spectra[elem],  c=colormap[spectra_id], alpha=0.5, label=f'K{spectra_id}-{onlyfiles[elem]}') # color=f'C{spectra_id}',
# ax2.legend(ncol=3)
# ax2.set_xlabel('Frequency')
# ax2.set_ylabel('Frequency Domain (Spectrum) Magnitude')
# predictions

"""
=========================
Multi-dimensional scaling
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: BSD


print(__doc__)
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.collections import LineCollection

from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA

similarities = euclidean_distances(spectra)
vectors = np.array([list(vec) for vec in spectra])

mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9,
                   dissimilarity="precomputed", n_jobs=1)
pos = mds.fit(similarities).embedding_

# Rescale the data
pos *= np.sqrt((vectors ** 2).sum()) / np.sqrt((pos ** 2).sum())

# Rotate the data
clf = PCA(n_components=2)
vectors = clf.fit_transform(vectors)

pos = clf.fit_transform(pos)

fig = plt.figure(1)
ax = plt.axes([0., 0., 1., 1.])

plt.scatter(pos[:, 0], pos[:, 1], marker='.', edgecolors=colormap[predictions], s=pt_size, facecolors='none',
            lw=1)  # , label=predictions[:]) lw=0,

hnds = []
for idx in np.unique(clusterer.labels_):
    pop = mpatches.Patch(color=colormap[idx], label=f'Population:{idx}-{categories[idx]}')
    hnds.append(pop)
plt.legend(handles=hnds)


start_idx, end_idx = np.where(pos)
segments = [[vectors[ix, :], vectors[jy, :]]
            for ix in range(len(pos)) for jy in range(len(pos))]
values = np.abs(similarities)
lc = LineCollection(segments,
                    zorder=0, cmap=plt.cm.Blues,
                    norm=plt.Normalize(0, values.max()))
lc.set_array(similarities.flatten())
lc.set_linewidths(np.full(len(segments), 0.05))
ax.add_collection(lc)

plt.show()

"""
=========================
Predicting
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: BSD


print(__doc__)

import scipy.io
from os import listdir
from os.path import isfile, join

datumn = []

mypath = '../../phm-model/hvac/data/baseline/'  # 'data/baseline/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for i, item in enumerate(onlyfiles):
    file = item.split('.')[0]
    print(file)
    (de, fe) = load_mat(file, mypath)
    datumn.append(de)

mypath = '../../phm-model/hvac/data/fault/'  # 'data/fault/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for i, item in enumerate(onlyfiles):
    file = item.split('.')[0]
    print(file)
    (de, fe) = load_mat(file, mypath)
    datumn.append(de)


sr = 12000
spec = []

test_points = []

for idx,sig in enumerate(datumn):
    X = signal.welch(sig, fs=sr, scaling='density', nperseg=2048)
    test_points.append(np.abs(X[1]))

tps = np.array([  list(vec)    for vec in test_points])
# test_labels, strengths = hdbscan.approximate_predict(clusterer, tps)

import hdbscan

dat = np.array([  list(vec)    for vec in test_points])
clusterer = hdbscan.HDBSCAN(min_cluster_size=2, prediction_data=True).fit(dat)
predictions = clusterer.labels_

from sklearn import manifold
from sklearn.metrics import euclidean_distances

newpts = test_points

similarities = euclidean_distances(newpts)

mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9,
                   dissimilarity="precomputed", n_jobs=1)
pos = mds.fit(similarities).embedding_

