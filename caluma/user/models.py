class AnonymousUser(object):
    def __init__(self):
        self.username = ""

    @property
    def is_authenticated(self):
        return False

    def __str__(self):
        return "AnonymousUser"


class OIDCUser(object):
    def __init__(self, jwt_token):
        self.username = jwt_token.get("sub", "")

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username
