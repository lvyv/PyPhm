#!/usr/bin/env python

"""Tests for `phm` package."""


import unittest
import matplotlib.pyplot as plt
from adjustText import adjust_text
from matplotlib import patches as mpatches
from os import listdir
from os.path import isfile, join
from phm.modules import utils
from phm.vibration import cluster, mds


class TestPhm(unittest.TestCase):
    """Tests for `phm` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        self.assertTrue(True)


def analysis_ims():
    mypath = '../../phm-model/hvac/data/'  # 'data/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # Set figure size for matplotlib
    plt.rcParams['figure.figsize'] = [12, 6]
    files = onlyfiles  # [0:6]

    data = []
    for file in files:
        x = utils.load_dat(file, mypath)
        data.append(x[0])

    sr = 20480  # sample rate
    ws = 2048  # window size
    freqs, spectra = cluster.ts2fft(data, sr, ws)
    cluster_, df = cluster.cluster_vectors(spectra, False)

    # plot frequencies cluster chart
    fig, ax = plt.subplots()
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
    ax.set_title('Frequency Domain Representation of Each Signal')
    for idx, elem in enumerate(df['vectors']):
        for el in elem:
            ax.plot(freqs, spectra[el], c=df['color'][idx])
    plt.show()

    df2 = mds.dev_age_compute(spectra, freqs, [28, 12, 52])
    pos = mds.compute_mds_pos(spectra)
    # set color for each points in df2
    df2.loc[:, 'color'] = '#000000'
    for idx, elems in enumerate(df['vectors']):
        for el in elems:
            df2.loc[el, 'color'] = df.loc[idx, 'color']

    # plot mds scatter chart
    plt.figure(1)
    plt.axes([0., 0., 1., 1.])
    plt.scatter(pos[:, 0], pos[:, 1], marker='.', edgecolors=df2.loc[:, 'color'], s=df2.loc[:, 'age'],
                facecolors='none',
                alpha=0.5, lw=1, label=df2.loc[:, 'color'])
    hnds = []
    for idx, el in enumerate(df['color']):
        pop = mpatches.Patch(color=el, label=f'cluster:{df["cid"][idx]}, {df["vectors"][idx]}')
        hnds.append(pop)
    plt.legend(handles=hnds, prop={'size': 6})
    txts = df[df['cid'] == -1]['vectors'][0]  # -1 point.
    texts = [plt.text(pos[txt, 0], pos[txt, 1], txt) for txt in txts]
    adjust_text(texts)
    plt.show()
    return


def analysis_cwru():
    print('---start---')
    sr = 12000
    ws = 2048

    datumn = []
    mypath = '../../phm-model/hvac/data/baseline/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    chunksize = 20480
    agelist = []
    for i, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        file = item.split('.')[0]
        (de, fe) = utils.load_mat(file, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.
    print(f'Total {len(datumn)} cnts of health points loaded.')

    mypath = '../../phm-model/hvac/data/fault/'  # 'data/fault/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for i, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        file = item.split('.')[0]
        (de, fe) = utils.load_mat(file, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.

    print('Total points(include health ones): ', len(datumn))

    frequencies, spectrum = cluster.ts2fft(datumn, sr, ws)
    clusternew_, dfnew = cluster.cluster_vectors(spectrum, False)

    # plot frequencies cluster chart
    fig, ax = plt.subplots()
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
    ax.set_title('Frequency Domain Representation of Each Signal')
    for idx, elem in enumerate(dfnew['vectors']):
        for el in elem:
            ax.plot(frequencies, spectrum[el], c=dfnew['color'][idx])
    plt.show()

    df2 = mds.dev_age_compute(spectrum, frequencies, agelist)  # should label at data reading phase.seg
    pos = mds.compute_mds_pos(spectrum)

    print(f'MDS pos computed.')

    # set color for each points in df2
    df2.loc[:, 'color'] = '#000000'
    for idx, elems in enumerate(dfnew['vectors']):
        for el in elems:
            df2.loc[el, 'color'] = dfnew.loc[idx, 'color']

    # plot mds scatter chart
    plt.figure(1)
    plt.axes([0., 0., 1., 1.])
    print(f'Total {len(agelist)} cnts of health points loaded.')
    collections = list(range(len(pos)))
    mask = dfnew[dfnew['cid'] == -1]['vectors'][0]
    dispindices = list(set(collections).difference(set(mask)))
    plt.scatter(x=pos[dispindices, 0],
                y=pos[dispindices, 1],
                s=df2.loc[dispindices, 'age'],
                label=df2.loc[dispindices, 'color'],
                edgecolors=df2.loc[dispindices, 'color'],
                facecolors='none', marker='.', alpha=0.5, lw=1)
    hnds = []
    for idx, el in enumerate(dfnew['color']):
        pop = mpatches.Patch(color=el, label=f'cluster:{dfnew["cid"][idx]}, {len(dfnew["vectors"][idx])}')
        hnds.append(pop)
    plt.legend(handles=hnds, prop={'size': 6})
    # label baseline points
    # baseline should be the first points
    # agelist = [24, 12, 24, 24, 6, ...]
    # dfnew:
    #       cid,       vectors
    #        -1     [84,85,86,87, ...]
    #         0     [156,157, ...]
    #        ...
    #         8     [0,1,2, ...]
    # should label points: 0, 24, 36, 60
    blcnts = 3
    baselineclass = [0]
    for idx, el in enumerate(agelist[0: blcnts]):
        ps = baselineclass[idx] + el
        baselineclass.append(ps)
    # find baselineclass leader points in dfnew and
    texts = []
    for obj in baselineclass:   # 0, 24, 36, 60
        for idx, vecs in enumerate(dfnew['vectors']):
            if obj in vecs:
                txt = dfnew['cid'][idx]
                texts.append(plt.text(pos[obj, 0], pos[obj, 1], txt))
    adjust_text(texts)
    # try:
    #     txts = dfnew[dfnew['cid'] == -1]['vectors'][0]  # -1 point.
    #     texts = [plt.text(pos[txt, 0], pos[txt, 1], txt) for txt in txts]
    #     adjust_text(texts)
    # except KeyError as ke:
    #     print(ke)
    #     pass
    plt.show()
    print('---over---')


if __name__ == "__main__":
    # unittest.main()
    # analysis_ims()
    analysis_cwru()
