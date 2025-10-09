from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="profile"
    )
    telegram_chat_id = models.CharField(
        max_length=64, null=True, blank=True, unique=True
    )

    def __str__(self):
        return f"Profile<{self.user_id}> chat_id={self.telegram_chat_id!r}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
