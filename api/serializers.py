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
		if self.user.utilisateur.agence:
			var = self.user.utilisateur
			data['agence'] = AgenceSerializer(var.agence, many=False).data
		if self.user.utilisateur.service:
			var = self.user.utilisateur
			data['service'] = ServiceSerializer(var.service, many=False).data
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
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['user'] = UserSerializer(instance.user, many=False).data
		user = UserSerializer(instance.user, many=False).data
		representation['user'] = {'id': user.get(
			'id'), 'username': user.get('username')}
		return representation

	class Meta:
		model = Agence
		fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['user'] = UserSerializer(instance.user, many=False).data
		representation['agence'] = AgenceSerializer(instance.agence, many=False).data
		return representation

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

	def update(self, instance, validated_data):
		user = instance.user
		print(validated_data)
		user_data = validated_data.pop('user')
		username = user_data.get('username')
		first_name = user_data.get('first_name')
		last_name = user_data.get('last_name')
		email = user_data.get('email')
		password = user_data.get('password')

		if username:
			user.username = username
		if first_name:
			user.first_name = first_name
		if last_name:
			user.last_name = last_name
		if email:
			user.email = email
		if password:
			user.set_password(password)

		instance.departement = validated_data.get('departement', instance.departement)
		instance.agence = validated_data.get('agence', instance.agence)
		group_user = user_data.get('groups')
		print(user)
		print(group_user)
		user.groups.clear()
		user.groups.add(group_user[0])
		user.save()
		instance.save()
		return instance

	class Meta:
		model = Utilisateur
		fields = "__all__"


class PasswordResetSerializer(serializers.Serializer):
	reset_code = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)


class AttendanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Attendance
		# fields = ('id','category','status','unite','status', 'materiel','designation','reference', 'quantite','unite', 'get_absolute_url', 'date_peremption')
		fields = '__all__'
		depth=1


class LeaveSerializer(serializers.ModelSerializer):
	class Meta:
		model = Leave
		# fields = ('id','category','status','unite','status', 'materiel','designation','reference', 'quantite','unite', 'get_absolute_url', 'date_peremption')
		fields = '__all__'
		depth=1


class QuotationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Quotation
		# fields = ('id','category','status','unite','status', 'materiel','designation','reference', 'quantite','unite', 'get_absolute_url', 'date_peremption')
		fields = '__all__'
		depth=1
