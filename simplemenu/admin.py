from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.urls import include, re_path

from simplemenu.models import MenuItem, URLItem, Menu
from simplemenu.forms import MenuItemForm


class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    list_display = ('item_name', 'move', 'page')
    list_filter = ('menu',)

    def save_model(self, request, obj, form, change):
        obj.page = form.selected_page()
        obj.save()

    def item_name(self, obj):
        # just to forbid sorting by name
        return obj.name

    item_name.short_description = ugettext_lazy('Item caption')

    def page(self, obj):
        return obj.page.name()

    page.short_description = ugettext_lazy('Page')

    def move(sefl, obj):
        """
        Returns html with links to move_up and move_down views.
        """
        button = u'<a href="%s"><img src="%ssimplemenu/arrow-%s.gif" /> %s</a>'
        prefix = settings.STATIC_URL

        link = '%d/move_up/' % obj.pk
        html = button % (link, prefix, 'up', _('up')) + " | "
        link = '%d/move_down/' % obj.pk
        html += button % (link, prefix, 'down', _('down'))
        return html
    move.allow_tags = True
    move.short_description = ugettext_lazy('Move')

    def get_urls(self):
        admin_view = self.admin_site.admin_view
        urls = [
            re_path(r'^(?P<item_pk>\d+)/move_up/$', admin_view(self.move_up)),
            re_path(r'^(?P<item_pk>\d+)/move_down/$', admin_view(self.move_down)),
        ]
        return urls + super(MenuItemAdmin, self).get_urls()

    def move_up(self, request, item_pk):
        """
        Decrease rank (change ordering) of the menu item with
        id=``item_pk``.
        """
        if self.has_change_permission(request):
            item = get_object_or_404(MenuItem, pk=item_pk)
            item.decrease_rank()
        else:
            raise PermissionDenied
        return redirect('admin:simplemenu_menuitem_changelist')

    def move_down(self, request, item_pk):
        """
        Increase rank (change ordering) of the menu item with
        id=``item_pk``.
        """
        if self.has_change_permission(request):
            item = get_object_or_404(MenuItem, pk=item_pk)
            item.increase_rank()
        else:
            raise PermissionDenied
        return redirect('admin:simplemenu_menuitem_changelist')


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', )


class UrlItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')


admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(URLItem, UrlItemAdmin)
admin.site.register(Menu, MenuAdmin)
