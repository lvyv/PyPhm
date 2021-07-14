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
Cluster and fft functions.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import logging
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
    return


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
    return
