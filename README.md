YouTrack JSON REST API client library
======

Current implementation is compatible with Python 3 and YouTrack 2017.1 or higher.  
Authentication for old YouTrack versions will be realized later. 

Requirements
------
Python 3.4+

Examples
------
```python
from youtrack import Connection, TokenAuth

TOKEN = 'perm:XXXXXXXXXXX=.XXXXXXXXXXXXXXXXXX==.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
c = Connection('https://youtrack.gdsln.com/', TokenAuth(TOKEN))
```