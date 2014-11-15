from django.db import models
from django.contrib import admin

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile

from imagekit.models.fields import ImageSpecField
from imagekit.processors import ResizeToFit


class MyProfile(UserenaBaseProfile):
    user = models.OneToOneField(User, unique=True,
                        verbose_name=_('user'), related_name='my_profile')
    favourite_snack = models.CharField(_('favourite snack'), max_length=5)

    def __str__(self):
        return self.user.get_username()