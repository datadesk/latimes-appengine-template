class MergeDict(object):
    """
    A simple class for creating new "virtual" dictionaries that actualy look
    up values in more than one dictionary, passed in the constructor.
    """
    def __init__(self, *dicts):
        self.dicts = dicts

    def __getitem__(self, key):
        for dict in self.dicts:
            try:
                return dict[key]
            except KeyError:
                pass
        raise KeyError

    def __contains__(self, key):
        return self.has_key(key)
        
    def __copy__(self): 
        return self.__class__(*self.dicts) 

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def getlist(self, key):
        for dict in self.dicts:
            try:
                return dict.getlist(key)
            except KeyError:
                pass
        raise KeyError

    def items(self):
        item_list = []
        for dict in self.dicts:
            item_list.extend(dict.items())
        return item_list

    def has_key(self, key):
        for dict in self.dicts:
            if dict.has_key(key):
                return True
        return False
        
    def copy(self): 
        """ returns a copy of this object""" 
        return self.__copy__()

class SortedDict(dict):
    "A dictionary that keeps its keys in the order in which they're inserted."
    def __init__(self, data=None):
        if data is None: data = {}
        dict.__init__(self, data)
        self.keyOrder = data.keys()

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key not in self.keyOrder:
            self.keyOrder.append(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.keyOrder.remove(key)

    def __iter__(self):
        for k in self.keyOrder:
            yield k

    def items(self):
        return zip(self.keyOrder, self.values())

    def keys(self):
        return self.keyOrder[:]

    def values(self):
        return [dict.__getitem__(self, k) for k in self.keyOrder]

    def update(self, dict):
        for k, v in dict.items():
            self.__setitem__(k, v)

    def setdefault(self, key, default):
        if key not in self.keyOrder:
            self.keyOrder.append(key)
        return dict.setdefault(self, key, default)

    def value_for_index(self, index):
        "Returns the value of the item at the given zero-based index."
        return self[self.keyOrder[index]]

    def copy(self):
        "Returns a copy of this object."
        # This way of initializing the copy means it works for subclasses, too.
        obj = self.__class__(self)
        obj.keyOrder = self.keyOrder
        return obj

class MultiValueDictKeyError(KeyError):
    pass

class MultiValueDict(dict):
    """
    A subclass of dictionary customized to handle multiple values for the same key.

    >>> d = MultiValueDict({'name': ['Adrian', 'Simon'], 'position': ['Developer']})
    >>> d['name']
    'Simon'
    >>> d.getlist('name')
    ['Adrian', 'Simon']
    >>> d.get('lastname', 'nonexistent')
    'nonexistent'
    >>> d.setlist('lastname', ['Holovaty', 'Willison'])

    This class exists to solve the irritating problem raised by cgi.parse_qs,
    which returns a list for every key, even though most Web forms submit
    single name-value pairs.
    """
    def __init__(self, key_to_list_mapping=()):
        dict.__init__(self, key_to_list_mapping)

    def __repr__(self):
        return "<MultiValueDict: %s>" % dict.__repr__(self)

    def __getitem__(self, key):
        """
        Returns the last data value for this key, or [] if it's an empty list;
        raises KeyError if not found.
        """
        try:
            list_ = dict.__getitem__(self, key)
        except KeyError:
            raise MultiValueDictKeyError, "Key %r not found in %r" % (key, self)
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, [value])

    def __copy__(self):
        return self.__class__(dict.items(self))

    def __deepcopy__(self, memo=None):
        import copy
        if memo is None: memo = {}
        result = self.__class__()
        memo[id(self)] = result
        for key, value in dict.items(self):
            dict.__setitem__(result, copy.deepcopy(key, memo), copy.deepcopy(value, memo))
        return result

    def get(self, key, default=None):
        "Returns the default value if the requested data doesn't exist"
        try:
            val = self[key]
        except KeyError:
            return default
        if val == []:
            return default
        return val

    def getlist(self, key):
        "Returns an empty list if the requested data doesn't exist"
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return []

    def setlist(self, key, list_):
        dict.__setitem__(self, key, list_)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def setlistdefault(self, key, default_list=()):
        if key not in self:
            self.setlist(key, default_list)
        return self.getlist(key)

    def appendlist(self, key, value):
        "Appends an item to the internal list associated with key"
        self.setlistdefault(key, [])
        dict.__setitem__(self, key, self.getlist(key) + [value])

    def items(self):
        """
        Returns a list of (key, value) pairs, where value is the last item in
        the list associated with the key.
        """
        return [(key, self[key]) for key in self.keys()]

    def lists(self):
        "Returns a list of (key, list) pairs."
        return dict.items(self)

    def values(self):
        "Returns a list of the last value on every key list."
        return [self[key] for key in self.keys()]

    def copy(self):
        "Returns a copy of this object."
        return self.__deepcopy__()

    def update(self, *args, **kwargs):
        "update() extends rather than replaces existing key lists. Also accepts keyword args."
        if len(args) > 1:
            raise TypeError, "update expected at most 1 arguments, got %d", len(args)
        if args:
            other_dict = args[0]
            if isinstance(other_dict, MultiValueDict):
                for key, value_list in other_dict.lists():
                    self.setlistdefault(key, []).extend(value_list)
            else:
                try:
                    for key, value in other_dict.items():
                        self.setlistdefault(key, []).append(value)
                except TypeError:
                    raise ValueError, "MultiValueDict.update() takes either a MultiValueDict or dictionary"
        for key, value in kwargs.iteritems():
            self.setlistdefault(key, []).append(value)

class DotExpandedDict(dict):
    """
    A special dictionary constructor that takes a dictionary in which the keys
    may contain dots to specify inner dictionaries. It's confusing, but this
    example should make sense.

    >>> d = DotExpandedDict({'person.1.firstname': ['Simon'],
            'person.1.lastname': ['Willison'],
            'person.2.firstname': ['Adrian'],
            'person.2.lastname': ['Holovaty']})
    >>> d
    {'person': {'1': {'lastname': ['Willison'], 'firstname': ['Simon']},
    '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}}}
    >>> d['person']
    {'1': {'firstname': ['Simon'], 'lastname': ['Willison'],
    '2': {'firstname': ['Adrian'], 'lastname': ['Holovaty']}
    >>> d['person']['1']
    {'firstname': ['Simon'], 'lastname': ['Willison']}

    # Gotcha: Results are unpredictable if the dots are "uneven":
    >>> DotExpandedDict({'c.1': 2, 'c.2': 3, 'c': 1})
    >>> {'c': 1}
    """
    def __init__(self, key_to_list_mapping):
        for k, v in key_to_list_mapping.items():
            current = self
            bits = k.split('.')
            for bit in bits[:-1]:
                current = current.setdefault(bit, {})
            # Now assign value to current position
            try:
                current[bits[-1]] = v
            except TypeError: # Special-case if current isn't a dict.
                current = {bits[-1] : v}
