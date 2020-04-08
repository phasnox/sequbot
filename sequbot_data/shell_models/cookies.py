from .core import BaseModel, Field, ReadOnlyArray
from http import cookiejar


@DeprecationWarning
class GoodCookie(BaseModel):
    version             =  Field()
    name                =  Field()
    value               =  Field()
    port                =  Field()
    port_specified      =  Field()
    domain              =  Field()
    domain_specified    =  Field()
    domain_initial_dot  =  Field()
    path                =  Field()
    path_specified      =  Field()
    secure              =  Field()
    expires             =  Field()
    discard             =  Field()
    comment             =  Field()
    comment_url         =  Field()
    _rest               =  Field()
    rfc2109             =  Field()

    @property
    def bad_cookie(self):
        return cookiejar.Cookie(self.version or 1, self.name, self.value, self.port,
                                self.port_specified, self.domain or '', self.domain_specified, 
                                self.domain_initial_dot, self.path, self.path_specified, 
                                self.secure, self.expires, self.discard, self.comment, 
                                self.comment_url, self._rest, self.rfc2109)

    @bad_cookie.setter
    def bad_cookie(self, bad_cookie):
        for key, value in vars(bad_cookie).items():
            if value:
                self.raw_object[key] = value


@DeprecationWarning
class Cookies(BaseModel):

    @property
    def cookiejar(self):
        good_cookies = self.raw_object
        cj = cookiejar.CookieJar()
        for gc in good_cookies:
            cj.set_cookie(GoodCookie(raw_object=gc).bad_cookie)
        return cj

    @cookiejar.setter
    def cookiejar(self, cj):
        good_cookies = self.raw_object = []
        for bad_cookie in cj:
            good_cookie = GoodCookie()
            good_cookie.bad_cookie = bad_cookie
            good_cookies.append(good_cookie.raw_object)
