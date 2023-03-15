from django.db import models
import random
from django.utils import timezone
import datetime
import time
from django.contrib.auth.models import User

STATUS = (
	('PRESENT', 'PRESENT'),
	('ABSENT', 'ABSENT'),
	('UNAVAILABLE', 'UNAVAILABLE')
)
GENDER = (
	('MALE','Male'),
	('FEMALE','Female')
	)

EDUCATIONAL_LEVEL = (
	('SENIORHIGH','Senior High School'),
	('JUNIORHIGH','Junior High School'),
	('PRIMARY','Primary School'),
	('TERTIARY','Tertiary/University/Polytechnic'),
	('OLEVEL','OLevel'),
	('OTHER','Other'),
	)

LEAVE_TYPE = (
	('SICK','Sick Leave'),
	('CASUAL','Casual Leave'),
	('EMERGENCY','Emergency Leave'),
	('STUDY','Study Leave'),
)

class Agence(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	nom = models.CharField(max_length=200, null=True, blank=False)
	description = models.CharField(max_length=200, null=True, blank=False)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.nom}'

class Service(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	agence=models.ForeignKey(Agence, on_delete=models.CASCADE)
	nom = models.CharField(max_length=125, unique=True)
	description = models.CharField(max_length=125,null=True,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


	def __str__(self):
		return self.nom

class Employe(models.Model):
	STATUS = (
		('MARRIED','Married'),
		('SINGLE','Single'),
		('DIVORCED','Divorced'),
		('WIDOW','Widow'),
		('WIDOWER','Widower'),
		)
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	agence = models.ForeignKey(Agence, on_delete=models.CASCADE)
	avatar  = models.ImageField(null=True, blank=True)
	is_valid = models.BooleanField(default = False)
	service = models.ForeignKey(Service,on_delete=models.CASCADE, null=True)
	mobile = models.CharField(max_length=15)
	status = models.CharField(max_length=10,choices=STATUS,blank=False,null=True)
	addresse = models.CharField(max_length=100, default='')
	genre = models.CharField(choices=GENDER, max_length=10)
	joined = models.DateTimeField(default=timezone.now, editable=False)
	date_naissance = models.DateField(blank=False,null=False)
	education = models.CharField(help_text='highest educational standard ie. your last level of schooling',max_length=20,choices=EDUCATIONAL_LEVEL,blank=False,null=True)
	fingerprint = models.CharField(max_length=10000)
	def __str__(self):

		return f'{self.user.username}' 

   

class Presence (models.Model):
	id = models.SmallAutoField(primary_key=True)
	employe = models.ForeignKey(Employe, on_delete=models.CASCADE, null=True)
	date_de_debut = models.DateTimeField(blank=True, null=True)
	date_de_fin = models.DateTimeField(blank=True, null=True)
	Approved_by = models.CharField(max_length = 50, help_text = 'Approved by ...')
	hours = models.FloatField(blank=True, null=True, editable=False)

	def save(self, *args, **kwargs):
		if self.date_de_debut and self.end_time:
			self.hours = (self.end_time - self.date_de_debut).seconds // 3600
		super(Presence, self).save(*args, **kwargs)


	
	def __str__(self):
		return 'Presence -> '+str(self.hours) +'h'' -> ' + str(self.utilisateur)


class Conge(models.Model):
	id = models.SmallAutoField(primary_key=True)
	employe = models.ForeignKey(Employe,on_delete=models.CASCADE,default=1)
	date_de_debut = models.DateField(help_text='leave start date is on ..',null=True,blank=False)
	date_de_fin = models.DateField(help_text='coming back on ...',null=True,blank=False)
	type_de_conge = models.CharField(choices=LEAVE_TYPE,max_length=25,null=True,blank=False)
	raison = models.CharField(max_length=255,help_text='add additional information for leave',null=True,blank=True)
	jours_par_defaut = models.PositiveIntegerField( null=True,blank=True)
	statut = models.CharField(max_length=12,default='pending') #pending,approved,rejected,cancelled
	is_approved = models.BooleanField(default=False) #hide
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)
	Approved_by = models.CharField(max_length=50, null=True, blank=False)

	def __str__(self):
		return self.employe

class Quotation(models.Model):
	id = models.SmallAutoField(primary_key=True)
	# presence
	employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
	mark = models.FloatField(default=0)

	def __str__(self):
		return self.employe