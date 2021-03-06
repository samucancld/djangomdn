from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User, Group
from datetime import date
from django.db.models.signals import pre_save

import uuid


class Language(models.Model):
    name = models.CharField(
        max_length=200, help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    '''attrs'''
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)
    authpic = models.ImageField(
        upload_to='authpics/', null=True, blank=True, verbose_name='Photo')
    '''metadata'''
    class Meta:
        permissions = (
            ('can_crud_authors', '#Create, Update and Delete authors'),
        )
        ordering = ['last_name', 'first_name']
    '''methods'''

    def __str__(self) -> str:
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        return reverse('catalog:author-detail', args=[str(self.id)])


class Genre(models.Model):
    name = models.CharField(
        max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    # attrs
    title = models.CharField(max_length=200)
    summary = models.CharField(
        max_length=1000, help_text='Enter a brief description of the book')

    pubdate = models.DateField('Publication Date')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    # punteros
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField(
        Genre, help_text='Select a genre for this book')
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=False, blank=False, unique=True)
    cover = models.ImageField(upload_to='covers/', null=True)

    # metadata
    class Meta:
        ordering = ["title", "-pubdate"]
        permissions = (
            ('can_crud_books', 'Can create, update, and delete books'),
        )

    # methods

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('catalog:book-detail', args=[str(self.slug)])

    def display_genre(self):
        ''' create a string for the genre, used in admin.py'''
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'

    def set_slug(sender, instance, *args, **kwargs):
        if instance.slug:
            return
        instance.slug = slugify(
            instance.title+'-'+instance.author.first_name+instance.author.last_name)


# pre_save.connect(Book.set_slug, sender=Book)


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book across whole library')
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(
        'Expected date of availability', null=True, blank=True)
    LOAN_STATUS = (
        ('o', 'On loan'),
        ('a', 'Available'),
    )
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        help_text='Book availability',
    )

    '''metadata'''
    class Meta:
        ''' the first attr on the permission is the name of the
        actual permission, and the second is a little description'''
        permissions = (
            ('can_mark_returned', 'Set book as returned'),
        )
    #     ordering = ('status','-due_back')

    '''punteros'''
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    borrower = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    '''methods'''

    def __str__(self) -> str:
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)


class UserProfile(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    userpic = models.ImageField(
        null=True,
        blank=True,
        upload_to='userpics/',
        verbose_name='Profile Picture',
    )
    description = models.CharField(
        max_length=1000,
        help_text='Enter a brief description of you',
        null=True,
        blank=True,
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    slug = models.SlugField(null=False, blank=False, unique=True)

    def set_slug(sender, instance, *args, **kwargs):
        if instance.slug:
            return
        instance.slug = slugify(
            instance.user.username)

    def set_membership(sender, instance, created, **kwargs):
        # if created:
        library_member = Group.objects.get(name='Library Member')
        library_member.user_set.add(instance.user)

    def __str__(self) -> str:
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        return reverse('catalog:user-profile', args=[str(self.slug)])

    def liberate_loaned_books(sender, instance, *args, **kwargs):
        # print('debug_liberate_loaned_books', instance)
        for i in instance.user.bookinstance_set.iterator():
            i.status = 'a'
            i.save()
            print('debug_liberate_loaned_books')


class LibrarianGroupBasedPermission(models.Model):
    class Meta:
        permissions = (
            ('is_librarian', 'This user is a Librarian'),
        )


class LibraryMemberGroupBasedPermission(models.Model):
    class Meta:
        permissions = (
            ('is_library_member', 'This user is a Library Member'),
        )
