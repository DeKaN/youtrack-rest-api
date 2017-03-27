import requests
import time

from . import exceptions

codes_map = {
    requests.codes.unauthorized: exceptions.UnauthorizedYouTrackException,
    requests.codes.forbidden: exceptions.ForbiddenYouTrackException,
    requests.codes.not_found: exceptions.NotFoundYouTrackException
}


class Connection:
    url = None
    base_url = None
    _session = None

    def __init__(self, url, auth):
        url = url.rstrip('/')
        self.url = url
        self.base_url = url + '/rest'
        self._session = requests.Session()
        self._session.hooks['response'].append(Connection._check_response)
        self._session.headers['Accept'] = 'application/json'
        self._session.auth = auth

    @staticmethod
    def _check_response(response, *args, **kwargs):
        if not response.ok:
            try:
                message = response.json().get('value')
            except (ValueError, KeyError):
                message = response.text or response.reason
            exc_class = codes_map.get(response.status_code, exceptions.YouTrackException)
            raise exc_class(message)

    def _get(self, path, params=None, **kwargs):
        return self._session.get(self.base_url + path, params=params, **kwargs).json()

    def _post(self, path, data=None, params=None, **kwargs):
        return self._session.post(self.base_url + path, data, params=params, **kwargs).json()

    def _put(self, path, data=None, params=None, **kwargs):
        return self._session.put(self.base_url + path, data, params=params, **kwargs)

    def _delete(self, path, **kwargs):
        return self._session.delete(self.base_url + path, **kwargs)

    def _create_object(self, cls, data):
        return cls(data, self)

    def _parse_issues_list(self, issues):
        return [self._create_object(Issue, x) for x in issues]

    def get_me(self):
        return self._create_object(User, self._get('/user/current'))

    def get_user(self, username):
        return self._create_object(User, self._get('/user/{}'.format(username)))

    def get_projects(self, verbose=False):
        params = {}
        if verbose:
            params['verbose'] = verbose
        projects = [self._create_object(Project, x) for x in self._get('/project/all', params)]
        return {p.shortName: p for p in projects}

    def get_issues_count(self, filters='', retry_delay=5, wait_answer=True):
        params = {
            'filter': filters,
        }
        result = -1
        for i in range(3):
            result = self._get('/issue/count', params).get('value', -1)
            if result != -1 or not wait_answer:
                return result
            time.sleep(retry_delay)
        else:
            return result

    def get_project_issues(self, project_id, filters=[], count=10, after=0, updated_after=None, wikify_desc=False):
        params = {
            'filter': filters,
            'max': count,
            'after': after,
            'wikifyDescription': wikify_desc
        }
        if updated_after:
            params['updatedAfter'] = updated_after.timestamp() * 1000
        return self._parse_issues_list(self._get('/issue/byproject/{}'.format(project_id), params))

    def get_issues(self, filters=[], with_fields=[], count=10, after=0):
        params = {
            'filter': filters,
            'max': count,
            'after': after
        }
        if with_fields:
            params['with'] = with_fields
        data = self._get('/issue', params)
        multi_search = filters and len(filters) > 1
        if not multi_search:
            return self._parse_issues_list(data['issue'])
        data = data['searchResult']
        for x in data:
            x['issues'] = self._parse_issues_list(x['issues'])
        return data

    def get_issue(self, issue_id):
        return self._create_object(Issue, self._get('/issue/{}'.format(issue_id)))

    def create_issue(self, project_id, summary, description='', attachments={}, **kwargs):
        params = {
            'project': project_id,
            'summary': summary,
            'description': description,
        }
        params.update(kwargs)
        req_kwargs = {}
        if attachments:
            req_kwargs['files'] = [('attachments', x) for x in attachments.items()]
        return self._put('/issue', params=params, **req_kwargs)

    def delete_issue(self, issue_id):
        return self._delete('/issue/{}'.format(issue_id))

    def create_attachment(self, issue_id, filename, data, author=None, created=None, group=None):
        params = {
            'group': group,
            'name': filename,
            'authorLogin': author,
        }
        if created:
            params['created'] = created.timestamp() * 1000
        return self._create_object(Attachment, self._post('/issue/{}/attachment'.format(issue_id), params=params,
                                                          files={filename: data}))

    def get_project(self, project_id):
        return self._create_object(Project, self._get('admin/project/{}'.format(project_id)))


class YoutrackObject:
    _data = None
    _connection = None
    _attribute_types = dict()

    def __init__(self, data={}, connection=None):
        self._data = dict()
        self._connection = connection
        if data:
            self._update_data(data)

    def _update_data(self, data):
        for k, v in data.items():
            if isinstance(v, list):
                data[k] = [x['value'] if isinstance(x, dict) else x for x in v]
        self._data.update(data)

    def __getattr__(self, item):
        return self._data[item]

    def __setattr__(self, key, value):
        if key in ('_data', '_connection', '_attribute_types'):
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value


class Attachment(YoutrackObject):
    pass


class Comment(YoutrackObject):
    pass


class Link(YoutrackObject):
    pass


class User(YoutrackObject):
    pass


class Project(YoutrackObject):
    def get_issues(self, filters=[], count=10, after=0, updated_after=None, wikify_desc=False):
        return self._connection.get_project_issues(self['shortName'], filters, count, after, updated_after, wikify_desc)

    def create_issue(self, summary, description='', attachments=None, permitted_group=None):
        return self._connection.create_issue(self['shortName'], summary, description, attachments, permitted_group)

    def get_issues_count(self, filters='', retry_delay=5, wait_answer=True):
        filters = filters or ''
        filters = 'project: {} {}'.format(self['shortName'], filters)
        return self._connection.get_issues_count(filters, retry_delay, wait_answer)


class Issue(YoutrackObject):
    _fields_map = {
        'attachments': Attachment,
        'comment': Comment,
        'links': Link,
    }

    def __init__(self, data={}, connection=None):
        data = data or {}
        data.update({x['name']: x['value'] for x in data.pop('field', [])})
        issue_items = {k: data.pop(k) for k in self._fields_map if k in data}
        super().__init__(data, connection)
        for k, v in issue_items.items():
            cls = self._fields_map[k]
            self[k] = [cls(x, connection) for x in v]

    def create_attachment(self, filename, data, author=None, created=None, group=None):
        return self._connection.create_attachment(self['id'], filename, data, author, created, group)

    def delete(self):
        return self._connection.delete_issue(self['id'])
