from graphite.intervals import Interval, IntervalSet
from graphite.logger import log
from graphite.node import BranchNode, LeafNode
from random import random
from time import localtime, time, strftime


class TestFinder:
    # Metric tree
    tree = {
        'test-finder': {
            'level1': {
                'level1_1': {
                    'level1_1_1': {},
                },
                'level1_2': {
                    'level1_2_1': {},
                    'level1_2_2': {},
                },
                'level1_3': {
                    'level1_3_1': {},
                    'level1_3_2': {},
                    'level1_3_3': {},
                },
            },
            'level2': {
                'level2_1': {
                    'level2_1_1': {},
                    'level2_2_2': {},
                    'level2_2_3': {},
                },
                'level2_2': {
                    'level2_2_1': {},
                    'level2_2_2': {},
                },
                'level2_3': {
                    'level2_3_1': {},
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
        path = filter(None, query.split('.'))
        # Create pointer to the first level
        pointer = self.tree

        # This is where we store the result
        ret = []

        # Indicates if it's the first level
        is_first = True
        # Indicates if the path is valid
        path_is_valid = False

        for item in path:
            if (
                    (item == '*' and (is_first or path_is_valid)) or
                    (
                        path_is_valid and item in pointer and
                        len(pointer[item].keys()) == 0)):

                # Create records for all children on this level
                for key in pointer.keys():
                    # Check if it's a leaf
                    has_children = int(bool(len(pointer[key].keys())))

                    # Create the record ID
                    rec_id = query
                    if query.endswith('*'):
                        rec_id = query.rstrip('*') + key

                    # Build the child record
                    record = {
                        'text': key,
                        'id': rec_id,
                        'allowChildren': has_children,
                        'expandable': has_children,
                        'leaf': int(not has_children),
                    }

                    # Append the child to the results
                    ret.append(record)
            elif item in pointer:
                pointer = pointer[item]
                path_is_valid = True

            # Invalidate the first flag
            is_first = False

        return ret


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

        data_step = 5
        data_from = start_time
        data_to = end_time

        series = []
        for n in range(0, data_to - data_from):
            series.append(random())

        # Compile the time info set
        time_info = data_from, data_to, data_step

        return time_info, series

    def get_intervals(self):
        log.info('===GET_INTERVALS===')
        # We have data for all the times ;o)
        start = 1
        end = int(time()+3600)

        log.info("get_interval: start=%s; end=%s" % (start, end))

        return IntervalSet([Interval(start, end)])
