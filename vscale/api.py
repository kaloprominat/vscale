#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2


class Client(object):

    """docstring for Vscale"""

    VSCALE_API_BASE_URL = 'https://api.vscale.io/v1/'

    def __init__(self, api_token=None, api_url=VSCALE_API_BASE_URL):

        super(Client, self).__init__()
        self.api_url = api_url
        self.api_token = api_token

    def _http_req(self, url, method='GET', data=None):

        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(url, data=data)
        request.add_header('X-Token', self.api_token)

        if data is not None:
            request.add_header("Content-Type", 'application/json;charset=UTF-8')

        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            print e
            raise e
        result = None
        result = connection.read()

        return result

    def _http_req_resource(self, resource, **kwargs):
        url = self.api_url + resource
        return self._http_req(url, **kwargs)

    def _get_json_resource(self, resource, **kwargs):
        res = self._http_req_resource(resource, **kwargs)
        return json.loads(res)

    def __getitem__(self, key):
        return self._get_json_resource(key)

# general accessors

    def account(self):
        return self['account']

    def scalets(self, ctid=None):
        return self['scalets'] if ctid is None else self['scalets/{0}'.format(ctid)]

    def rplans(self):
        return self['rplans']

    def images(self):
        return self['images']

    def locations(self):
        return self['locations']

    def tasks(self):
        return self['tasks']

    def sshkeys(self):
        return self['sshkeys']

    def billing(self, **kwargs):
        if kwargs.get('info') != 'consumption':
            return self._get_json_resource('billing/{info}'.format(**kwargs))

        return self._get_json_resource('billing/{info}?start={start}&end={end}'.format(**kwargs))

# scalets operations

    def scalets_create(self, **kwargs):
        ckwargs = {}
        for i in ['name', 'make_from', 'rplan', 'do_start', 'location', 'keys']:
            if i in kwargs:
                ckwargs[i] = kwargs[i]

        if 'keys' not in ckwargs or ckwargs['keys'] is None:
            sshkeys = self['sshkeys']
            if len(sshkeys) > 0:
                ckwargs['keys'] = [ i['id'] for i in sshkeys]

        try:
            scalet = self._get_json_resource('scalets', **{'method': 'POST', 'data': json.dumps(ckwargs)})
        except urllib2.HTTPError as e:
            print e
            raise e
        return scalet

    def scalets_start(self, **kwargs):

        return self._get_json_resource('scalets/{0}/start'.format(kwargs['ctid']), **{'method':'PATCH', 'data': json.dumps({'id': str(kwargs.get('ctid'))})})

    def scalets_stop(self, **kwargs):

        return self._get_json_resource('scalets/{0}/stop'.format(kwargs['ctid']), **{'method':'PATCH', 'data': json.dumps({'id': str(kwargs.get('ctid'))})})

    def scalets_restart(self, **kwargs):

        return self._get_json_resource('scalets/{0}/restart'.format(kwargs['ctid']), **{'method':'PATCH', 'data': json.dumps({'id': str(kwargs.get('ctid'))})})

    def scalets_rebuild(self, **kwargs):

        return self._get_json_resource('scalets/{0}/rebuild'.format(kwargs['ctid']), **{'method':'PATCH'})

    def scalets_delete(self, **kwargs):

        return self._get_json_resource('scalets/{0}'.format(kwargs['ctid']), **{'method': 'DELETE'})

    def scalets_tasks(self, **kwargs):
        return self._get_json_resource('tasks')
