import re

def slugify(value):
    """
    Converts to lowercase, removes non-alpha chars and converts spaces to hyphens
    
    Taken from django. Helpful to have it here so I can use it with webapp code.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('\s+', '-', value)

