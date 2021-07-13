import os
import errno
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
from matplotlib import patches as mpatches
from datetime import datetime
from os import listdir
from os.path import isfile, join
from phm.modules import utils
from phm.vibration import cluster, mds
import unittest


def get_iot_data(iot, usr, pwd, entitytype, entityid, keys, st, et):
    try:
        url = f'http://{iot}/api/auth/login'
        data = f'''{{
             "username": "{usr}",
             "password": "{pwd}"
         }}'''
        response = requests.post(url, data=data)

        token = json.loads(response.text)['token']
        headers = {
            'X-Authorization': f'Bearer {token}'
        }

        url = f'http://{iot}/api/plugins/telemetry/{entitytype}/{entityid}/values/timeseries'
        payload = {
            'limit': '2500',
            'agg': 'NONE',
            'orderBy': 'ASC',
            'keys': f'{keys}',
            'startTs': f'{st}',
            'endTs': f'{et}'
        }
        response = requests.get(url, headers=headers, params=payload)
        datumn = json.loads(response.text)
        keys = list(datumn.keys())
        if len(keys) == 0:
            return None
        df1 = pd.DataFrame.from_dict(datumn['wave_url'])  # FIXME hardcode
        for key in keys:
            dfr = pd.DataFrame.from_dict(datumn[key])
            df1 = pd.merge(df1, dfr, on='ts', suffixes=['', key])
            df1 = df1.rename(columns={f'value{key}': key})
        return df1.drop(columns=['value'])
    except Exception as e:
        print(e)
        return None


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open_w(path):
    """
    Open "path" for writing, creating any parent directories as needed.

    """
    mkdir_p(os.path.dirname(path))
    return open(path, 'wb')


def retrieve_url_file(url, localfile):
    # print(url)
    r = requests.get(url)
    if r.status_code == 200:
        with safe_open_w(localfile) as f:
            f.write(r.content)
    return r.status_code


