from django.core import validators
from django import oldforms
from django.core.mail import mail_admins, mail_managers
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.comments.models import Comment, FreeComment, RATINGS_REQUIRED, RATINGS_OPTIONAL, IS_PUBLIC
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.utils.text import normalize_newlines
from django.conf import settings
from django.utils.translation import ngettext
import base64, datetime

COMMENTS_PER_PAGE = 20

class PublicCommentManipulator(AuthenticationForm):
    "Manipulator that handles public registered comments"
    def __init__(self, user, ratings_required, ratings_range, num_rating_choices):
        AuthenticationForm.__init__(self)
        self.ratings_range, self.num_rating_choices = ratings_range, num_rating_choices
        choices = [(c, c) for c in ratings_range]
        def get_validator_list(rating_num):
            if rating_num <= num_rating_choices:
                return [validators.RequiredIfOtherFieldsGiven(['rating%d' % i for i in range(1, 9) if i != rating_num], _("This rating is required because you've entered at least one other rating."))]
            else:
                return []
        self.fields.extend([
            oldforms.LargeTextField(field_name="comment", maxlength=3000, is_required=True,
                validator_list=[self.hasNoProfanities]),
            oldforms.RadioSelectField(field_name="rating1", choices=choices,
                is_required=ratings_required and num_rating_choices > 0,
                validator_list=get_validator_list(1),
            ),
            oldforms.RadioSelectField(field_name="rating2", choices=choices,
                is_required=ratings_required and num_rating_choices > 1,
                validator_list=get_validator_list(2),
            ),
            oldforms.RadioSelectField(field_name="rating3", choices=choices,
                is_required=ratings_required and num_rating_choices > 2,
                validator_list=get_validator_list(3),
            ),
            oldforms.RadioSelectField(field_name="rating4", choices=choices,
                is_required=ratings_required and num_rating_choices > 3,
                validator_list=get_validator_list(4),
            ),
            oldforms.RadioSelectField(field_name="rating5", choices=choices,
                is_required=ratings_required and num_rating_choices > 4,
                validator_list=get_validator_list(5),
            ),
            oldforms.RadioSelectField(field_name="rating6", choices=choices,
                is_required=ratings_required and num_rating_choices > 5,
                validator_list=get_validator_list(6),
            ),
            oldforms.RadioSelectField(field_name="rating7", choices=choices,
                is_required=ratings_required and num_rating_choices > 6,
                validator_list=get_validator_list(7),
            ),
            oldforms.RadioSelectField(field_name="rating8", choices=choices,
                is_required=ratings_required and num_rating_choices > 7,
                validator_list=get_validator_list(8),
            ),
        ])
        if user.is_authenticated():
            self["username"].is_required = False
            self["username"].validator_list = []
            self["password"].is_required = False
            self["password"].validator_list = []
            self.user_cache = user

    def hasNoProfanities(self, field_data, all_data):
        if settings.COMMENTS_ALLOW_PROFANITIES:
            return
        return validators.hasNoProfanities(field_data, all_data)

    def get_comment(self, new_data):
        "Helper function"
        return Comment(None, self.get_user_id(), new_data["content_type_id"],
            new_data["object_id"], new_data.get("headline", "").strip(),
            new_data["comment"].strip(), new_data.get("rating1", None),
            new_data.get("rating2", None), new_data.get("rating3", None),
            new_data.get("rating4", None), new_data.get("rating5", None),
            new_data.get("rating6", None), new_data.get("rating7", None),
            new_data.get("rating8", None), new_data.get("rating1", None) is not None,
            datetime.datetime.now(), new_data["is_public"], new_data["ip_address"], False, settings.SITE_ID)

    def save(self, new_data):
        today = datetime.date.today()
        c = self.get_comment(new_data)
        for old in Comment.objects.filter(content_type__id__exact=new_data["content_type_id"],
            object_id__exact=new_data["object_id"], user__id__exact=self.get_user_id()):
            # Check that this comment isn't duplicate. (Sometimes people post
            # comments twice by mistake.) If it is, fail silently by pretending
            # the comment was posted successfully.
            if old.submit_date.date() == today and old.comment == c.comment \
                and old.rating1 == c.rating1 and old.rating2 == c.rating2 \
                and old.rating3 == c.rating3 and old.rating4 == c.rating4 \
                and old.rating5 == c.rating5 and old.rating6 == c.rating6 \
                and old.rating7 == c.rating7 and old.rating8 == c.rating8:
                return old
            # If the user is leaving a rating, invalidate all old ratings.
            if c.rating1 is not None:
                old.valid_rating = False
                old.save()
        c.save()
        # If the commentor has posted fewer than COMMENTS_FIRST_FEW comments,
        # send the comment to the managers.
        if self.user_cache.comment_set.count() <= settings.COMMENTS_FIRST_FEW:
            message = ngettext('This comment was posted by a user who has posted fewer than %(count)s comment:\n\n%(text)s',
                'This comment was posted by a user who has posted fewer than %(count)s comments:\n\n%(text)s', settings.COMMENTS_FIRST_FEW) % \
                {'count': settings.COMMENTS_FIRST_FEW, 'text': c.get_as_text()}
            mail_managers("Comment posted by rookie user", message)
        if settings.COMMENTS_SKETCHY_USERS_GROUP and settings.COMMENTS_SKETCHY_USERS_GROUP in [g.id for g in self.user_cache.get_group_list()]:
            message = _('This comment was posted by a sketchy user:\n\n%(text)s') % {'text': c.get_as_text()}
            mail_managers("Comment posted by sketchy user (%s)" % self.user_cache.username, c.get_as_text())
        return c

