import copy

from django.urls import reverse
from django.db.models.query import QuerySet

registry = []

def register(*args):
    """
    Register urls, views, model instances and QuerySets to be potential
    pages for menu items.

    Example::

        import simplemenu
        simplemenu.register(
            'package.module.view',
            ('package.module.view','name'),
            FlatPage.objects.all(),
            (FlatPage.objects.all(),'attr_containing_name'),
            Products.objects.get(pk=1),
        )
    """
    registry.extend(args)

class PageWrapper(object):
    """
    A helper-object to wrap the pages, which might be django models or
    strings.
    """
    def __init__(self, urlobj_or_str, name=None):
        if isinstance(urlobj_or_str, str):
            self.urlobj = None
            self.urlstr = urlobj_or_str
        else:
            self.urlobj = urlobj_or_str
            self.urlstr = str()
        self._name = name

    def name(self):
        if self._name:
            name = self._name
        elif self.urlobj:
            name = unicode(self.urlobj)
        elif "/" in self.urlstr:
            name = self.urlstr
        else:
            name = self.urlstr.rsplit('.', 1)[-1]
            name = name.replace("_", " ").capitalize()
        return name

    def url(self):
        if self.urlobj:
            url = self.urlobj.get_absolute_url()
        elif "/" in self.urlstr:
            url = self.urlstr
        else:
            url = reverse(self.urlstr)
        return url

    def strkey(self):
        """
        Generates somewhat unique string id of the wrappee.
        """
        if self.urlobj:
            return "%s.%s.pk%s" % (self.urlobj.__module__,
                                   self.urlobj.__class__.__name__,
                                   self.urlobj.pk)
        else:
            return self.urlstr

def get_registered_pages():
    """
    Returns all registered pages wrapped in PageWrapper helper-object
    evaluating all QuerySets along the way.
    """
    pages = []
    for reg in map(copy.deepcopy, registry):
        name = None
        if isinstance(reg, tuple):
            reg, name = reg
        if isinstance(reg, QuerySet):
            # Name is the given attr if possible elsewise just use unicode(obj)
            if not name:
                f  = lambda obj: PageWrapper(obj, unicode(obj))
            else:
                f  = lambda obj: PageWrapper(obj, getattr(obj, name, unicode(obj)))
            # evaluating QuerySet objects by iteration
            pages.extend(map(f, reg))
        else:
            pages.append(PageWrapper(reg, name))
    return pages
