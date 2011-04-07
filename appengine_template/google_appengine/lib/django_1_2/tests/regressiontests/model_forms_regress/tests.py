from datetime import date

from django import db, forms
from django.conf import settings
from django.forms.models import modelform_factory, ModelChoiceField
from django.test import TestCase

from models import Person, RealPerson, Triple, FilePathModel, Article, \
    Publication, CustomFF, Author, Author1, Homepage


class ModelMultipleChoiceFieldTests(TestCase):

    def setUp(self):
        self.old_debug = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_debug

    def test_model_multiple_choice_number_of_queries(self):
        """
        Test that ModelMultipleChoiceField does O(1) queries instead of
        O(n) (#10156).
        """
        for i in range(30):
            Person.objects.create(name="Person %s" % i)

        db.reset_queries()
        f = forms.ModelMultipleChoiceField(queryset=Person.objects.all())
        selected = f.clean([1, 3, 5, 7, 9])
        self.assertEquals(len(db.connection.queries), 1)

    def test_model_multiple_choice_run_validators(self):
        """
        Test that ModelMultipleChoiceField run given validators (#14144).
        """
        for i in range(30):
            Person.objects.create(name="Person %s" % i)

        self._validator_run = False
        def my_validator(value):
            self._validator_run = True

        f = forms.ModelMultipleChoiceField(queryset=Person.objects.all(),
                                           validators=[my_validator])

        f.clean([p.pk for p in Person.objects.all()[8:9]])
        self.assertTrue(self._validator_run)

class TripleForm(forms.ModelForm):
    class Meta:
        model = Triple

class UniqueTogetherTests(TestCase):
    def test_multiple_field_unique_together(self):
        """
        When the same field is involved in multiple unique_together
        constraints, we need to make sure we don't remove the data for it
        before doing all the validation checking (not just failing after
        the first one).
        """
        Triple.objects.create(left=1, middle=2, right=3)

        form = TripleForm({'left': '1', 'middle': '2', 'right': '3'})
        self.assertFalse(form.is_valid())

        form = TripleForm({'left': '1', 'middle': '3', 'right': '1'})
        self.assertTrue(form.is_valid())

class TripleFormWithCleanOverride(forms.ModelForm):
    class Meta:
        model = Triple

    def clean(self):
        if not self.cleaned_data['left'] == self.cleaned_data['right']:
            raise forms.ValidationError('Left and right should be equal')
        return self.cleaned_data

class OverrideCleanTests(TestCase):
    def test_override_clean(self):
        """
        Regression for #12596: Calling super from ModelForm.clean() should be
        optional.
        """
        form = TripleFormWithCleanOverride({'left': 1, 'middle': 2, 'right': 1})
        self.assertTrue(form.is_valid())
        # form.instance.left will be None if the instance was not constructed
        # by form.full_clean().
        self.assertEquals(form.instance.left, 1)

# Regression test for #12960.
# Make sure the cleaned_data returned from ModelForm.clean() is applied to the
# model instance.

class PublicationForm(forms.ModelForm):
    def clean(self):
        self.cleaned_data['title'] = self.cleaned_data['title'].upper()
        return self.cleaned_data

    class Meta:
        model = Publication

class ModelFormCleanTest(TestCase):
    def test_model_form_clean_applies_to_model(self):
        data = {'title': 'test', 'date_published': '2010-2-25'}
        form = PublicationForm(data)
        publication = form.save()
        self.assertEqual(publication.title, 'TEST')

class FPForm(forms.ModelForm):
    class Meta:
        model = FilePathModel

class FilePathFieldTests(TestCase):
    def test_file_path_field_blank(self):
        """
        Regression test for #8842: FilePathField(blank=True)
        """
        form = FPForm()
        names = [p[1] for p in form['path'].field.choices]
        names.sort()
        self.assertEqual(names, ['---------', '__init__.py', 'models.py', 'tests.py'])

class ManyToManyCallableInitialTests(TestCase):
    def test_callable(self):
        "Regression for #10349: A callable can be provided as the initial value for an m2m field"

        # Set up a callable initial value
        def formfield_for_dbfield(db_field, **kwargs):
            if db_field.name == 'publications':
                kwargs['initial'] = lambda: Publication.objects.all().order_by('date_published')[:2]
            return db_field.formfield(**kwargs)

        # Set up some Publications to use as data
        Publication(title="First Book", date_published=date(2007,1,1)).save()
        Publication(title="Second Book", date_published=date(2008,1,1)).save()
        Publication(title="Third Book", date_published=date(2009,1,1)).save()

        # Create a ModelForm, instantiate it, and check that the output is as expected
        ModelForm = modelform_factory(Article, formfield_callback=formfield_for_dbfield)
        form = ModelForm()
        self.assertEquals(form.as_ul(), u"""<li><label for="id_headline">Headline:</label> <input id="id_headline" type="text" name="headline" maxlength="100" /></li>
<li><label for="id_publications">Publications:</label> <select multiple="multiple" name="publications" id="id_publications">
<option value="1" selected="selected">First Book</option>
<option value="2" selected="selected">Second Book</option>
<option value="3">Third Book</option>
</select>  Hold down "Control", or "Command" on a Mac, to select more than one.</li>""")

