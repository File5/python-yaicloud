import time
from requests_html import HTMLSession
import random
import uuid
import string

from yaicloud import utils
from yaicloud.exceptions import RequestFailed, AccountInvalidError, AccountHackedError

class Account:
    def __init__(self, login, password, session=None):
        self.login = login
        self.password = password
        self._session = session

    @property
    def session(self):
        if self._session is None:
            self._session = HTMLSession()
            self._login()
        return self._session

    def _login(self):
        data = {
            "login": self.login,
            "passwd": self.password,
            "retpath": "",
        }
        r = self._session.post("https://passport.yandex.ru/auth", data)
        if not r.ok:
            raise RequestFailed()
        account_hacked_warning = r.html.xpath('//div[@data-reason="account_hacked_no_phone"]')
        utils.wait()
        if account_hacked_warning:
            raise AccountHackedError()
        if not self._check():
            raise AccountInvalidError()

    def _check(self):
        r = self.session.get('https://passport.yandex.ru/profile')
        utils.wait()
        if not r.ok:
            raise RequestFailed()
        first_name_div = r.html.xpath('//div[@class="personal-info__first"]')
        if len(first_name_div) < 1:
            return None
        first_name = first_name_div[0].text
        last_name = r.html.xpath('//div[@class="personal-info__last"]')[0].text
        return first_name + ' ' + last_name

    def __repr__(self):
        return "<Account '{}:{}'".format(self.login, self.password)

class AccountStorage:
    FIRST_NAMES = ["Boris", "Egor", "Gleb", "Mikhail", "Ivan", "Vladimir", "Stepan", "Petr", "Yuri"]
    LAST_NAMES = ["Ivanov", "Smirnov", "Kuznetsov", "Popov", "Petrov", "Sokolov", "Mikhailov"]

    class AccountRegistrationRequest:
        def __init__(self, session, track_id, captcha_key, captcha_img_url):
            self.session = session
            self.track_id = track_id
            self.captcha_key = captcha_key
            self.captcha_img_url = captcha_img_url

        def __repr__(self):
            return "<AccountRegistrationRequest captcha='{}'>".format(self.captcha_img_url)

    def __init__(self, first_name=None, last_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.accounts = {}

    def get_registration_request(self):
        new_session = HTMLSession()
        r = new_session.get('https://passport.yandex.ru/registration')

        track_id = r.html.xpath('//input[@name="track_id"]/@value')[0]
        captcha_key = r.html.xpath('//input[@name="captcha_key"]/@value')[0]
        captcha_img_url = r.html.xpath('//img[@class="captcha__image"]/@src')[0]

        return AccountStorage.AccountRegistrationRequest(new_session, track_id, captcha_key, captcha_img_url)

    def register(self, registration_request, captcha_code, login=None, password=None):
        if login is None:
            login = self._get_random_login()
        if password is None:
            password = self._get_random_password()
        if self.first_name is not None:
            first_name = self.first_name
        else:
            first_name = random.choice(self.FIRST_NAMES)
        if self.last_name is not None:
            last_name = self.last_name
        else:
            last_name = random.choice(self.LAST_NAMES)
        data = {
            "track_id": registration_request.track_id,
            "firstname": first_name,
            "lastname": last_name,
            "surname": "",
            "login": login,
            "password": password,
            "password_confirm": password,
            "hint_question_id": "12",
            "hint_answer": "Scrapy",
            "captcha": captcha_code,
            "captcha_key": registration_request.captcha_key,
            "validation_method": "captcha",
            "money_eula_accepted": "on",
            "eula_accepted": "on",
        }
        r = registration_request.session.post('https://passport.yandex.ru/registration', data)
        if not r.ok:
            raise RequestFailed()
        errors = r.html.xpath('//div[@class="error-message"]/text()')
        if errors:
            return list(map(lambda x: str(x), errors))
        self.accounts[login] = Account(login, password, session=registration_request.session)
        return []

    def add_account(self, login, password):
        self.accounts[login] = Account(login, password)

    def _get_random_login(self):
        return random.choice(string.ascii_letters) + str(uuid.uuid4()).replace('-', '')[3:]  # 30 characters, 1st is letter

    def _get_random_password(self, length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))