class PublicFreeCommentManipulator(oldforms.Manipulator):
    "Manipulator that handles public free (unregistered) comments"
    def __init__(self):
        self.fields = (
            oldforms.TextField(field_name="person_name", maxlength=50, is_required=True,
                validator_list=[self.hasNoProfanities]),
            oldforms.LargeTextField(field_name="comment", maxlength=3000, is_required=True,
                validator_list=[self.hasNoProfanities]),
        )

    def hasNoProfanities(self, field_data, all_data):
        if settings.COMMENTS_ALLOW_PROFANITIES:
            return
        return validators.hasNoProfanities(field_data, all_data)

    def get_comment(self, new_data):
        "Helper function"
        return FreeComment(None, new_data["content_type_id"],
            new_data["object_id"], new_data["comment"].strip(),
            new_data["person_name"].strip(), datetime.datetime.now(), new_data["is_public"],
            new_data["ip_address"], False, settings.SITE_ID)

    def save(self, new_data):
        today = datetime.date.today()
        c = self.get_comment(new_data)
        # Check that this comment isn't duplicate. (Sometimes people post
        # comments twice by mistake.) If it is, fail silently by pretending
        # the comment was posted successfully.
        for old_comment in FreeComment.objects.filter(content_type__id__exact=new_data["content_type_id"],
            object_id__exact=new_data["object_id"], person_name__exact=new_data["person_name"],
            submit_date__year=today.year, submit_date__month=today.month,
            submit_date__day=today.day):
            if old_comment.comment == c.comment:
                return old_comment
        c.save()
        return c

def post_comment(request):
    """
    Post a comment

    Redirects to the `comments.comments.comment_was_posted` view upon success.

    Templates: `comment_preview`
    Context:
        comment
            the comment being posted
        comment_form
            the comment form
        options
            comment options
        target
            comment target
        hash
            security hash (must be included in a posted form to succesfully
            post a comment).
        rating_options
            comment ratings options
        ratings_optional
            are ratings optional?
        ratings_required
            are ratings required?
        rating_range
            range of ratings
        rating_choices
            choice of ratings
    """
    if not request.POST:
        raise Http404, _("Only POSTs are allowed")
    try:
        options, target, security_hash = request.POST['options'], request.POST['target'], request.POST['gonzo']
    except KeyError:
        raise Http404, _("One or more of the required fields wasn't submitted")
    photo_options = request.POST.get('photo_options', '')
    rating_options = normalize_newlines(request.POST.get('rating_options', ''))
    if Comment.objects.get_security_hash(options, photo_options, rating_options, target) != security_hash:
        raise Http404, _("Somebody tampered with the comment form (security violation)")
    # Now we can be assured the data is valid.
    if rating_options:
        rating_range, rating_choices = Comment.objects.get_rating_options(base64.decodestring(rating_options))
    else:
        rating_range, rating_choices = [], []
    content_type_id, object_id = target.split(':') # target is something like '52:5157'
    try:
        obj = ContentType.objects.get(pk=content_type_id).get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404, _("The comment form had an invalid 'target' parameter -- the object ID was invalid")
    option_list = options.split(',') # options is something like 'pa,ra'
    new_data = request.POST.copy()
    new_data['content_type_id'] = content_type_id
    new_data['object_id'] = object_id
    new_data['ip_address'] = request.META.get('REMOTE_ADDR')
    new_data['is_public'] = IS_PUBLIC in option_list
    manipulator = PublicCommentManipulator(request.user,
        ratings_required=RATINGS_REQUIRED in option_list,
        ratings_range=rating_range,
        num_rating_choices=len(rating_choices))
    errors = manipulator.get_validation_errors(new_data)
    # If user gave correct username/password and wasn't already logged in, log them in
    # so they don't have to enter a username/password again.
    if manipulator.get_user() and not manipulator.get_user().is_authenticated() and new_data.has_key('password') and manipulator.get_user().check_password(new_data['password']):
        from django.contrib.auth import login
        login(request, manipulator.get_user())
    if errors or request.POST.has_key('preview'):
        class CommentFormWrapper(oldforms.FormWrapper):
            def __init__(self, manipulator, new_data, errors, rating_choices):
                oldforms.FormWrapper.__init__(self, manipulator, new_data, errors)
                self.rating_choices = rating_choices
            def ratings(self):
                field_list = [self['rating%d' % (i+1)] for i in range(len(rating_choices))]
                for i, f in enumerate(field_list):
                    f.choice = rating_choices[i]
                return field_list
        comment = errors and '' or manipulator.get_comment(new_data)
        comment_form = CommentFormWrapper(manipulator, new_data, errors, rating_choices)
        return render_to_response('comments/preview.html', {
            'comment': comment,
            'comment_form': comment_form,
            'options': options,
            'target': target,
            'hash': security_hash,
            'rating_options': rating_options,
            'ratings_optional': RATINGS_OPTIONAL in option_list,
            'ratings_required': RATINGS_REQUIRED in option_list,
            'rating_range': rating_range,
            'rating_choices': rating_choices,
        }, context_instance=RequestContext(request))
    elif request.POST.has_key('post'):
        # If the IP is banned, mail the admins, do NOT save the comment, and
        # serve up the "Thanks for posting" page as if the comment WAS posted.
        if request.META['REMOTE_ADDR'] in settings.BANNED_IPS:
            mail_admins("Banned IP attempted to post comment", str(request.POST) + "\n\n" + str(request.META))
        else:
            manipulator.do_html2python(new_data)
            comment = manipulator.save(new_data)
        return HttpResponseRedirect("../posted/?c=%s:%s" % (content_type_id, object_id))
    else:
        raise Http404, _("The comment form didn't provide either 'preview' or 'post'")

