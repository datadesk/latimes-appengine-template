import inspect

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError

from regressiontests.views import BrokenException, except_args

class DebugViewTests(TestCase):
    def setUp(self):
        self.old_debug = settings.DEBUG
        settings.DEBUG = True
        self.old_template_debug = settings.TEMPLATE_DEBUG
        settings.TEMPLATE_DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_debug
        settings.TEMPLATE_DEBUG = self.old_template_debug

    def test_files(self):
        response = self.client.get('/views/raises/')
        self.assertEquals(response.status_code, 500)

        data = {
            'file_data.txt': SimpleUploadedFile('file_data.txt', 'haha'),
        }
        response = self.client.post('/views/raises/', data)
        self.assertTrue('file_data.txt' in response.content)
        self.assertFalse('haha' in response.content)

    def test_404(self):
        response = self.client.get('/views/raises404/')
        self.assertEquals(response.status_code, 404)

    def test_view_exceptions(self):
        for n in range(len(except_args)):
            self.assertRaises(BrokenException, self.client.get,
                reverse('view_exception', args=(n,)))

    def test_template_exceptions(self):
        for n in range(len(except_args)):
            try:
                self.client.get(reverse('template_exception', args=(n,)))
            except TemplateSyntaxError, e:
                raising_loc = inspect.trace()[-1][-2][0].strip()
                self.assertFalse(raising_loc.find('raise BrokenException') == -1,
                    "Failed to find 'raise BrokenException' in last frame of traceback, instead found: %s" %
                        raising_loc)

    def test_template_loader_postmortem(self):
        response = self.client.get(reverse('raises_template_does_not_exist'))
        self.assertContains(response, 'templates/i_dont_exist.html</code> (File does not exist)</li>', status_code=500)
