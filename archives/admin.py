from django.contrib import admin

# Register your models here.
from .models import Armoire, Batiment, Role, Salle, Etagere, PhaseArchive

@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'adresse')  # Colonnes affichées
    search_fields = ('nom', 'code')            # Barre de recherche
    list_filter = ('date_creation',) 
             
@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'batiment', 'etage')
    list_filter = ('batiment', 'type_salle')
    search_fields = ('nom', 'code')

    
admin.site.register(Armoire)
admin.site.register(Etagere)
admin.site.register(PhaseArchive)
admin.site.register(Role)