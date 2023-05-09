from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Agence)
admin.site.register(Service)
admin.site.register(Employe)
admin.site.register(Presence)
admin.site.register(Conge)
admin.site.register(Quotation)