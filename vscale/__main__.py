#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time

from api import Client

VSCALE_API_BASE_URL = 'https://api.vscale.io/v1/'
VSCALE_RESOURCES = ['account', 'scalets', 'backups', 'locations', 'images', 'rplans', 'sshkeys', 'billing']


def main():

    kwargs = {'vscale_dir': None }

    vs_api_token = None

    if os.path.exists(os.path.expanduser('~') + '/.vscale'):
        kwargs['vscale_dir'] = os.path.expanduser('~') + '/.vscale'

    if 'VSCALE_DIR' in os.environ:
        vscale_dir = os.environ['VSCALE_DIR']

    if 'VSCALE_API_TOKEN' in os.environ:
        vs_api_token = os.environ['VSCALE_API_TOKEN']

    VSCALE_DIR = kwargs.get('vscale_dir')

    import argparse

    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(help = 'available resources', dest = 'resource')

    subp_l = {}

    for resource in VSCALE_RESOURCES:
        subp_l[resource] = subparsers.add_parser(resource)

    # scalets

    scalets_sub = subp_l['scalets'].add_subparsers(help = 'scalets actions', dest = 'action')

    s_subs = {}

    # general operations

    for act in ['list', 'ls']:
        s_subs[act] = scalets_sub.add_parser(act, help = 'list scalets')
    for act in ['tasks', 'ps']:
        s_subs[act] = scalets_sub.add_parser(act, help = 'tasks scalets')
    for act in ['create', 'show', 'start', 'stop', 'restart', 'rebuild', 'delete', 'ssh']:
        s_subs[act] = scalets_sub.add_parser(act, help = '{0} scalets'.format(act))

    for act in ['show', 'start', 'stop', 'restart', 'rebuild', 'delete', 'ssh']:
        s_subs[act].add_argument('id', help = 'ctid or scalet name', action='store')

    # creation

    s_subs['create'].add_argument('-n', '--name', help = 'scalet name', action='store', dest='name', required = True)
    s_subs['create'].add_argument('-t', '--template', help = 'template name', dest = 'make_from', action='store', required = True)
    s_subs['create'].add_argument('-p', '--plan', help = 'plan name', dest = 'rplan', action='store', required = True)
    s_subs['create'].add_argument('-l', '--location', help = 'location name', dest = 'location', action='store', required = True)
    s_subs['create'].add_argument('-k', '--key', help = 'ssh key id', dest='keys', action='store', required = False)
    s_subs['create'].add_argument('-s', '--start', help = 'start after creation', action='store_true', dest='do_start', default = True)

    for act in ['create', 'start', 'stop', 'restart', 'rebuild', 'delete']:
        s_subs[act].add_argument('-b', '--batch', help = 'wait for task to complete', action='store_true', dest='batch', default = False)

    for act in ['create', 'start', 'restart', 'rebuild']:
        s_subs[act].add_argument('--ssh', help='start ssh after scalet operation', dest='ssh_start', action='store_true', default =False)

    # billing

    billing_sub = subp_l['billing'].add_subparsers(help = 'billing information', dest = 'info')

    billing_balance = billing_sub.add_parser('balance', help = 'show balance info')
    billing_payments = billing_sub.add_parser('payments', help = 'show payments info')
    billing_consumption = billing_sub.add_parser('consumption', help = 'show consumption info')
    billing_consumption.add_argument('-s', '--start', help='starting date, formatted YYYT-MM-DD', dest = 'start', action = 'store', required = True)
    billing_consumption.add_argument('-e', '--end', help='ending date, formatted YYYT-MM-DD', dest = 'end', action = 'store', required = True)

    args = argparser.parse_args()
    kwargs = args.__dict__

    # print kwargs

    def get_pretty_table(iterable, header):
        max_len = [len(x) for x in header]
        for row in iterable:
            row = [row] if type(row) not in (list, tuple) else row
            for index, col in enumerate(row):
                if max_len[index] < len(unicode(col)):
                    max_len[index] = len(unicode(col))
        output = ' ' + '-' * (sum(max_len) + 2 + int(len(header)*1.5) ) + '\n'
        output += '| ' + ''.join([h + ' ' * (l - len(h)) + '| ' for h, l in zip(header, max_len)]) + '\n'
        output += ' ' + '-' * (sum(max_len) + 2 + int(len(header)*1.5)) + '\n'
        for row in iterable:
            row = [row] if type(row) not in (list, tuple) else row
            output += '| ' + ''.join([unicode(c) + ' ' * (l - len(unicode(c))) + '| ' for c, l in zip(row, max_len)]) + '\n'
        output += ' ' + '-' * (sum(max_len) + 2 + int(len(header)*1.5)) + '\n'
        return output

    def scalet_by_name_id(vs, name_id):
        scalet = None

        is_name = False

        if not name_id.isdigit():
            is_name = True
        else:
            try:
                scalet = vs.scalets(name_id)
            except urllib2.HTTPError as e:
                if e.code != 404:
                    raise e

                # that means it probably name
                is_name = True
            else:
                is_name = False

        if is_name:
            scalets = vs.scalets()

            for s in scalets:
                if s['name'] == name_id:
                    scalet = s

        return scalet

    def start_ssh(vs, **kwargs):

        ip = kwargs.get('ip', None)
        ctid = kwargs.get('ctid', None)

        if ctid:
            s = vs.scalets(ctid)
            ip = s['public_address']['address']
        os.system('ssh %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l root' % ip)

    def wait_scalet_task(vs, **kwargs):
        ctid = int(kwargs.get('ctid'))
        s_task_exists = True

        while s_task_exists:
            tasks = vs.scalets_tasks()
            ctids = [ int(t['scalet']) for t in tasks ]
            if ctid not in ctids:
                s_task_exists = False
                break

            time.sleep(5)

    def save_cache(dir_path, resource, data):
        if dir_path is not None and os.path.exists(dir_path):
            with open('{0}/{1}'.format(dir_path, resource), 'w') as f:
                f.write(json.dumps(data))

    def load_cache(dir_path, resource):
        if os.path.exists('{0}/{1}'.format(dir_path, resource)):
            with open('{0}/{1}'.format(dir_path, resource), 'r') as f:
                return json.loads(f.read())

    def print_scalet(s):

        print '\n' + s['name'] + ': %s' % s['ctid']
        print get_pretty_table([[i, s[i].__str__()] for i in s], ['Attribute', 'Value'])

    def print_tasks(ts):
        if ts is not None and len(ts) > 0:
            print get_pretty_table([ t.values() for t in ts ], ts[0].keys())

    vs = Client(api_url = VSCALE_API_BASE_URL, api_token = vs_api_token)

    if kwargs['resource'] == 'account':
        info = vs[kwargs['resource']]['info']
        print get_pretty_table( [[i, info[i]] for i in info ], ['Attribute', 'Value'] )

    elif kwargs['resource'] not in ['billing', 'scalets', 'account']:
        rs = vs[kwargs['resource']]

        save_cache(VSCALE_DIR, kwargs['resource'], rs)

        if kwargs['resource'] in ['locations', 'images']:

            print get_pretty_table([[i['id'], i['active'], i['description'], ','.join(i['rplans'])] for i in rs], ['id','active','description','rplans'])
        elif kwargs['resource'] in ['rplans']:
            print get_pretty_table([[i['id'], i['disk'], i['memory'], i['cpus'],i['addresses'],','.join(i['locations'])] for i in rs], ['id','disk','memory','cpus','addresses','locations'])
        elif kwargs['resource'] in ['sshkeys']:
            print get_pretty_table([[i['id'], i['name'],i['key'][:50] + '..'] for i in rs], ['id','name','key'])

    elif kwargs['resource'] == 'billing':
        s = vs.billing(**kwargs)

        if kwargs['info'] == 'balance':
            print get_pretty_table([[i, s[i].__str__()] for i in s], ['Attribute', 'Value'])

        elif kwargs['info'] == 'payments':

            p = [ i.values() for i in s['items'] ]

            print get_pretty_table(p, s['items'][0].keys())

        elif kwargs['info'] == 'consumption':

            print get_pretty_table([[i, s[i]['summ']] for i in s], ['scalet id', 'summ'])

    elif kwargs['resource'] == 'scalets':

        if kwargs['action'] in ['ls', 'list']:
            scalets = vs.scalets()

            save_cache(VSCALE_DIR, 'scalets', scalets)

            for s in scalets:
                print_scalet(s)

        elif kwargs['action'] in ['start', 'stop', 'restart', 'rebuild', 'delete']:

            if 'ssh_start' not in kwargs:
                kwargs['ssh_start'] = False

            s = scalet_by_name_id(vs, kwargs['id'])

            if s:

                kwargs['ctid'] = s['ctid']
                func = vs.__getattribute__('scalets_{0}'.format(kwargs['action']))

                s = func(**kwargs)

                if kwargs['batch'] or kwargs['ssh_start']:
                    wait_scalet_task(vs, **s)

                print_scalet(s)

                if 'ssh_start' in kwargs and kwargs['ssh_start']:
                    start_ssh(vs, **{'ctid' : s['ctid']})

        elif kwargs['action'] == 'create':

            if 'keys' in kwargs and kwargs['keys'] is not None:
                kwargs['keys'] = [ int(i) for i in kwargs['keys'].split(',') ]

            s = vs.scalets_create(**kwargs)

            if kwargs['batch'] or kwargs['ssh_start']:
                wait_scalet_task(vs, **s)

            print_scalet(s)

            if kwargs['ssh_start']:
                start_ssh(vs, **{'ctid' : s['ctid']})

        elif kwargs['action'] == 'show':

            s = scalet_by_name_id(vs, kwargs['id'])

            if s:
                print_scalet(s)

        elif kwargs['action'] == 'ssh':

            s = scalet_by_name_id(vs, kwargs['id'])

            if s:
                start_ssh(vs, **s)

        elif kwargs['action'] in ['tasks', 'ps']:

            print_tasks(vs.scalets_tasks())


if __name__ == '__main__':

    kwargs = {'vscale_dir': None }

    api_token = None

    if os.path.exists(os.path.expanduser('~') + '/.vscale'):
        kwargs['vscale_dir'] = os.path.expanduser('~') + '/.vscale'

    if 'VSCALE_DIR' in os.environ:
        vscale_dir = os.environ['VSCALE_DIR']

    if 'VSCALE_API_TOKEN' in os.environ:
        api_token = os.environ['VSCALE_API_TOKEN']

    main(api_token, **kwargs)
