from graphite.intervals import Interval, IntervalSet
from graphite.logger import log
from graphite.node import BranchNode, LeafNode
from random import random
from time import localtime, time, strftime
import re


class TestFinder:
    # Metric tree
    tree = {
        'test-finder': {
            'level_1': {
                'level_a': {
                    'level_A': {},
                },
                'level_b': {
                    'level_A': {},
                    'level_B': {},
                },
                'level_c': {
                    'level_A': {},
                    'level_B': {},
                    'level_C': {},
                },
            },
            'level_2': {
                'level_a': {
                    'level_A': {},
                    'level_B': {},
                    'level_C': {},
                },
                'level_b': {
                    'level_A': {},
                    'level_B': {},
                },
                'level_c': {
                    'level_A': {},
                },
            },
        },
    }

    def find_nodes(self, query):
        # Get the part of tree described by the query
        struct = self.get_struct(query.pattern)

        # Build node
        for item in struct:
            if item['leaf']:
                yield LeafNode(item['id'], RandomReader(item['id']))
            else:
                yield BranchNode(item['id'])

    def get_struct(self, query):
        # Parse the query
        items = filter(None, query.split('.'))

        prev_paths = [items]
        records = []

        # Evaluate path
        while True:
            cur_paths = []
            cur_records = []

            for path in prev_paths:
                paths, records = self.eval_path(path)
                cur_paths += paths
                cur_records += records

            if prev_paths == cur_paths:
                # Take the last record information
                records = cur_records
                break
            else:
                prev_paths = cur_paths

        return records

    def eval_path(self, path):
        is_list = False
        is_wild = False
        is_valid = True

        # Create pointer to the first level
        pointer = self.tree

        # Check if there is some item to expand
        n = 0
        for item in path:
            if '{' in item:
                # Expand list
                is_list = True
                break
            elif '*' in item:
                # Expand wildcard
                is_wild = True
                break
            elif item not in pointer:
                is_valid = False
                break

            pointer = pointer[item]

            n += 1

        # This is where we store the result
        ret_path = []
        ret_record = []

        if is_list:
            # Create items from the list
            match = re.match('(.*){(.*)}(.*)', path[n])
            if match:
                groups = match.groups()
                lst = groups[1].split(',')

                for item in lst:
                    tmp = list(path)
                    tmp[n] = groups[0] + item + groups[2]
                    ret_path.append(tmp)
        elif is_wild:
            # Create items from the wildcard
            item = path[n].replace('*', '.*')
            pattern = re.compile(item)

            for key in sorted(pointer.keys()):
                if pattern.match(key):
                    tmp = list(path)
                    tmp[n] = key
                    ret_path.append(tmp)
        elif is_valid:
            # Check if it's a leaf
            has_children = int(bool(len(pointer.keys())))

            # Build the child record
            record = {
                'text': path[-1],
                'id': '.'.join(path),
                'allowChildren': has_children,
                'expandable': has_children,
                'leaf': int(not has_children),
            }

            ret_path = [path]
            ret_record = [record]

        return ret_path, ret_record


class RandomReader:
    # This recommended to save memory on readers
    __slots__ = ('path',)

    def __init__(self, path):
        log.info('===INIT===')
        log.info("path=%s" % path)
        self.path = path

    def fetch(self, start_time, end_time):
        log.info('===FETCH===')
        log.info("start=%s (%s); end=%s (%s)" % (
            start_time,
            strftime("%Y/%m/%d %T", localtime(start_time)),
            end_time,
            strftime("%Y/%m/%d %T", localtime(end_time))))

        # Data step
        data_step = 5

        # Time period definition
        data_from = start_time
        data_to = end_time

        # Generate data
        series = []
        for n in range(0, data_to - data_from):
            series.append(random())

        # Compile the time info set
        time_info = data_from, data_to, data_step

        return time_info, series

    def get_intervals(self):
        log.info('===GET_INTERVALS===')
        # We have data from the beginning of the epoch :o)
        start = 1
        # We can see one hour into the future :o)
        end = int(time()+3600)

        log.info("get_interval: start=%s; end=%s" % (start, end))

        return IntervalSet([Interval(start, end)])
