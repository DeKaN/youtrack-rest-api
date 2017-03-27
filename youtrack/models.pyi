from datetime import datetime

import requests
from requests.auth import AuthBase
from typing import Dict, Any, Union, MutableMapping, Text, IO, TypeVar, Type, List, BinaryIO

from . import exceptions

codes_map: Dict[int, exceptions.YouTrackException] = ...

Params = Union[None, bytes, MutableMapping[Text, Text]]
Data = Union[None, bytes, MutableMapping[Text, Text], IO]


class YoutrackObject:
    _data: YO_Items = ...
    _connection: Connection = ...

    def __init__(self, data: Dict[str, Any] = {}, connection: Connection = None) -> None: ...

    def _update_data(self, data) -> None: ...

    def __getattr__(self, item: str) -> Any: ...

    def __setattr__(self, key: str, value: Any): ...

    def __getitem__(self, item: str): ...

    def __setitem__(self, key: str, value: Any): ...


YO = TypeVar('YO', bound=YoutrackObject)
YO_Item = Union[None, str, int, List[str], YO, List[YO]]
YO_Items = Dict[str, YO_Item]


class Connection:
    url: str = ...
    base_url: str = ...
    _session: requests.Session = ...

    def __init__(self, url: str, auth: AuthBase) -> None: ...

    @staticmethod
    def _check_response(response: requests.Response, *args: Any, **kwargs: Any) -> None: ...

    def _get(self, path: str, params: Params = None, **kwargs: Any) -> Dict[str, Any]: ...

    def _post(self, path: str, data: Data = None, params: Params = None, **kwargs: Any) -> Dict[
        str, Any]: ...

    def _put(self, path: str, data: Data = None, params: Params = None,
             **kwargs: Any) -> requests.Response: ...

    def _delete(self, path: str, **kwargs: Any): ...

    def _create_object(self, cls: Type[YO], data: Dict[str, Any]) -> YO: ...

    def _parse_issues_list(self, issues: List[YO_Items]) -> List[Issue]: ...

    def get_me(self) -> User: ...

    def get_user(self, username: str) -> User: ...

    def get_projects(self, verbose: bool = False) -> Dict[str, Project]: ...

    def get_issues_count(self, filters: str = '', retry_delay: int = 5,
                         wait_answer: bool = True) -> int: ...

    def get_project_issues(self, project_id: str, filters: List[str] = [], count: int = 10,
                           after: int = 0,
                           updated_after: datetime = None, wikify_desc: bool = False) -> List[
        Issue]: ...

    def get_issues(self, filters: List[str] = [], with_fields: List[str] = [], count: int = 10,
                   after: int = 0) -> \
            Union[List[Issue], Dict[str, Union[str, List[Issue]]]]: ...

    def get_issue(self, issue_id: str) -> Issue: ...

    def create_issue(self, project_id: str, summary: str, description: str = '',
                     attachments: Dict[str, BinaryIO] = {},
                     **kwargs: Any) -> requests.Response: ...

    def delete_issue(self, issue_id: str) -> requests.Response: ...

    def create_attachment(self, issue_id: str, filename: str, data: BinaryIO, author: str = None,
                          created: datetime = None, group: str = None) -> Attachment: ...

    def get_project(self, project_id: str) -> Project: ...


class Attachment(YoutrackObject):
    pass


class Comment(YoutrackObject):
    pass


class Link(YoutrackObject):
    pass


class User(YoutrackObject):
    pass


class Project(YoutrackObject):
    def get_issues(self, filters: List[str] = [], count: int = 10, after: int = 0,
                   updated_after: datetime = None,
                   wikify_desc: bool = False) -> List[Issue]: ...

    def create_issue(self, summary: str, description: str = '',
                     attachments: Dict[str, BinaryIO] = {},
                     **kwargs: Any) -> requests.Response: ...

    def get_issues_count(self, filters: str = '', retry_delay: int = 5,
                         wait_answer: bool = True) -> int: ...


class Issue(YoutrackObject):
    _fields_map: Dict[str, YO] = ...

    def __init__(self, data: Dict[str, Any] = {}, connection: Connection = None) -> None: ...

    def create_attachment(self, filename: str, data: BinaryIO, author: str = None,
                          created: datetime = None,
                          group: str = None) -> Attachment: ...
    def delete(self) -> requests.Response: ...
