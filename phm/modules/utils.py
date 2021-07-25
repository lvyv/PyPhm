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
Common module
=========================

An illustration of the rotation machine health model by viberation metric.
Common ultilities function.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import pandas as pd
import scipy.fftpack
import scipy.io


def load_mat(file, path):
    strf = f'{path}{file}'
    data = scipy.io.loadmat(strf)
    # fid = '{:0>3}'.format(file)  # 99 --> 099
    fileid = [int(si) for si in file.split('.') if si.isdigit()][0]  # xx.97.mat now changed to 97
    width = 3
    fid = f'{fileid:0{width}d}'  # 97 -> 097, and 100 -> 100
    de = data[f'X{fid}_DE_time']
    fe = data[f'X{fid}_FE_time']
    # drive end amplitude
    ampde = []
    for i in range(de.shape[0]):
        ampde.append(de[i][0])
    # fan end amplitude
    ampfe = []
    for i in range(fe.shape[0]):
        ampfe.append(fe[i][0])

    return ampde, ampfe


def load_csv(file, path, ns=['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']):
    strf = f'{path}{file}'
    df = pd.read_table(strf, names=ns)
    c1 = df.iloc[:, 0].values
    c2 = df.iloc[:, 1].values
    return c1, c2


def load_dat(file, path, ns=['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']):
    return load_csv(file, path, ns)
    # return load_mat(file, path)

