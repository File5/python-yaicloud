# Run using: python -m pytest -s

from yaicloud.accounts import Account, AccountStorage

s = AccountStorage()


def test_registration_works():
    r = s.get_registration_request()
    print("\n" + "{0} PLEASE ENTER CAPTCHA {0}\n".format("=" * 29))
    print(r.captcha_img_url)
    code = input("Captcha: ")
    errors = s.register(r, code)

    assert len(errors) == 0, "Registration failed: {}".format(str(errors))


def test_registration_errors():
    r = s.get_registration_request()
    print(r.captcha_img_url)
    r.session.get(r.captcha_img_url)
    code = "неправильнаякапча"
    print("Captcha:", code)
    errors = s.register(r, code)
    print(errors)
    assert len(errors) != 0, "No registration errors, but expected: 'Wrong captcha'"


if __name__ == '__main__':
    test_registration_errors()
