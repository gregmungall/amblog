# django-cleanup app is used to delete images whenever the image field is changed.

import posixpath
import urllib

from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

# Set user as the currently active user model.
User = get_user_model()


def post_photo_path(instance, filename):
    """
    Callable that sets the upload path dependent on if the post has been assigned a pk from the database.
    """
    if instance.pk is None:
        return 'post_pictures/tmp/{0}'.format(filename)
    return 'post_pictures/post_{0}/{1}'.format(instance.pk, filename)


def tag_photo_path(instance, filename):
    """
    Callable that sets the upload path for tag images.
    """
    return 'tag_pictures/{0}/{1}'.format(instance.slug, filename)


class Tag(models.Model):
    """
    Model for topic tags.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(allow_unicode=True, unique=True)  # Used for URLs.
    subheading = models.TextField()

    # Callable upload path.
    image = models.ImageField(blank=True, upload_to=tag_photo_path)

    overview = RichTextField()  # WYSIWYG rich text editor field (CKEditor).

    def save(self, *args, **kwargs):
        """
        Additonal to base, sets slug upon save.
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag-overview', kwargs={'slug': self.slug})

    def __str__(self):
        """
        String representation of object.
        """
        return self.name


class Post(models.Model):
    """
    Model for posts.
    """
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, unique=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    subheading = models.TextField(blank=True, null=True)

    # Callable upload path.
    image = models.ImageField(blank=True, null=True, upload_to=post_photo_path)

    created_date = models.DateTimeField(default=timezone.now, editable=False)
    publish_date = models.DateTimeField(blank=True, null=True)
    edited_date = models.DateTimeField(blank=True, null=True)
    # WYSIWYG rich text editor field (CKEditor).
    text = RichTextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Additonal to base, this saves the image in a dir that includes the post pk.
        """

        # In order to save the image in a directory named with the post pk,
        # the post must first be assigned a pk from the database (i.e. saved).
        # Therefore, when a post is first saved, the image is intially saved
        # in a tmp directory. It is then moved to a directory named with the
        # newly assigned post pk.

        # This action saves the record to the database which assigns a pk.
        # If the post has not been saved before, if the user has input an image
        # into the form, the image is saved to a tmp directory.
        super().save(*args, **kwargs)

        # If an image exists, check to see if the image is located in a tmp
        # directory. If yes, create a new directory using the post pk, move the
        # image, and remove the tmp directory.
        if self.image and urllib.parse.urljoin(settings.MEDIA_URL, 'post_pictures/tmp') == posixpath.dirname(self.image.url):

            # Store the tmp file path.
            tmp_file = self.image.name

            # Store the image filename.
            filename = posixpath.basename(tmp_file)

            # Open the image located in the tmp directory and call save on the
            # image field with the image data. As the post object now has a pk,
            # post_photo_path will return a path including the pk.
            with default_storage.open(tmp_file, 'rb') as f:
                data = File(f)
                self.image.save(filename, data, True)

            # Remove the tmp folder.
            default_storage.delete(tmp_file)

    def publish(self):
        """
        Saves the post, and sets publish date as the current date.
        """
        self.publish_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})

    def __str__(self):
        """
        String representation of object.
        """
        return self.title


class Comment(models.Model):
    """
    Model for comments.
    """
    post = models.ForeignKey(
        Post, related_name='comments', null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    edited_date = models.DateTimeField(blank=True, null=True)
    text = models.TextField()

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.post.pk})

    def __str__(self):
        """
        String representation of object.
        """
        return self.text
