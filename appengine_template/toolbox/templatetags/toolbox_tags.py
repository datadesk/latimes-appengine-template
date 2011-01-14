"""
A collection of miscellaneous string filters that we use to dress up our data.
"""
# Templatetag helpers
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
