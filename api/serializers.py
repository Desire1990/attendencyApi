from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password


class TokenPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['groups'] = [group.name for group in self.user.groups.all()]
		data['id'] = self.user.id
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name
		# if self.user.utilisateur.agence:
		# 	var = self.user.utilisateur
		# 	data['agence'] = AgenceSerializer(var.agence, many=False).data
		# if self.user.utilisateur.service:
		# 	var = self.user.utilisateur
		# 	data['service'] = ServiceSerializer(var.service, many=False).data
		data['is_staff'] = self.user.is_staff
		return data


class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"
		depth=2


class UserSerializer(serializers.ModelSerializer):
	@transaction.atomic()
	def update(self, instance, validated_data):
		user = instance
		username = validated_data.get('username')
		first_name = validated_data.get('first_name')
		last_name = validated_data.get('last_name')
		nouv_password = validated_data.get('nouv_password')
		anc_password = validated_data.get('anc_password')
		if check_password(anc_password, self.context['request'].user.password):
			if username:
				user.username = username
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if password:
				user.set_password(password)
			user.save()
			return user
		return user

	class Meta:
		model = User
		read_only_fields = "is_active", "is_staff"
		exclude = "last_login", "is_staff", "date_joined"
		extra_kwargs = {
			'username': {
				'validators': [UnicodeUsernameValidator()]
			}
		}



class AgenceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Agence
		fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Service
		fields = "__all__"


class UtilisateurSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		user = User.objects.get(id=instance.user.id)
		group = [group.name for group in user.groups.all()]
		representation['user'] = {'id': user.id, 'username': user.username,
								  'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'groups': group}
		representation['service'] = ServiceSerializer(instance.service, many=False).data
		representation['agence'] = AgenceSerializer(instance.agence, many=False).data
		return representation
	user = UserSerializer()


	@transaction.atomic
	def create(self, validated_data):
		user_data = validated_data.pop('user')
		user = User(
			username = user_data['username'],
			first_name = user_data['first_name'],
			last_name = user_data['last_name'],
			email = user_data['email'],
		)
		password = user_data['password']
		user.is_active = True
		user.set_password(password)

		employe = Employe(
			user = user,
			service = self.validated_data["service"],
			agence = self.validated_data["agence"],
			matricule = self.validated_data["matricule"],
			date_naissance = self.validated_data["date_naissance"],
		)
		user.save()
		employe.save()
		return employe

	class Meta:
		model = Employe
		fields = "__all__"


class PasswordResetSerializer(serializers.Serializer):
	reset_code = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)


class AttendanceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Presence
		fields = ('id', 'user', 'date', 'first_in', 'last_out', 'status', 'hours', 'is_approved')
		depth = 1

class LeaveSerializer(serializers.ModelSerializer):

	def to_representation(self, obj):
		representation = super(LeaveSerializer, self).to_representation(obj)
		representation['user'] = str(obj.user)
		return representation
	class Meta:
		model = Conge
		fields=('id','user', 'date_de_fin', 'date_de_debut', 'statut','type_de_conge','jours_par_defaut','sold', 'raison', 'is_approved')
		# fields = '__all__'
		# depth=1


class QuotationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Quotation
		fields = '__all__'
		depth=1
