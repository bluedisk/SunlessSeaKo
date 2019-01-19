"""
utilities for make fetch or extract data from json
"""
import glob
import json
import os
from pprint import pprint

import hgtk
import tqdm

from sunless_web.models import Entry


def tracing(data, process, tree, pattern):
    """ tree tracing & processing """

    if isinstance(data, list):
        for idx, datum in enumerate(data):

            subtree = tree.copy()
            if isinstance(datum, dict):
                key = datum.get('Id', None)
                if not key:
                    key = datum.get('AreaId', None)
                if not key:
                    key = datum.get('QualityId', None)
                if not key:
                    key = datum.get('AssociatedQualityId', None)
                if not key:
                    key = datum.get('Order', None)
                if not key:
                    key = datum.get('Position', None)
                    if key:
                        key = ":".join(map(str, key.values()))
                if not key:
                    key = datum.get('SpawnName', None)
                if not key:
                    key = datum.get('Name', None)

                if not key or not hgtk.checker.is_latin1(str(key)):
                    pprint(tree)
                    pprint(datum)
                    pprint(key)
                    raise Exception()

                subtree.append(str(key))
            else:
                subtree.append(str(idx))

            subpattern = pattern.copy()
            subpattern.append('idx')
            data[idx] = tracing(datum, process, subtree, subpattern)

    elif isinstance(data, dict):
        for key, value in data.items():
            subtree = tree.copy()
            subtree.append(str(key))

            subpattern = pattern.copy()
            subpattern.append(str(key))

            data[key] = tracing(value, process, subtree, subpattern)

    elif isinstance(data, str):
        hash_v2 = Entry.make_hash("/".join(tree))
        return process(hash_v2, data)

    elif type(data) in (int, bool, float, type(None),):
        pass

    else:
        print("type error", type(data), tree)

    return data


def run_all(process, from_dir):
    """ check all items in json files under the target path"""

    result = {}
    for filename in tqdm.tqdm(glob.glob(from_dir + '/**/*.json', recursive=True)):
        basename = os.path.basename(filename)

        with open(filename) as data_file:
            data = json.load(data_file)

        cate, _ = os.path.splitext(basename)
        tracing(data, process, [cate], [cate])

        result[filename[len(from_dir):]] = data

        # if target_dir:
        #     target = filename.split('/')
        #     target[0] = target_dir
        #     target = "/".join(target)
        #
        #     os.makedirs(os.path.dirname(target), exist_ok=True)
        #
        #     with open(target, "w") as target_file:
        #         json.dump(data, target_file, ensure_ascii=False)

    return result
