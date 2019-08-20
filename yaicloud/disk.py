from yaicloud.accounts import Account
from yaicloud.exceptions import DiskAuthError
import yadisk

class Disk:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.y = yadisk.YaDisk(app_id, app_secret)

    def login(self, account):
        url = self.y.get_code_url()
        r = account.session.get(url)

        csrf = r.html.xpath('//input[@name="csrf"]/@value')[0]
        request_id = r.html.xpath('//input[@name="request_id"]/@value')[0]
        data = {
            "granted_scopes": "cloud_api:disk.write",
            "granted_scopes": "cloud_api:disk.read",
            "granted_scopes": "cloud_api:disk.info",
            "granted_scopes": "cloud_api:disk.app_folder",
            "csrf": csrf,
            "response_type": "code",
            "redirect_uri": "https://httpstat.us/200",
            "request_id": request_id,
            "state": "",
            "retpath": "https://oauth.yandex.ru/authorize?response_type=code&client_id={}&display=popup&force_confirm=yes".format(self.app_id),
            "client_id": self.app_id,
            "device_id": "",
            "device_name": "",
            "display": "popup",
            "login_hint": "",
            "scope": "",
            "optional_scope": ""
        }

        allow_url = "https://oauth.yandex.ru/authorize/allow?response_type=code&client_id={}&display=popup&force_confirm=yes".format(self.app_id)
        r = account.session.post(allow_url, data)
        i = r.url.find('code=')
        code = r.url[i + len('code='):]

        try:
            response = self.y.get_token(code)
        except yadisk.exceptions.BadRequestError:
            raise DiskAuthError()

        self.y.token = response.access_token

        if not self.y.check_token():
            raise DiskAuthError()
