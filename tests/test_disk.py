# Run using: python -m pytest -s

from yaicloud.accounts import Account, AccountStorage
from yaicloud.disk import Disk
from yaicloud.info import *

s = AccountStorage()
r = s.get_registration_request()
print("\n" + "{0} PLEASE ENTER CAPTCHA {0}\n".format("=" * 29))
print(r.captcha_img_url)
code = input("Captcha: ")
errors = s.register(r, code)

assert len(errors) == 0, "Registration failed: {}".format(str(errors))
a = list(s.accounts.values())[0]

def test_disk_works():
    result = Disk.register_app(a)
    assert result is not None, "Failed to register yadisk app"
    app_id, app_secret = result

    d = Disk(app_id, app_secret)
    d.login(a)

    disk_info = d.y.get_disk_info()
    print(disk_info)
    assert disk_info, 'Disk info is not available'


if __name__ == '__main__':
    test_disk_works()
