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
cluster module
=========================

An illustration of the rotation machine health model by viberation metric.
Common ultilities function.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import numpy as np
import pandas as pd
import hdbscan
from scipy import signal


def ts2fft(datumn, samplerate, nperseg):
    """
    This function computes all the one-dimensional time domain signals by FFT.
    Parameters
    ----------
    datumn : array of timeseries(list)
        Input signal is list array, list element contain many sample points
        in time domain.
    samplerate : int
        The sample rate of the input signals. All signals are assumed as the
        same sample rate.
    nperseg : int
        Axis over which to compute the FFT.  If not given, the last axis is
        used.
    Returns
    -------
    A tuple, `(frequencies, spectrumn_vectors)`
        The result of datumn transform by fft.
    Raises
    ------
    See Also
    --------
    Notes
    -----
    References
    ----------
    Examples
    --------
    >>>
    """
    fre = None
    spectrum_list = []
    # Because frequency domain is symmetrical, take only positive frequencies
    for idx, sig in enumerate(datumn):
        fre, amp = signal.welch(sig, fs=samplerate, scaling='density', nperseg=nperseg)
        spectrum_list.append(np.abs(amp))
    return fre, spectrum_list


def cluster_vectors(vectors, predict=True):
    """
    This function cluster all the frequence domain vectors.
    ----------
    vectors : array of frequency vectors
        Each vector in vectors is nd.array type in frequency domain.
    predict : bool, optional
        Determine cluster model could be used for prediction or not.
    Returns
    -------
    A tuple, `(clustermodel, dataframe)`
        Dataframe's columns are cluster id, color, vector indices.
    Raises
    ------
    See Also
    --------
    Notes
    -----
    References
    ----------
    Examples
    --------
    >>>
    """
    # 聚类数量和对应颜色空间
    # https://jdherman.github.io/colormap/
    # ['#35ffcc', '#7cdc66', '#c3b900', '#e15d61', '#ff00c3', '#df5ee1', '#bfbbff', '#7ddde0', '#000000']
    # The last color is set black for outliers.
    cm = np.array(['#ff003b', '#ef084d', '#de105f', '#ce1871', '#bd2084', '#ac2896', '#9b30a8', '#8b38ba', '#7c42ca',
                   '#7353d1', '#6b64d8', '#6375df', '#5a86e6', '#5297ed', '#4aa8f4', '#41b9fb', '#4abeef', '#63b5ce',
                   '#7cadad', '#95a48c', '#ae9b6b', '#c7934a', '#e08a29', '#f98208', '#e78005', '#c6800c', '#a58013',
                   '#84801b', '#638022', '#428029', '#218030', '#000000'])
    dat = np.array([list(vec) for vec in vectors])
    clusterer = hdbscan.HDBSCAN(min_cluster_size=6, prediction_data=predict).fit(dat)
    cids = np.unique(clusterer.labels_)
    labels = clusterer.labels_
    df = pd.DataFrame(cids, columns=['cid'])
    df['color'] = [cm[x] for x in cids]  # cluster count should not be two great.
    df['vectors'] = [list(np.where(labels == sid)[0]) for sid in cids]
    return clusterer, df