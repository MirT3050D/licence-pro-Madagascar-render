from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    point = models.IntegerField(default=0)

    class Meta:
        db_table = 'role'
        verbose_name = 'Rôle'
        verbose_name_plural = 'Rôles'

    def __str__(self):
        return f"{self.label} ({self.nom})"


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        if not username:
            raise self.model.DoesNotExist
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username.strip()})

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        if 'role' not in extra_fields or extra_fields['role'] is None:
            Role = self.model._meta.get_field('role').remote_field.model
            role_admin, _ = Role.objects.get_or_create(
                nom='admin',
                defaults={'label': 'Administrateur', 'point': 100}
            )
            extra_fields['role'] = role_admin

        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.RESTRICT,
        db_column='id_role',
        null=True,
        blank=True,
        related_name='utilisateurs'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
