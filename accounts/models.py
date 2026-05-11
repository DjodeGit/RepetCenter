from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN      = 'ADMIN',      'Administrateur'
        ENSEIGNANT = 'ENSEIGNANT', 'Enseignant'
        APPRENANT  = 'APPRENANT',  'Apprenant'

    email      = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name  = models.CharField(max_length=100, verbose_name="Nom")
    phone      = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo      = models.ImageField(
                    upload_to='photos/users/',
                    blank=True, null=True,
                    verbose_name="Photo de profil"
                )
    role       = models.CharField(
                    max_length=20,
                    choices=Role.choices,
                    default=Role.APPRENANT,
                    verbose_name="Rôle"
                )
    is_active       = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff        = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(auto_now_add=True, verbose_name="Date création")
    last_login_date = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering            = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    # Propriétés utiles pour les templates et vues
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_enseignant(self):
        return self.role == self.Role.ENSEIGNANT

    @property
    def is_apprenant(self):
        return self.role == self.Role.APPRENANT