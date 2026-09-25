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

    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'prenom', 'numero', 'email', 'role', 'role_id', 'password', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Utilisateur(**validated_data)
        if password:
            user.set_password(password)
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

        user_exists = Utilisateur.objects.filter(email__iexact=email).exists()
        if not user_exists:
            raise serializers.ValidationError({
                'detail': f"Aucun compte associé à l'adresse '{email}'. Les comptes existants sont admin@licencepro.mg ou vendeur@licencepro.mg."
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
