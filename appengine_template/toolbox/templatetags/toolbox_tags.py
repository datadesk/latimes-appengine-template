"""
A collection of miscellaneous string filters that we use to dress up our data.
"""
# Templatetag helpers
import re
from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

# Open up the templatetag registry
register = template.Library()

#
# Replacement filters
#

def truthjs(bool):
    """
    Replaces True with true and False with false, so I can print JavaScript.
    """
    if bool == True:
        return 'true'
    elif bool == False:
        return 'false'
    elif bool == None:
        return 'null'
    else:
        return ''
truthjs.is_safe = True
register.filter(truthjs)


def datejs(dt):
    """
    Reformats a datetime object as a JavaScript Date() object.
    """
    if hasattr(dt, 'hour') and hasattr(dt, 'minute') and hasattr(dt, 'second'):
        js = 'Date(%s, %s, %s, %s, %s, %s)' % (
            dt.year, dt.month-1, dt.day,
            dt.hour, dt.minute, dt.second,
        )
    else:
        js = 'Date(%s, %s, %s)' % (dt.year, dt.month-1, dt.day)
    return mark_safe(js)
datejs.is_safe = True
register.filter(datejs)


def trim_p(html, count=2):
    """
    Trims a html block to the requested number of paragraphs
    """
    grafs = [i.end() for i in re.finditer("</p>", html)]
    if len(grafs) < count:
        return html
    else:
        end = grafs[count-1]
        return html[:end]
trim_p = stringfilter(trim_p)
register.filter(trim_p)

_base_js_escapes = (
    ('\\', r'\u005C'),
    ('\'', r'\u0027'),
    ('"', r'\u0022'),
    ('>', r'\u003E'),
    ('<', r'\u003C'),
    ('&', r'\u0026'),
    ('=', r'\u003D'),
    ('-', r'\u002D'),
    (';', r'\u003B'),
    (u'\u2028', r'\u2028'),
    (u'\u2029', r'\u2029')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))

def escapejs(value):
    """
    Replaces Django's built-in escaping function with one that actually works.

    Take from "Changeset 12781":http://code.djangoproject.com/changeset/12781
    """
    for bad, good in _js_escapes:
        value = value.replace(bad, good)
    return value
escapejs = stringfilter(escapejs)
register.filter(escapejs)
