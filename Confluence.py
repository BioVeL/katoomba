import json
import requests
from requests.auth import HTTPBasicAuth

class Server:

    def __init__(self, hostname, username, password):
        self.confluenceBase = 'https://%s/rpc/json-rpc/confluenceservice-v2' % hostname

        self.params = dict(
            auth = HTTPBasicAuth(username, password),
            verify = False, # not yet setup to verify the server certificate
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
                }
            )

    def getPageId(self, space, title):
        response = requests.post(self.confluenceBase + '/getPage',
            data=json.dumps([space, title]), **self.params)
        response.raise_for_status()
        page = response.json()
        pageId = page['id']
        return pageId

    def publish(self, content, space, title, parentId):
        response = requests.post(self.confluenceBase + '/getPage',
            data=json.dumps([space, title]), **self.params)
        response.raise_for_status()
        page = response.json()
        if 'error' in page:
            code = page['error']['code']
            if code == 500:
                prevContent = None
                update = {
                    'space': space,
                    'title': title,
                    'content': content,
                    'parentId': parentId
                }
                pageUpdateOptions = dict(
                    versionComment = 'Triggered update',
                    minorEdit = False
                    )

                response = requests.post(self.confluenceBase + '/storePage',
                    data=json.dumps([update]), **self.params)
                response.raise_for_status()
                newPage = response.json()
                if 'error' in newPage:
                    raise RuntimeError(newPage['error']['message'])
            else:
                raise RuntimeError(page['error']['message'])
        else:
            prevContent = page['content']

            # Although Confluence documentation states that additional arguments are
            # ignored, updates fail unless we use the bare minimum of required arguments.
            update = {
                'id': page['id'],
                'space': page['space'],
                'title': page['title'],
                'content': content,
                'version': page['version'],
                'parentId': page['parentId']
            }
            pageUpdateOptions = dict(
                versionComment = 'Triggered update',
                minorEdit = False
                )

            response = requests.post(self.confluenceBase + '/storePage',
                data=json.dumps([update]), **self.params)
            response.raise_for_status()

            newPage = response.json()
            if 'error' in newPage:
                raise RuntimeError(newPage['error']['message'])
            assert 'content' in newPage, newPage
            newContent = newPage['content']