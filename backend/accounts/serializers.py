from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Role, Utilisateur


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'nom', 'label', 'point']


class UtilisateurSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True
    )
    password = serializers.CharField(write_only=True, required=False)
    ventes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'nom', 'prenom', 'numero', 'email', 'role', 'role_id',
            'password', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'ventes_count'
        ]

    def get_ventes_count(self, obj):
        return obj.ventes.count()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Utilisateur(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email', '').strip()
        attrs['email'] = email

        user = Utilisateur.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError({
                'detail': f"Aucun compte associé à l'adresse '{email}'. Veuillez vérifier votre saisie."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                'detail': "Ce compte est en attente d'approbation par l'administrateur. Veuillez contacter votre responsable pour son activation."
            })

        try:
            data = super().validate(attrs)
        except Exception:
            raise serializers.ValidationError({
                'detail': "Mot de passe incorrect pour ce compte."
            })

        user_serializer = UtilisateurSerializer(self.user)
        data['user'] = user_serializer.data
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'prenom', 'numero', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        email = attrs.get('email', '').strip().lower()
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                'email': "Cette adresse email est déjà utilisée par un autre compte."
            })
        attrs['email'] = email
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        # Si aucun administrateur actif n'existe dans le système, le premier compte devient Admin actif
        has_active_admin = Utilisateur.objects.filter(is_superuser=True, is_active=True).exists()

        if not has_active_admin:
            role_obj, _ = Role.objects.get_or_create(
                nom='admin',
                defaults={'label': 'Administrateur', 'point': 50}
            )
            is_staff = True
            is_superuser = True
            is_active = True
        else:
            role_obj, _ = Role.objects.get_or_create(
                nom='media_buyer',
                defaults={'label': 'Media Buyer', 'point': 10}
            )
            is_staff = False
            is_superuser = False
            is_active = False  # En attente d'approbation par l'administrateur

        user = Utilisateur.objects.create_user(
            password=password,
            role=role_obj,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **validated_data
        )
        return user
