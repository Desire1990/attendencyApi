from django.db import models
import random
from django.utils import timezone
from datetime import datetime, timedelta
import time
from django.contrib.auth.models import User

STATUS = (
	('PRESENT', 'PRESENT'),
	('ABSENT', 'ABSENT')
)
CONGE = (
	('pending','pending'),
	('approved', 'approved'),
	('rejected', 'rejected'),
	('cancelled', 'cancelled')
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


class Service(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=125, unique=True)
	description = models.CharField(max_length=125)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nom

class Agence(models.Model):
	id = models.SmallAutoField(primary_key=True)
	nom = models.CharField(max_length=200, unique=True)
	description = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.nom}'


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
	service = models.ForeignKey(Service,on_delete=models.CASCADE, null=True)
	matricule = models.IntegerField(unique=True)
	# avatar  = models.ImageField(null=True, blank=True)
	is_valid = models.BooleanField(default = False)
	# mobile = models.CharField(max_length=15)
	# status = models.CharField(max_length=20,choices=STATUS)
	# addresse = models.CharField(max_length=100)
	# genre = models.CharField(choices=GENDER, max_length=10)
	joined = models.DateTimeField(default=timezone.now, editable=False)
	date_naissance = models.DateField(blank=False,null=False)
	# education = models.CharField(help_text='niveau d\'éducation le plus élevé, c\'est-à-dire. votre dernier niveau de scolarité',max_length=200,choices=EDUCATIONAL_LEVEL)
	# fingerprint = models.CharField(max_length=10000)
	def __str__(self):

		return f'{self.user.username}' 

   

class Presence (models.Model):
	STATUS = (('PRESENT', 'PRESENT'), ('ABSENT', 'ABSENT'),('UNAVAILABLE', 'UNAVAILABLE'))
	id = models.SmallAutoField(primary_key=True)
	date = models.DateField(auto_now_add=True)
	first_in = models.TimeField()
	last_out = models.TimeField(null=True)
	status = models.CharField(choices=STATUS, max_length=15 )
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	# staff = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
	hours = models.TimeField(blank=True, null=True, editable=False)
	is_approved = models.BooleanField(default=False)


	def __str__(self):
		return 'Presence -> '+str(self.hours) +'h'' -> ' + str(self.user)

	class Meta:
		ordering = ('-date',)


class Conge(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	date_de_debut = models.DateField(help_text='leave start date is on ..',null=True,blank=False)
	date_de_fin = models.DateField(help_text='coming back on ...',null=True,blank=False)
	type_de_conge = models.CharField(choices=LEAVE_TYPE,max_length=25,null=True,blank=False)
	raison = models.CharField(max_length=255,help_text='ajouter des informations supplémentaires pour le congé',null=True,blank=True)
	sold = models.IntegerField(blank=True, default=20, editable=False)
	jours_par_defaut = models.IntegerField(blank=True, null=True, editable=False)
	statut = models.CharField(max_length=12, choices=CONGE, default='pending') #pending,approved,rejected,'cancelled'
	is_approved = models.BooleanField(default=False) #hide
	created = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.user.username


	# @property
	# def date_diff(self):
	# 	diff = 
	# 	if self.type_de_conge == 'Conge annuelle':
	# 		return (str(self.date_de_fin - self.date_de_debut)).days

    # def whenpublished(self):
    #     now = timezone.now()
        
    #     diff= now - self.pub_date

    #     if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
    #         seconds= diff.seconds
            
    #         if seconds == 1:
    #             return str(seconds) +  "second ago"
            
    #         else:
    #             return str(seconds) + " seconds ago"

            

    #     if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
    #         minutes= math.floor(diff.seconds/60)

    #         if minutes == 1:
    #             return str(minutes) + " minute ago"
            
    #         else:
    #             return str(minutes) + " minutes ago"



    #     if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
    #         hours= math.floor(diff.seconds/3600)

    #         if hours == 1:
    #             return str(hours) + " hour ago"

    #         else:
    #             return str(hours) + " hours ago"

        # # 1 day to 30 days
        # if diff.days >= 1 and diff.days < 30:
        #     days= diff.days
        
        #     if days == 1:
        #         return str(days) + " day ago"

        #     else:
        #         return str(days) + " days ago"

        # if diff.days >= 30 and diff.days < 365:
        #     months= math.floor(diff.days/30)
            

        #     if months == 1:
        #         return str(months) + " month ago"

        #     else:
        #         return str(months) + " months ago"


        # if diff.days >= 365:
        #     years= math.floor(diff.days/365)

        #     if years == 1:
        #         return str(years) + " year ago"

        #     else:
        #         return str(years) + " years ago"





class Quotation(models.Model):
	id = models.SmallAutoField(primary_key=True)
	# presence
	employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
	mark = models.FloatField(default=0)

	def __str__(self):
		return self.employe