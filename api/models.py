from django.db import models
import random
from django.utils import timezone
import datetime
import time
from django.contrib.auth.models import User

STATUS = (
	('PRESENT', 'PRESENT'),
	('ABSENT', 'ABSENT')
)
GENDER = (
	('Homme','Homme'),
	('Femme','Femme')
	)

EDUCATIONAL_LEVEL = (
	('Lycee','Lycee'),
	('Ecole Primaire','Ecole Primaire'),
	('Tertiaire/Universite/Polytechnique','Tertiaire/Universite/Polytechnique'),
	('0 niveau','0 niveau'),
	)

LEAVE_TYPE = (
	('Conge de maladie','Conge de maladie'),
	('Conge annuelle','Conge annuelle'),
	('Conge circonstance','Conge circonstance'),
	('Conge prénatal','Conge prénatal'),
	('Conge postnatal','Conge postnatal'),
	('Conge d\'etude','Conge d\'etude'),
)

class Agence(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=200, unique=True)
	description = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.nom}'

class Service(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=125, unique=True)
	description = models.CharField(max_length=125)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


	def __str__(self):
		return self.nom

class Employe(models.Model):
	STATUS = (
		('Marié','Marié'),
		('Celibataire','Celibataire'),
		('Divorcé','Divorcé'),
		# ('WIDOW','Widow'),
		# ('WIDOWER','Widower'),
		)
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	agence = models.ForeignKey(Agence, on_delete=models.CASCADE)
	avatar  = models.ImageField(null=True, blank=True)
	is_valid = models.BooleanField(default = False)
	service = models.ForeignKey(Service,on_delete=models.CASCADE, null=True)
	mobile = models.CharField(max_length=15)
	matricule = models.IntegerField(unique=True)
	status = models.CharField(max_length=20,choices=STATUS)
	addresse = models.CharField(max_length=100)
	genre = models.CharField(choices=GENDER, max_length=10)
	joined = models.DateTimeField(default=timezone.now, editable=False)
	date_naissance = models.DateField(blank=False,null=False)
	education = models.CharField(help_text='niveau d\'éducation le plus élevé, c\'est-à-dire. votre dernier niveau de scolarité',max_length=200,choices=EDUCATIONAL_LEVEL)
	fingerprint = models.CharField(max_length=10000)
	def __str__(self):

		return f'{self.user.username}' 

   

class Presence (models.Model):
	id = models.SmallAutoField(primary_key=True)
	employe = models.ForeignKey(Employe, on_delete=models.CASCADE, null=True)
	date_de_debut = models.DateTimeField(blank=True, null=True)
	date_de_fin = models.DateTimeField(blank=True, null=True)
	Apprové_par = models.CharField(max_length = 50, help_text = 'Approved by ...')
	hours = models.FloatField(blank=True, null=True, editable=False)

	def save(self, *args, **kwargs):
		if self.date_de_debut and self.end_time:
			self.hours = (self.end_time - self.date_de_debut).seconds // 3600
		super(Presence, self).save(*args, **kwargs)


	
	def __str__(self):
		return 'Presence -> '+str(self.hours) +'h'' -> ' + str(self.utilisateur)


class Conge(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
	date_de_debut = models.DateField(help_text='leave start date is on ..',null=True,blank=False)
	date_de_fin = models.DateField(help_text='coming back on ...',null=True,blank=False)
	type_de_conge = models.CharField(choices=LEAVE_TYPE,max_length=25,null=True,blank=False)
	raison = models.CharField(max_length=255,help_text='ajouter des informations supplémentaires pour le congé',null=True,blank=True)
	jours_par_defaut = models.PositiveIntegerField( default=20)
	statut = models.CharField(max_length=12,default='pending') #pending,approved,rejected,cancelled
	is_approved = models.BooleanField(default=False) #hide
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.employe.user.username

class Quotation(models.Model):
	id = models.SmallAutoField(primary_key=True)
	# presence
	employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
	mark = models.FloatField(default=0)

	def __str__(self):
		return self.employe