from django.template import Library, Node, TemplateSyntaxError
from simplemenu.models import MenuItem, Menu

register = Library()

class SimplemenuNode(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = MenuItem.objects.all()
        return ''

class NamedmenuNode(Node):
    def __init__(self, menuname, varname):
        self.varname = varname
        self.menuname = menuname

    def render(self, context):
        menu = Menu.objects.get(name=self.menuname)
        context[self.varname] = MenuItem.objects.filter(menu=menu)
        return ''

@register.tag
def get_simplemenu(parser, token):
    """
    Loads all ``simplemenu.models.MenuItems`` and stores them in a
    context variable.

    Usage::

        {% get_simplemenu as [varname] %}

    Example::

        {% get_simplemenu as menu_items %}
        {% for item in menu_items %}
          <a href="{{ item.page.url }}">{{ item.name }}</a>
        {% endfor %}

    """
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise TemplateSyntaxError("Incorrect tag arguments. "
                                  "Usage: %s as varname" % bits[0])
    return SimplemenuNode(bits[2])

@register.tag
def get_namedmenu(parser, token):
    """
    Usage::

        {% get_namedmenu [menu] as [varname] %}
    """
    bits = token.split_contents()
    if len(bits) != 4 or bits[2] != 'as':
        raise TemplateSyntaxError("Incorrect tag arguments. "
                                  "Usage: %s menuname as varname" % bits[0])
    return NamedmenuNode(bits[1],bits[3])

@register.simple_tag
def active(request, pattern):
  import re
  # Special case for / - we don't want it lit up on every page...
  if pattern == "/":
    if not request.path == "/":
      return
  # /complicated/sub/directory should light up parent /complicated/
  if re.search(pattern, request.path):
    return 'active'
  return ''

