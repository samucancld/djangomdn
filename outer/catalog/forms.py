from dataclasses import fields
import datetime

from django import forms
from catalog.models import Book, UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class RenewBookForm(forms.Form):
    '''if not specified the default label is the name
    of the field with a capital letter and a space instead of an underscore'''
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3).")

    borrower_choices = dict()

    for member in UserProfile.objects.all():
        borrower_choices[member.user.username] = member.user.username

    borrower_choices = list(borrower_choices.items())
    # print(borrower_choices)

    borrower_field = forms.ChoiceField(choices=borrower_choices)

    def clean_renewal_date(self):
        # gets us the data "cleaned" and sanitized of potentially unsafe input using the default validators, and converted into the correct standard type for the data (in this case a Python datetime.datetime object)
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Invalid date - renewal more than 4 weeks ahead'))

        return data


class CreateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'summary',
            'pubdate',
            'isbn',
            'author',
            'genre',
            'language',
            'cover',
        ]
        widgets = {
            'summary': forms.Textarea(),
        }


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'phone',
            'description',
            'userpic',
            # 'user', <-- MAL
        ]
        widgets = {
            'description': forms.Textarea(),
            # 'user': forms.HiddenInput(), <-- NO HACER NUNCA ESTO!
        }
