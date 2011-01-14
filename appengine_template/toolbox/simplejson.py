from datetime import datetime
from django.utils import simplejson as json

def dtdump(data):
    """
    A modified version of simplejson that handles datetimes a little better.
    """
    return json.dumps(
        data, 
        default=lambda x: x.isoformat() if isinstance(x, datetime) else None
    )
