from django.db import models
import random
from django.utils import timezone
import datetime
import time
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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


class Service(models.Model):
	id = models.SmallAutoField(primary_key=True)
	name = models.CharField(max_length=125, unique=True)
	description = models.CharField(max_length=125,null=True,blank=True)
	created = models.DateTimeField(verbose_name=_('Created'),auto_now_add=True)
	updated = models.DateTimeField(verbose_name=_('Updated'),auto_now=True)


	def __str__(self):
		return self.name

class Utilisateur(models.Model):
	STATUS = (
		('MARRIED','Married'),
		('SINGLE','Single'),
		('DIVORCED','Divorced'),
		('WIDOW','Widow'),
		('WIDOWER','Widower'),
		)
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar  = models.ImageField(null=True, blank=True)
	is_valid = models.BooleanField(default = False)
	service = models.ForeignKey(Service,on_delete=models.CASCADE, null=True)
	mobile = models.CharField(max_length=15)
	status = models.CharField(_('Marital Status'),max_length=10,choices=STATUS,blank=False,null=True)
	address = models.CharField(max_length=100, default='')
	gender = models.CharField(choices=GENDER, max_length=10)
	joined = models.DateTimeField(default=timezone.now, editable=False)
	birthday = models.DateField(_('Birthday'),blank=False,null=False)
	education = models.CharField(_('Education'),help_text='highest educational standard ie. your last level of schooling',max_length=20,choices=EDUCATIONAL_LEVEL,blank=False,null=True)
	fingerprint = models.CharField(max_length=1000, null=False, blank=False)
	def __str__(self):

		return f'{self.user.username}' 

   

class Attendance (models.Model):
	id = models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True)
	start_time = models.DateTimeField(blank=True, null=True)
	end_time = models.DateTimeField(blank=True, null=True)
	Approved_by = models.CharField(max_length = 50, help_text = 'Approved by ...')
	hours = models.FloatField(blank=True, null=True, editable=False)

	def save(self, *args, **kwargs):
		if self.start_time and self.end_time:
			self.hours = (self.end_time - self.start_time).seconds // 3600
		super(Attendance, self).save(*args, **kwargs)


	
	def __str__(self):
		return 'Attendance -> '+str(self.hours) +'h'' -> ' + str(self.utilisateur)


class Leave(models.Model):
	id = models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE,default=1)
	startdate = models.DateField(verbose_name=_('Start Date'),help_text='leave start date is on ..',null=True,blank=False)
	enddate = models.DateField(verbose_name=_('End Date'),help_text='coming back on ...',null=True,blank=False)
	leavetype = models.CharField(choices=LEAVE_TYPE,max_length=25,null=True,blank=False)
	reason = models.CharField(verbose_name=_('Reason for Leave'),max_length=255,help_text='add additional information for leave',null=True,blank=True)
	defaultdays = models.PositiveIntegerField(verbose_name=_('Leave days per year counter'), null=True,blank=True)
	status = models.CharField(max_length=12,default='pending') #pending,approved,rejected,cancelled
	is_approved = models.BooleanField(default=False) #hide
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)
	Approved_by = models.CharField(max_length=50, null=True, blank=False)

	def __str__(self):
		return self.utilisateur

class Quotation(models.Model):
	id = models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
	mark = models.FloatField(default=0)

	def __str__(self):
		return self.utilisateur