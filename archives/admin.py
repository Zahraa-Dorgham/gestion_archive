from django.contrib import admin

# Register your models here.
from .models import Armoire, Batiment, Salle, Etagere, PhaseArchive

admin.site.register(Batiment)
admin.site.register(Salle)
admin.site.register(Armoire)
admin.site.register(Etagere)
admin.site.register(PhaseArchive)