def post_free_comment(request):
    """
    Post a free comment (not requiring a log in)

    Redirects to `comments.comments.comment_was_posted` view on success.

    Templates: `comment_free_preview`
    Context:
        comment
            comment being posted
        comment_form
            comment form object
        options
            comment options
        target
            comment target
        hash
            security hash (must be included in a posted form to succesfully
            post a comment).
    """
    if not request.POST:
        raise Http404, _("Only POSTs are allowed")
    try:
        options, target, security_hash = request.POST['options'], request.POST['target'], request.POST['gonzo']
    except KeyError:
        raise Http404, _("One or more of the required fields wasn't submitted")
    if Comment.objects.get_security_hash(options, '', '', target) != security_hash:
        raise Http404, _("Somebody tampered with the comment form (security violation)")
    content_type_id, object_id = target.split(':') # target is something like '52:5157'
    content_type = ContentType.objects.get(pk=content_type_id)
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404, _("The comment form had an invalid 'target' parameter -- the object ID was invalid")
    option_list = options.split(',')
    new_data = request.POST.copy()
    new_data['content_type_id'] = content_type_id
    new_data['object_id'] = object_id
    new_data['ip_address'] = request.META['REMOTE_ADDR']
    new_data['is_public'] = IS_PUBLIC in option_list
    manipulator = PublicFreeCommentManipulator()
    errors = manipulator.get_validation_errors(new_data)
    if errors or request.POST.has_key('preview'):
        comment = errors and '' or manipulator.get_comment(new_data)
        return render_to_response('comments/free_preview.html', {
            'comment': comment,
            'comment_form': oldforms.FormWrapper(manipulator, new_data, errors),
            'options': options,
            'target': target,
            'hash': security_hash,
        }, context_instance=RequestContext(request))
    elif request.POST.has_key('post'):
        # If the IP is banned, mail the admins, do NOT save the comment, and
        # serve up the "Thanks for posting" page as if the comment WAS posted.
        if request.META['REMOTE_ADDR'] in settings.BANNED_IPS:
            from django.core.mail import mail_admins
            mail_admins("Practical joker", str(request.POST) + "\n\n" + str(request.META))
        else:
            manipulator.do_html2python(new_data)
            comment = manipulator.save(new_data)
        return HttpResponseRedirect("../posted/?c=%s:%s" % (content_type_id, object_id))
    else:
        raise Http404, _("The comment form didn't provide either 'preview' or 'post'")

def comment_was_posted(request):
    """
    Display "comment was posted" success page

    Templates: `comment_posted`
    Context:
        object
            The object the comment was posted on
    """
    obj = None
    if request.GET.has_key('c'):
        content_type_id, object_id = request.GET['c'].split(':')
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
            obj = content_type.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            pass
    return render_to_response('comments/posted.html', {'object': obj}, context_instance=RequestContext(request))
