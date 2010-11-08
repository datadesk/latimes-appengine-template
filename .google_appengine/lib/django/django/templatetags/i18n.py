from django.template import Node, resolve_variable
from django.template import TemplateSyntaxError, TokenParser, Library
from django.template import TOKEN_TEXT, TOKEN_VAR
from django.utils import translation

register = Library()

class GetAvailableLanguagesNode(Node):
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        from django.conf import settings
        context[self.variable] = [(k, translation.gettext(v)) for k, v in settings.LANGUAGES]
        return ''

class GetCurrentLanguageNode(Node):
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        context[self.variable] = translation.get_language()
        return ''

class GetCurrentLanguageBidiNode(Node):
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        context[self.variable] = translation.get_language_bidi()
        return ''

class TranslateNode(Node):
    def __init__(self, value, noop):
        self.value = value
        self.noop = noop

    def render(self, context):
        value = resolve_variable(self.value, context)
        if self.noop:
            return value
        else:
            return translation.gettext(value)

class BlockTranslateNode(Node):
    def __init__(self, extra_context, singular, plural=None, countervar=None, counter=None):
        self.extra_context = extra_context
        self.singular = singular
        self.plural = plural
        self.countervar = countervar
        self.counter = counter

    def render_token_list(self, tokens):
        result = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents)
            elif token.token_type == TOKEN_VAR:
                result.append('%%(%s)s' % token.contents)
        return ''.join(result)

    def render(self, context):
        context.push()
        for var,val in self.extra_context.items():
            context[var] = val.resolve(context)
        singular = self.render_token_list(self.singular)
        if self.plural and self.countervar and self.counter:
            count = self.counter.resolve(context)
            context[self.countervar] = count
            plural = self.render_token_list(self.plural)
            result = translation.ngettext(singular, plural, count) % context
        else:
            result = translation.gettext(singular) % context
        context.pop()
        return result

def do_get_available_languages(parser, token):
    """
    This will store a list of available languages
    in the context.

    Usage::

        {% get_available_languages as languages %}
        {% for language in languages %}
        ...
        {% endfor %}

    This will just pull the LANGUAGES setting from
    your setting file (or the default settings) and
    put it into the named variable.
    """
    args = token.contents.split()
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "'get_available_languages' requires 'as variable' (got %r)" % args
    return GetAvailableLanguagesNode(args[2])

def do_get_current_language(parser, token):
    """
    This will store the current language in the context.

    Usage::

        {% get_current_language as language %}

    This will fetch the currently active language and
    put it's value into the ``language`` context
    variable.
    """
    args = token.contents.split()
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "'get_current_language' requires 'as variable' (got %r)" % args
    return GetCurrentLanguageNode(args[2])

def do_get_current_language_bidi(parser, token):
    """
    This will store the current language layout in the context.

    Usage::

        {% get_current_language_bidi as bidi %}

    This will fetch the currently active language's layout and
    put it's value into the ``bidi`` context variable.
    True indicates right-to-left layout, otherwise left-to-right
    """
    args = token.contents.split()
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "'get_current_language_bidi' requires 'as variable' (got %r)" % args
    return GetCurrentLanguageBidiNode(args[2])

def do_translate(parser, token):
    """
    This will mark a string for translation and will
    translate the string for the current language.

    Usage::

        {% trans "this is a test" %}

    This will mark the string for translation so it will
    be pulled out by mark-messages.py into the .po files
    and will run the string through the translation engine.

    There is a second form::

        {% trans "this is a test" noop %}

    This will only mark for translation, but will return
    the string unchanged. Use it when you need to store
    values into forms that should be translated later on.

    You can use variables instead of constant strings
    to translate stuff you marked somewhere else::

        {% trans variable %}

    This will just try to translate the contents of
    the variable ``variable``. Make sure that the string
    in there is something that is in the .po file.
    """
    class TranslateParser(TokenParser):
        def top(self):
            value = self.value()
            if self.more():
                if self.tag() == 'noop':
                    noop = True
                else:
                    raise TemplateSyntaxError, "only option for 'trans' is 'noop'"
            else:
                noop = False
            return (value, noop)
    value, noop = TranslateParser(token.contents).top()
    return TranslateNode(value, noop)

def do_block_translate(parser, token):
    """
    This will translate a block of text with parameters.

    Usage::

        {% blocktrans with foo|filter as bar and baz|filter as boo %}
        This is {{ bar }} and {{ boo }}.
        {% endblocktrans %}

    Additionally, this supports pluralization::

        {% blocktrans count var|length as count %}
        There is {{ count }} object.
        {% plural %}
        There are {{ count }} objects.
        {% endblocktrans %}

    This is much like ngettext, only in template syntax.
    """
    class BlockTranslateParser(TokenParser):

        def top(self):
            countervar = None
            counter = None
            extra_context = {}
            while self.more():
                tag = self.tag()
                if tag == 'with' or tag == 'and':
                    value = self.value()
                    if self.tag() != 'as':
                        raise TemplateSyntaxError, "variable bindings in 'blocktrans' must be 'with value as variable'"
                    extra_context[self.tag()] = parser.compile_filter(value)
                elif tag == 'count':
                    counter = parser.compile_filter(self.value())
                    if self.tag() != 'as':
                        raise TemplateSyntaxError, "counter specification in 'blocktrans' must be 'count value as variable'"
                    countervar = self.tag()
                else:
                    raise TemplateSyntaxError, "unknown subtag %s for 'blocktrans' found" % tag
            return (countervar, counter, extra_context)

    countervar, counter, extra_context = BlockTranslateParser(token.contents).top()

    singular = []
    plural = []
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            singular.append(token)
        else:
            break
    if countervar and counter:
        if token.contents.strip() != 'plural':
            raise TemplateSyntaxError, "'blocktrans' doesn't allow other block tags inside it"
        while parser.tokens:
            token = parser.next_token()
            if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
                plural.append(token)
            else:
                break
    if token.contents.strip() != 'endblocktrans':
        raise TemplateSyntaxError, "'blocktrans' doesn't allow other block tags (seen %r) inside it" % token.contents

    return BlockTranslateNode(extra_context, singular, plural, countervar, counter)

register.tag('get_available_languages', do_get_available_languages)
register.tag('get_current_language', do_get_current_language)
register.tag('get_current_language_bidi', do_get_current_language_bidi)
register.tag('trans', do_translate)
register.tag('blocktrans', do_block_translate)
