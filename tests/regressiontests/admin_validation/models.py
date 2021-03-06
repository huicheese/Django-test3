"""
Tests of ModelAdmin validation logic.
"""

from django.db import models


class Album(models.Model):
    title = models.CharField(max_length=150)


class Song(models.Model):
    title = models.CharField(max_length=150)
    album = models.ForeignKey(Album)

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title


class TwoAlbumFKAndAnE(models.Model):
    album1 = models.ForeignKey(Album, related_name="album1_set")
    album2 = models.ForeignKey(Album, related_name="album2_set")
    e = models.CharField(max_length=1)

class Book(models.Model):
    name = models.CharField(max_length=100)

__test__ = {'API_TESTS':"""

>>> from django import forms
>>> from django.contrib import admin
>>> from django.contrib.admin.validation import validate, validate_inline

# Regression test for #8027: custom ModelForms with fields/fieldsets

>>> class SongForm(forms.ModelForm):
...     pass

>>> class ValidFields(admin.ModelAdmin):
...     form = SongForm
...     fields = ['title']

>>> class InvalidFields(admin.ModelAdmin):
...     form = SongForm
...     fields = ['spam']

>>> validate(ValidFields, Song)
>>> validate(InvalidFields, Song)
Traceback (most recent call last):
    ...
ImproperlyConfigured: 'InvalidFields.fields' refers to field 'spam' that is missing from the form.

# Tests for basic validation of 'exclude' option values (#12689)

>>> class ExcludedFields1(admin.ModelAdmin):
...     exclude = ('foo')

>>> validate(ExcludedFields1, Book)
Traceback (most recent call last):
    ...
ImproperlyConfigured: 'ExcludedFields1.exclude' must be a list or tuple.

>>> class ExcludedFields2(admin.ModelAdmin):
...     exclude = ('name', 'name')

>>> validate(ExcludedFields2, Book)
Traceback (most recent call last):
    ...
ImproperlyConfigured: There are duplicate field(s) in ExcludedFields2.exclude

>>> class ExcludedFieldsInline(admin.TabularInline):
...     model = Song
...     exclude = ('foo')

>>> class ExcludedFieldsAlbumAdmin(admin.ModelAdmin):
...     model = Album
...     inlines = [ExcludedFieldsInline]

>>> validate(ExcludedFieldsAlbumAdmin, Album)
Traceback (most recent call last):
    ...
ImproperlyConfigured: 'ExcludedFieldsInline.exclude' must be a list or tuple.

# Regression test for #9932 - exclude in InlineModelAdmin
# should not contain the ForeignKey field used in ModelAdmin.model

>>> class SongInline(admin.StackedInline):
...     model = Song
...     exclude = ['album']

>>> class AlbumAdmin(admin.ModelAdmin):
...     model = Album
...     inlines = [SongInline]

>>> validate(AlbumAdmin, Album)
Traceback (most recent call last):
    ...
ImproperlyConfigured: SongInline cannot exclude the field 'album' - this is the foreign key to the parent model Album.

# Regression test for #11709 - when testing for fk excluding (when exclude is
# given) make sure fk_name is honored or things blow up when there is more
# than one fk to the parent model.

>>> class TwoAlbumFKAndAnEInline(admin.TabularInline):
...     model = TwoAlbumFKAndAnE
...     exclude = ("e",)
...     fk_name = "album1"

>>> validate_inline(TwoAlbumFKAndAnEInline, None, Album)

# Ensure inlines validate that they can be used correctly.

>>> class TwoAlbumFKAndAnEInline(admin.TabularInline):
...     model = TwoAlbumFKAndAnE

>>> validate_inline(TwoAlbumFKAndAnEInline, None, Album)
Traceback (most recent call last):
    ...
Exception: <class 'regressiontests.admin_validation.models.TwoAlbumFKAndAnE'> has more than 1 ForeignKey to <class 'regressiontests.admin_validation.models.Album'>

>>> class TwoAlbumFKAndAnEInline(admin.TabularInline):
...     model = TwoAlbumFKAndAnE
...     fk_name = "album1"

>>> validate_inline(TwoAlbumFKAndAnEInline, None, Album)

"""}