def fre2mds(url, benchpath, cachepath='.cache/data/'):
    """
    Determines soh according the given wave file.

    Parameters
    ----------
    url : string
        `url` is a .mat format file accessed by the given url.

    benchpath : string
        `benchpath` is something like ../phm-model/hvac/data/

    cachepath : string
        `localpath` is something like ./cache/data

    Returns
    -------
    out : float
        Float result of SOH calculated by the frequency analysis model.

    """
    sr = 20480  # sample rate
    ws = 2048  # window size

    # 1.read benchamark data files
    datumn = []
    mypath = benchpath
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    chunksize = 20480
    agelist = []
    for ii, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        (de, fe) = utils.load_dat(item, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.
    agelist = [28, 12, 52]  # FIXME: The benchmark datasets originally include three run to failure tests.
    objpos = len(datumn)    # This position should be used to plot object sample.
    print(f'1.Benchmark data read: {objpos}')

    # 2.download the dat file if necessary.
    fn = url.rsplit('/', 1)[-1]
    local = f'{cachepath}{fn}'
    if not os.path.exists(local):
        retrieve_url_file(url, local)

    # 3.read obj data files
    mypath = cachepath  # Obj data from url, cached in local .cache directory.
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for ii, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        (de, fe) = utils.load_dat(item, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.
    print(f'2.Total points(include obj ones): {len(datumn)}')

    # 4.fft and cluster

    frequencies, spectrum = cluster.ts2fft(datumn, sr, ws)
    clusternew_, dfnew = cluster.cluster_vectors(spectrum, False)

    df2 = mds.dev_age_compute(spectrum, frequencies, agelist)  # should label at data reading phase.seg
    pos = mds.compute_mds_pos(spectrum)

    # set color for each points in df2
    df2.loc[:, 'color'] = '#000000'
    for idx, elems in enumerate(dfnew['vectors']):
        for el in elems:
            df2.loc[el, 'color'] = dfnew.loc[idx, 'color']
    print(f'3.MDS pos computed.')

    # plot mds scatter chart
    plt.figure(1)
    plt.axes([0., 0., 1., 1.])
    # print(f'Total {len(agelist)} cnts samples loaded.')
    # collections = list(range(len(pos)))
    # mask = dfnew[dfnew['cid'] == -1]['vectors'][0]
    # dispindices = list(set(collections).difference(set(mask)))
    dispindices = list(range(objpos))  # only plot benchmark points.
    plt.scatter(x=pos[dispindices, 0],
                y=pos[dispindices, 1],
                s=df2.loc[dispindices, 'age'],
                label=df2.loc[dispindices, 'color'],
                edgecolors=df2.loc[dispindices, 'color'],
                facecolors='none', marker='.', alpha=0.5, lw=1)
    hnds = []
    for idx, el in enumerate(dfnew['color']):
        pop = mpatches.Patch(color=el, label=f'C: [{dfnew["cid"][idx]}], cnts:[{len(dfnew["vectors"][idx])}]')
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
    blcnts = 2
    baselineclass = [0]
    for idx, el in enumerate(agelist[0: blcnts]):
        ps = baselineclass[idx] + el
        baselineclass.append(ps)
    # find baselineclass leader points in dfnew and
    texts = []
    for obj in baselineclass:   # 0, 24, 36, 60
        for idx, vecs in enumerate(dfnew['vectors']):
            if obj in vecs:
                txt = f'{obj} in C: [{dfnew["cid"][idx]}]'
                texts.append(plt.text(pos[obj, 0], pos[obj, 1], txt))
    adjust_text(texts)
    # label object points
    plt.scatter(x=pos[objpos:, 0],
                y=pos[objpos:, 1],
                label=df2.loc[objpos:, 'color'],
                marker='*', s=300, color='k', alpha=0.5, lw=1)
    for txt in list(range(objpos, len(datumn))):
        plt.text(pos[txt, 0], pos[txt, 1], f'PT: {txt}', c='#000000')
    plt.show()
    print('4.MDS plot finished.')
    df2.drop(df2.columns[list(range(len(df2.T)-3))], axis=1, inplace=True)
    df2['pos_x'] = pos[:, 0]
    df2['pos_y'] = pos[:, 1]
    df2['shape'] = 0
    df2.loc[objpos:, 'shape'] = 1
    json.loads(df2.to_json())
    print('5.Return to main procedure.')
    return df2.to_json()    # return a valid json string


def wrap_mds(df, base):
    ret = []
    for index, row in df.iterrows():
        item = {"ts": row['ts'], "MDS": fre2mds(row[1], base)}
        ret.append(item)
    return ret


def calculate_mds_indicator(modelparam, bp):
    idx = None
    try:
        iot = modelparam['iot']
        usr = modelparam['usr']
        pwd = modelparam['pwd']
        entitytype = modelparam['entitytype']
        entityid = modelparam['entityid']
        keys = modelparam['keys']
        # st = '1 209 820 000 000' # 2008.05.03T21:06:40
        # et = '1 209 830 000 000'
        st = round(datetime.timestamp(datetime.strptime(modelparam['stime'], '%Y-%m-%dT%X')) * 1000)
        et = round(datetime.timestamp(datetime.strptime(modelparam['etime'], '%Y-%m-%dT%X')) * 1000)

        df = get_iot_data(iot, usr, pwd, entitytype, entityid, keys, st, et)

        if not (df is None):
            if modelparam['obj'] == 'MDS':
                idx = wrap_mds(df, bp)
    except ValueError as ve:
        print('Exception occured.', ve)
        pass
    return idx


def compute_mdsdata(benchpath, objpath):
    """
    Determines soh according the given wave file.

    Parameters
    ----------
    benchpath : string
        `benchpath` is a local path maintained that stores baseline data files.

    objpath : string
        `objpath` is a url to a csv file containing new spectrum samples.

    Returns
    -------
    out : DataFrame object
        Details information include cid, color, pos, age etc.
    """

    sr = 20480  # sample rate
    ws = 2048  # window size

    # 1.download the mat file if necessary.
    fn = objpath.rsplit('/', 1)[-1]
    cachepath = '.cache/data/'
    local = f'{cachepath}{fn}'
    if not os.path.exists(local):
        retrieve_url_file(objpath, local)

    # 2.read benchamark data files
    datumn = []
    mypath = benchpath
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    chunksize = 20480
    agelist = []
    for ii, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        (de, fe) = utils.load_dat(item, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.
    agelist = [28, 12, 52]  # FIXME: The benchmark datasets originally include three run to failure tests.
    objpos = len(datumn)    # This position should be used to plot object sample.
    print(f'Benchmark data read {objpos} cnts of points.')

    # 3.read obj data files
    mypath = cachepath  # Obj data from url, cached in local .cache directory.
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for ii, item in enumerate(onlyfiles):
        fractionlet = 0  # some segment is too short and should be drop out.
        (de, fe) = utils.load_dat(item, mypath)
        # segment by chunksize(default 20480)
        for idx, subset in enumerate(range(0, len(de), chunksize)):
            seg = de[subset: subset + chunksize]
            if len(seg) > ws:
                datumn.append(seg)
                fractionlet += 1
        agelist.append(fractionlet)  # each chunk contains idx+1 segments.
    print('Total points(include obj ones): ', len(datumn))

    # 4.fft and cluster

    frequencies, spectrum = cluster.ts2fft(datumn, sr, ws)
    clusternew_, dfnew = cluster.cluster_vectors(spectrum, False)

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
    print(f'Total {len(agelist)} cnts samples loaded.')
    # collections = list(range(len(pos)))
    # mask = dfnew[dfnew['cid'] == -1]['vectors'][0]
    # dispindices = list(set(collections).difference(set(mask)))
    dispindices = list(range(objpos))  # only plot benchmark points.
    plt.scatter(x=pos[dispindices, 0],
                y=pos[dispindices, 1],
                s=df2.loc[dispindices, 'age'],
                label=df2.loc[dispindices, 'color'],
                edgecolors=df2.loc[dispindices, 'color'],
                facecolors='none', marker='.', alpha=0.5, lw=1)
    hnds = []
    for idx, el in enumerate(dfnew['color']):
        pop = mpatches.Patch(color=el, label=f'C: [{dfnew["cid"][idx]}], cnts:[{len(dfnew["vectors"][idx])}]')
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
    blcnts = 2
    baselineclass = [0]
    for idx, el in enumerate(agelist[0: blcnts]):
        ps = baselineclass[idx] + el
        baselineclass.append(ps)
    # find baselineclass leader points in dfnew and
    texts = []
    for obj in baselineclass:   # 0, 24, 36, 60
        for idx, vecs in enumerate(dfnew['vectors']):
            if obj in vecs:
                txt = f'{obj} in C: [{dfnew["cid"][idx]}]'
                texts.append(plt.text(pos[obj, 0], pos[obj, 1], txt))
    adjust_text(texts)

    plt.scatter(x=pos[objpos:, 0],
                y=pos[objpos:, 1],
                label=df2.loc[objpos:, 'color'],
                marker='*', s=300, color='k', alpha=0.5, lw=1)

    for txt in list(range(objpos, len(datumn))):
        plt.text(pos[txt, 0], pos[txt, 1], f'Object {txt}', c='#000000')

    plt.show()
    print('---over---')

    return 1


class Tests(unittest.TestCase):
    def testCache(self):
        self.assert_(True)


if __name__ == "__main__":
    unittest.main()
