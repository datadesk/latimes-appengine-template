from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import SuspiciousOperation
from django.utils.cache import patch_vary_headers
import datetime

TEST_COOKIE_NAME = 'testcookie'
TEST_COOKIE_VALUE = 'worked'

class SessionWrapper(object):
    def __init__(self, session_key):
        self.session_key = session_key
        self.accessed = False
        self.modified = False

    def __contains__(self, key):
        return key in self._session

    def __getitem__(self, key):
        return self._session[key]

    def __setitem__(self, key, value):
        self._session[key] = value
        self.modified = True

    def __delitem__(self, key):
        del self._session[key]
        self.modified = True

    def keys(self):
        return self._session.keys()

    def items(self):
        return self._session.items()

    def get(self, key, default=None):
        return self._session.get(key, default)

    def set_test_cookie(self):
        self[TEST_COOKIE_NAME] = TEST_COOKIE_VALUE

    def test_cookie_worked(self):
        return self.get(TEST_COOKIE_NAME) == TEST_COOKIE_VALUE

    def delete_test_cookie(self):
        del self[TEST_COOKIE_NAME]

    def _get_session(self):
        # Lazily loads session from storage.
        self.accessed = True
        try:
            return self._session_cache
        except AttributeError:
            if self.session_key is None:
                self._session_cache = {}
            else:
                try:
                    s = Session.objects.get(session_key=self.session_key,
                        expire_date__gt=datetime.datetime.now())
                    self._session_cache = s.get_decoded()
                except (Session.DoesNotExist, SuspiciousOperation):
                    self._session_cache = {}
                    # Set the session_key to None to force creation of a new
                    # key, for extra security.
                    self.session_key = None
            return self._session_cache

    _session = property(_get_session)

class SessionMiddleware(object):
    def process_request(self, request):
        request.session = SessionWrapper(request.COOKIES.get(settings.SESSION_COOKIE_NAME, None))

    def process_response(self, request, response):
        # If request.session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.session_key:
                    session_key = request.session.session_key
                else:
                    obj = Session.objects.get_new_session_object()
                    session_key = obj.session_key

                if settings.SESSION_EXPIRE_AT_BROWSER_CLOSE:
                    max_age = None
                    expires = None
                else:
                    max_age = settings.SESSION_COOKIE_AGE
                    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
                new_session = Session.objects.save(session_key, request.session._session,
                    datetime.datetime.now() + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE))
                response.set_cookie(settings.SESSION_COOKIE_NAME, session_key,
                    max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE or None)
        return response
