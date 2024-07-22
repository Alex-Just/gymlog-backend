from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import ImageField
from django.db.models import TextField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from gymlog.mixins import UUIDModel


class User(UUIDModel, AbstractUser):
    """
    Default custom user model for gymlog.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    language = CharField(_("Preferred language"), max_length=10, blank=True)
    bio = TextField(_("Bio"), blank=True)
    profile_picture = ImageField(
        _("Profile Picture"),
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    private_profile = BooleanField(_("Private Profile"), default=True)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
