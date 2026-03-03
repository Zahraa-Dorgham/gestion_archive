from django.db import models
from django.core.exceptions import ValidationError

# definition des roles
class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Ajout d'un niveau hiérarchique pour les permissions
    niveau = models.IntegerField(default=1, help_text="Niveau hiérarchique (1 = le plus élevé)")
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['niveau', 'nom']

    def __str__(self):
        return self.nom


# classe batiment
class Batiment(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, 
                           help_text="Code unique du bâtiment (ex: B001)")
    adresse = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bâtiment"
        verbose_name_plural = "Bâtiments"
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}" if self.code else self.nom


# classe salle
class Salle(models.Model):
    TYPE_SALLE = [
        ('ARCHIVE', "Salle d'archive"),
        ('CONSULTATION', 'Salle de consultation'),
        ('TRI', 'Salle de tri'),
        ('NUMERISATION', 'Salle de numérisation'),
    ]
    
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True,
                           help_text="Code unique de la salle (ex: S001)")
    batiment = models.ForeignKey(
        Batiment,
        on_delete=models.CASCADE,
        related_name='salles'
    )
    type_salle = models.CharField(max_length=20, choices=TYPE_SALLE, default='ARCHIVE')
    etage = models.IntegerField(default=0)
    superficie = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                    help_text="Superficie en m²")
    climatisee = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ['batiment', 'nom']
        unique_together = ['batiment', 'nom']  # Évite les doublons dans un même bâtiment

    def __str__(self):
        return f"{self.code} - {self.nom}" if self.code else f"{self.nom} - {self.batiment.nom}"



class Armoire(models.Model):
    """Armoire de rangement contenant des étagères"""
    
    TYPE_ARMOIRE = [
        ('METAL', 'Métallique'),
        ('BOIS', 'Bois'),
        ('COMPACT', 'Compact à rayonnages mobiles'),
        ('MURAL', 'Mural'),
    ]
    
    code = models.CharField(max_length=50, unique=True, 
                           help_text="Code unique de l'armoire (ex: ARM-001)")
    type_armoire = models.CharField(max_length=20, choices=TYPE_ARMOIRE, default='METAL')
    salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE,
        related_name='armoires'
    )
    
    # Caractéristiques physiques
    hauteur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 help_text="Hauteur en cm")
    largeur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 help_text="Largeur en cm")
    profondeur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                    help_text="Profondeur en cm")
    
    # Identification
    code_barres = models.CharField(max_length=100, unique=True, null=True, blank=True)
    qr_code = models.TextField(blank=True, help_text="QR code en format texte ou URL")
    
    # Métadonnées
    description = models.TextField(blank=True)
    date_installation = models.DateField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Armoire"
        verbose_name_plural = "Armoires"
        ordering = ['salle', 'code']

    def __str__(self):
        return f"{self.code} - {self.get_type_armoire_display()} - {self.salle.code}"

    def nombre_etageres(self):
        """Retourne le nombre d'étagères dans cette armoire"""
        return self.etageres.count()


class Etagere(models.Model):
    """Étagère située dans une armoire"""
    
    armoire = models.ForeignKey(
        Armoire,
        on_delete=models.CASCADE,
        related_name='etageres'
    )
    
    numero = models.IntegerField(help_text="Numéro de l'étagère dans l'armoire")
    code_barres = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # Capacité
    capacite_max_boites = models.IntegerField(default=10, 
                                             help_text="Nombre maximum de boîtes")
    occupation_actuelle = models.IntegerField(default=0,
                                             help_text="Nombre de boîtes actuellement")
    
    # Position
    hauteur_sol = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                     help_text="Hauteur par rapport au sol en cm")
    
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Étagère"
        verbose_name_plural = "Étagères"
        ordering = ['armoire', 'numero']
        unique_together = ['armoire', 'numero']  # Empêche les doublons de numéro dans une même armoire

    def __str__(self):
        return f"{self.armoire.code} - Étagère {self.numero}"

    def taux_occupation(self):
        """Calcule le taux d'occupation de l'étagère"""
        if self.capacite_max_boites > 0:
            return (self.occupation_actuelle / self.capacite_max_boites) * 100
        return 0

    def est_pleine(self):
        """Vérifie si l'étagère est pleine"""
        return self.occupation_actuelle >= self.capacite_max_boites

    def ajouter_boite(self):
        """Ajoute une boîte à l'étagère si possible"""
        if not self.est_pleine():
            self.occupation_actuelle += 1
            self.save()
            return True
        return False




# classe phase d'archivage
class PhaseArchive(models.Model):
    TYPE_PHASE = [
        ('COURANTE', 'Archive courante'),
        ('INTERMEDIAIRE', 'Archive intermédiaire'),
        ('DEFINITIVE', 'Archive définitive'),
        ('HISTORIQUE', 'Archive historique'),
    ]
    
    nom = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    type_phase = models.CharField(max_length=20, choices=TYPE_PHASE, default='COURANTE')
    duree_conservation = models.IntegerField(help_text="Durée en années")
    description = models.TextField(blank=True)
    
    # Relations entre phases
    phase_suivante = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Phase suivante dans le cycle de vie"
    )
    
    # Règles de disposition finale
    action_finale = models.CharField(
        max_length=20,
        choices=[
            ('CONSERVER', 'Conservation permanente'),
            ('ELIMINER', 'Élimination'),
            ('VERSER', 'Versement aux archives historiques'),
        ],
        default='ELIMINER'
    )
    
    ordre = models.IntegerField(default=0, help_text="Ordre dans le cycle de vie")
    
    class Meta:
        verbose_name = "Phase d'archivage"
        verbose_name_plural = "Phases d'archivage"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.duree_conservation} ans)"

    def clean(self):
        """Empêche une phase d'être sa propre phase suivante"""
        if self.phase_suivante and self.phase_suivante.pk == self.pk:
            raise ValidationError("Une phase ne peut pas être sa propre phase suivante")