import time
import sys
import json
from pprint import pprint

import requests

USAGE = 'Usage: python -m scripts.active_tasks -i my.ini -p interval=5'
try:
    sys.path.append('lib')
    import TestInput
except ImportError:
    sys.exit(USAGE)


def collect_index_barriers(server):
    url = 'http://{0}:8092/_active_tasks'.format(server.ip)
    auth = (server.rest_username, server.rest_password)
    try:
        tasks = requests.get(url=url, auth=auth).json
    except requests.exceptions.ConnectionError:
        return

    main = filter(lambda t: t['type'] == 'couch_main_index_barrier', tasks)
    repl = filter(lambda t: t['type'] == 'couch_replica_index_barrier', tasks)

    return {
        'timestamp': time.time(),
        server.ip + '_running_couch_main_index_barrier': main[0]['running'],
        server.ip + '_waiting_couch_main_index_barrier': main[0]['waiting'],
        server.ip + '_running_couch_replica_index_barrier': repl[0]['running'],
        server.ip + '_waiting_couch_replica_index_barrier': repl[0]['waiting']
    }


def collect_couchdb_tasks(server):
    url = 'http://{0}:8092/_active_tasks'.format(server.ip)
    auth = (server.rest_username, server.rest_password)
    try:
        tasks = requests.get(url=url, auth=auth).json
    except requests.exceptions.ConnectionError:
        return

    get_id = lambda task: '_{0}_{1}_{2}_'.format(task.get('set', ''),
                                                 task['type'],
                                                 task.get('indexer_type', ''))

    samples = {'timestamp': time.time()}
    for metric in ('changes_done', 'total_changes', 'progress'):
        sample = dict(
            (server.ip + get_id(t) + metric, t.get(metric, None))
            for t in tasks
            if t['type'] in ('view_compaction', 'indexer')
        )
        samples.update(sample)
    return samples


def collect_active_tasks(server):
    url = 'http://{0}:8091/pools/default/tasks'.format(server.ip)
    auth = (server.rest_username, server.rest_password)
    try:
        tasks = requests.get(url=url, auth=auth).json
    except requests.exceptions.ConnectionError:
        return

    get_id = lambda task: '{0}_{1}{2}_'.format(task['type'],
                                               task.get('bucket', ''),
                                               task.get('designDocument', ''))

    samples = {'timestamp': time.time()}
    for metric in ('changesDone', 'totalChanges', 'progress'):
        sample = dict(
            (get_id(task) + metric, task.get(metric, None))
            for task in tasks
        )
        samples.update(sample)
    return samples


def main():
    try:
        input = TestInput.TestInputParser.get_test_input(sys.argv)
    except AttributeError:
        print USAGE
    else:
        all_samples = list()
        while True:
            try:
                samples =\
                    [collect_index_barriers(s) for s in input.servers] +\
                    [collect_couchdb_tasks(s) for s in input.servers] +\
                    [collect_active_tasks(input.servers[0])]
                samples = filter(lambda sample: sample, samples)
                all_samples.extend(samples)

                pprint(samples)
                time.sleep(input.param('interval', 5))
            except KeyboardInterrupt:
                break
        filename = 'active_tasks_{0}.json'\
            .format(time.strftime('%Y%m%d_%H%M', time.localtime(time.time())))
        with open(filename, 'w') as fh:
            print '\nSaving all stats to: {0}'.format(filename)
            fh.write(json.dumps(all_samples, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
