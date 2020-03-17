from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favorite_pony = models.CharField(max_length=1024, blank=True)
    favorite_pony = models.CharField(max_length=1024, blank=True)
    theme_choices = [
        (1, "Princess Luna"),  # Dark theme
        (2, "King Sombra"),  # Black/red theme
        (3, "Shining Armor"),  # Light/blue theme
        (4, "Pinkie Pie"),  # Overboard pink pony theme
    ]
    theme = IntegerField(choices=theme_choices)

    def __str__(self):
        return "{}'s profile".format(self.user)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)