class CFFForm(forms.ModelForm):
    class Meta:
        model = CustomFF

class CustomFieldSaveTests(TestCase):
    def test_save(self):
        "Regression for #11149: save_form_data should be called only once"

        # It's enough that the form saves without error -- the custom save routine will
        # generate an AssertionError if it is called more than once during save.
        form = CFFForm(data = {'f': None})
        form.save()

class ModelChoiceIteratorTests(TestCase):
    def test_len(self):
        class Form(forms.ModelForm):
            class Meta:
                model = Article
                fields = ["publications"]

        Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        f = Form()
        self.assertEqual(len(f.fields["publications"].choices), 1)

class RealPersonForm(forms.ModelForm):
    class Meta:
        model = RealPerson

class CustomModelFormSaveMethod(TestCase):
    def test_string_message(self):
        data = {'name': 'anonymous'}
        form = RealPersonForm(data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors['__all__'], ['Please specify a real name.'])

class ModelClassTests(TestCase):
    def test_no_model_class(self):
        class NoModelModelForm(forms.ModelForm):
            pass
        self.assertRaises(ValueError, NoModelModelForm)

class OneToOneFieldTests(TestCase):
    def test_assignment_of_none(self):
        class AuthorForm(forms.ModelForm):
            class Meta:
                model = Author
                fields = ['publication', 'full_name']

        publication = Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        author = Author.objects.create(publication=publication, full_name='John Doe')
        form = AuthorForm({'publication':u'', 'full_name':'John Doe'}, instance=author)
        self.assert_(form.is_valid())
        self.assertEqual(form.cleaned_data['publication'], None)
        author = form.save()
        # author object returned from form still retains original publication object
        # that's why we need to retreive it from database again
        new_author = Author.objects.get(pk=author.pk)
        self.assertEqual(new_author.publication, None)

    def test_assignment_of_none_null_false(self):
        class AuthorForm(forms.ModelForm):
            class Meta:
                model = Author1
                fields = ['publication', 'full_name']

        publication = Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        author = Author1.objects.create(publication=publication, full_name='John Doe')
        form = AuthorForm({'publication':u'', 'full_name':'John Doe'}, instance=author)
        self.assert_(not form.is_valid())


class ModelChoiceForm(forms.Form):
    person = ModelChoiceField(Person.objects.all())


class TestTicket11183(TestCase):
    def test_11183(self):
        form1 = ModelChoiceForm()
        field1 = form1.fields['person']
        # To allow the widget to change the queryset of field1.widget.choices correctly,
        # without affecting other forms, the following must hold:
        self.assert_(field1 is not ModelChoiceForm.base_fields['person'])
        self.assert_(field1.widget.choices.field is field1)

class HomepageForm(forms.ModelForm):
    class Meta:
        model = Homepage

class URLFieldTests(TestCase):
    def test_url_on_modelform(self):
        "Check basic URL field validation on model forms"
        self.assertFalse(HomepageForm({'url': 'foo'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://example'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://example.'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://com.'}).is_valid())

        self.assertTrue(HomepageForm({'url': 'http://localhost'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://example.com'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com:8000'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com/test'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com:8000/test'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://example.com/foo/bar'}).is_valid())

    def test_http_prefixing(self):
        "If the http:// prefix is omitted on form input, the field adds it again. (Refs #13613)"
        form = HomepageForm({'url': 'example.com'})
        form.is_valid()
        # self.assertTrue(form.is_valid())
        # self.assertEquals(form.cleaned_data['url'], 'http://example.com/')

        form = HomepageForm({'url': 'example.com/test'})
        form.is_valid()
        # self.assertTrue(form.is_valid())
        # self.assertEquals(form.cleaned_data['url'], 'http://example.com/test')


class FormFieldCallbackTests(TestCase):

    def test_baseform_with_widgets_in_meta(self):
        """Regression for #13095: Using base forms with widgets defined in Meta should not raise errors."""
        widget = forms.Textarea()

        class BaseForm(forms.ModelForm):
            class Meta:
                model = Person
                widgets = {'name': widget}

        Form = modelform_factory(Person, form=BaseForm)
        self.assertTrue(Form.base_fields['name'].widget is widget)

    def test_custom_callback(self):
        """Test that a custom formfield_callback is used if provided"""

        callback_args = []

        def callback(db_field, **kwargs):
            callback_args.append((db_field, kwargs))
            return db_field.formfield(**kwargs)

        widget = forms.Textarea()

        class BaseForm(forms.ModelForm):
            class Meta:
                model = Person
                widgets = {'name': widget}

        _ = modelform_factory(Person, form=BaseForm,
                              formfield_callback=callback)
        id_field, name_field = Person._meta.fields

        self.assertEqual(callback_args,
                         [(id_field, {}), (name_field, {'widget': widget})])

    def test_bad_callback(self):
        # A bad callback provided by user still gives an error
        self.assertRaises(TypeError, modelform_factory, Person,
                          formfield_callback='not a function or callable')
