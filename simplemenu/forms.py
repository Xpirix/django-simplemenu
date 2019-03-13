from django import forms
from django.utils.translation import ugettext_lazy as _

from simplemenu.models import MenuItem
from simplemenu.pages import get_registered_pages

class MenuItemForm(forms.ModelForm):
    page = forms.ChoiceField(label=_('Page'))

    class Meta:
        model = MenuItem
        fields = ('name','menu')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=forms.utils.ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):
        if instance:
            if not initial:
                initial = {}
            initial['page'] = instance.page.strkey()
        super(MenuItemForm, self).__init__(data, files, auto_id, prefix,
                                           initial, error_class, label_suffix,
                                           empty_permitted, instance)
        self._registered_pages_cache = get_registered_pages()
        self.fields['page'].choices = self.page_choices()
        self.fields['name'].required = False

    def page_choices(self):
        """
        Returns list of 2-tuples ('page unique key', 'page name')
        to fill the ChoiceField.
        """
        from IPython import embed; embed(using=False)
        choices = []
        for p in self._registered_pages_cache:
            choices.append((p.strkey(), p.name()))
        choices.sort(key=lambda x: x[1])
        return choices


    def selected_page(self):
        """
        Returns ``simplemenu.pages.PageWrapper`` for the selected from
        ChoiceField page if form is bound.
        """
        key = self.cleaned_data['page']
        for p in self._registered_pages_cache:
            if p.strkey() == key:
                return p
        return None

    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data['name']
        if not name:
            cleaned_data['name'] = self.selected_page().name()
        return cleaned_data
