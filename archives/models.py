from django.db import models
from django.core.exceptions import ValidationError

# definition des roles
class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # # Ajout d'un niveau hiérarchique pour les permissions
    # niveau = models.IntegerField(default=1, help_text="Niveau hiérarchique (1 = le plus élevé)")
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['nom']

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
    # superficie = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
    #                                 help_text="Superficie en m²")
    # climatisee = models.BooleanField(default=False)
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
    # hauteur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
    #                              help_text="Hauteur en cm")
    # largeur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
    #                              help_text="Largeur en cm")
    # profondeur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
    #                                 help_text="Profondeur en cm")
    
    # Identification
    code_barres = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # qr_code = models.TextField(blank=True, help_text="QR code en format texte ou URL")
    
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
    # hauteur_sol = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
    #                                  help_text="Hauteur par rapport au sol en cm")
    
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
            ('CONSERVER', 'Archiver définitivement'),
            ('ELIMINER', 'Élimination'),
            
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
        




class Boitier(models.Model):
    """
    Boîtier d'archives - conteneur physique de dossiers
    Correspond à l'entité 'Boitier' du diagramme
    """
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('PLEIN', 'Plein'),
        ('ARCHIVE', 'Archivé'),
        ('EN_TRANSFERT', 'En transfert'),
        ('EN_PREPARATION', 'En préparation'),
    ]
    
    # Identifiants (correspond à idboit du diagramme)
    idboit = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="ID Boîtier",
        help_text="Identifiant unique du boîtier (ex: BOX-2024-001)"
    )
    
    code_barre = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Code-barres",
        help_text="Code-barres unique pour scan"
    )
    
    # Métadonnées (correspond au diagramme)
    titre = models.CharField(
        max_length=200,
        verbose_name="Titre",
        help_text="Titre descriptif du boîtier"
    )
    
    capacite = models.IntegerField(
        verbose_name="Capacité",
        help_text="Nombre maximum de dossiers que peut contenir le boîtier"
    )
    
    # Relations avec les classes existantes
    armoire = models.ForeignKey(
        'Armoire',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boitiers',
        verbose_name="Armoire"
    )
    
    etagere = models.ForeignKey(
        'Etagere',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boitiers',
        verbose_name="Étagère"
    )
    
    # Statut 
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIF',
        verbose_name="Statut"
    )
    
    # Dates de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    class Meta:
        verbose_name = "Boîtier"
        verbose_name_plural = "Boîtiers"
        ordering = ['idboit']
        indexes = [
            models.Index(fields=['idboit']),
            models.Index(fields=['code_barre']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.idboit} - {self.titre}"

    # ========== MÉTHODES MÉTIER ==========

    def calculer_taux_remplissage(self):
        """
        Calcule le taux de remplissage du boîtier
        Correspond à 'tauxRemplissage' du diagramme
        """
        total_dossiers = self.dossiers.count()
        if self.capacite > 0:
            return (total_dossiers / self.capacite) * 100
        return 0

    @property
    def taux_remplissage(self):
        """Propriété pour accéder facilement au taux"""
        return self.calculer_taux_remplissage()

    def est_plein(self):
        """Vérifie si le boîtier est plein"""
        return self.dossiers.count() >= self.capacite

    def ajouter_dossier(self, dossier):
        """
        Ajoute un dossier au boîtier
        Vérifie la capacité et met à jour le statut
        """
        if self.est_plein():
            return False, "Le boîtier est plein"
        
        dossier.boitier = self
        dossier.save()
        
        # Mettre à jour le statut si plein
        if self.est_plein():
            self.statut = 'PLEIN'
            self.save()
        
        return True, f"Dossier {dossier.reference} ajouté"

    def retirer_dossier(self, dossier):
        """
        Retire un dossier du boîtier
        """
        if dossier.boitier != self:
            return False, "Ce dossier n'est pas dans ce boîtier"
        
        dossier.boitier = None
        dossier.save()
        
        # Mettre à jour le statut
        if self.statut == 'PLEIN':
            self.statut = 'ACTIF'
            self.save()
        
        return True, f"Dossier {dossier.reference} retiré"

    def localisation_complete(self):
        """
        Retourne la localisation complète du boîtier
        """
        if self.armoire and self.etagere:
            return (f"{self.armoire.salle.batiment.nom} > "
                   f"{self.armoire.salle.nom} > "
                   f"{self.armoire.code} > "
                   f"Étagère {self.etagere.numero} > "
                   f"Boîtier {self.idboit}")
        return "Non localisé"
    



class Dossier(models.Model):
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('CLOS', 'Clos'),
        ('TRANSFERE', 'Transféré'),
        ('DETRUIT', 'Détruit'),
    ]
    
    # Identifiants
    idDossier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID Dossier",
        help_text="Identifiant unique du dossier (ex: DOS-2024-001)"
    )
    
    reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Référence",
        help_text="Référence administrative du dossier"
    )
    
    # Métadonnées
    titre = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Relations
    boitier = models.ForeignKey(
        'Boitier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dossiers',
        verbose_name="Boîtier"
    )
    
    phase_archive = models.ForeignKey(
        'PhaseArchive',
        on_delete=models.PROTECT,
        related_name='dossiers',
        verbose_name="Phase d'archive"
    )
    
    # Dates (correspond au diagramme)
    date_creation = models.DateField(
        verbose_name="Date de création",
        help_text="Date de création du dossier"
    )
    
    date_cloture = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de clôture"
    )
    
    # Gestion
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIF',
        verbose_name="Statut"
    )
    
    niveau_confidentialite = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'Public'),
            ('INTERNE', 'Interne'),
            ('CONFIDENTIEL', 'Confidentiel'),
            ('SECRET', 'Secret'),
        ],
        default='INTERNE',
        verbose_name="Niveau de confidentialité"
    )
    
    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['reference']
        indexes = [
            models.Index(fields=['idDossier']),
            models.Index(fields=['reference']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.titre}"

    # ========== MÉTHODES MÉTIER ==========

    def nombre_documents(self):
        """Retourne le nombre de documents dans le dossier"""
        return self.documents.count()

    def ajouter_document(self, document):
        """
        Ajoute un document au dossier
        Correspond à 'ajouterDoc()' du diagramme
        """
        document.dossier = self
        document.save()
        return True, f"Document {document.reference} ajouté"

    def volume_total(self):
        """Calcule le volume total des documents (taille)"""
        total = sum(doc.taille_fichier or 0 for doc in self.documents.all())
        return total

    def peut_etre_transfere(self):
        """Vérifie si le dossier peut être transféré"""
        # Un dossier peut être transféré si tous ses documents sont prêts
        return all(doc.est_transferable() for doc in self.documents.all())

    def lier_boitier(self, boitier):
        """Lie le dossier à un boîtier"""
        if boitier.est_plein():
            return False, "Le boîtier est plein"
        
        self.boitier = boitier
        self.save()
        boitier.ajouter_dossier(self)  # Met à jour le taux de remplissage
        return True, f"Dossier lié au boîtier {boitier.idboit}"
    


# documents/models.py (ou ajoutez dans votre models.py existant)

from django.utils import timezone
from datetime import timedelta
import hashlib
import os

class Document(models.Model):
    """
    Document d'archive - unité documentaire de base
    Correspond à l'entité 'Document' du diagramme
    """
    
    NIV_CONFIDENTIALITE = [
        ('PUBLIC', 'Public'),
        ('INTERNE', 'Interne'),
        ('CONFIDENTIEL', 'Confidentiel'),
        ('SECRET', 'Secret'),
    ]
    
    TYPE_DOCUMENT = [
        ('CONTRAT', 'Contrat'),
        ('FACTURE', 'Facture'),
        ('RAPPORT', 'Rapport'),
        ('COURRIER', 'Courrier'),
        ('FORMULAIRE', 'Formulaire'),
        ('AUTRE', 'Autre'),
    ]
    
    # Identifiants (correspond au diagramme)
    idDoc = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID Document",
        help_text="Identifiant unique du document"
    )
    
    reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Référence"
    )
    
    titre = models.CharField(
        max_length=500,
        verbose_name="Titre"
    )
    
    # Relations
    dossier = models.ForeignKey(
        'Dossier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Dossier"
    )
    
    phase_archive = models.ForeignKey(
        'PhaseArchive',
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name="Phase d'archive"
    )
    
    # Métadonnées (correspond au diagramme)
    date_creation = models.DateField(
        verbose_name="Date de création"
    )
    
    niv_confidentialite = models.CharField(
        max_length=20,
        choices=NIV_CONFIDENTIALITE,
        default='INTERNE',
        verbose_name="Niveau de confidentialité"
    )
    
    version = models.IntegerField(
        default=1,
        verbose_name="Version",
        help_text="Numéro de version du document"
    )
    
    # Informations complémentaires
    type_document = models.CharField(
        max_length=20,
        choices=TYPE_DOCUMENT,
        default='AUTRE'
    )
    
    auteur = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Auteur"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Fichier
    fichier = models.FileField(
        upload_to='documents/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fichier"
    )
    
    taille_fichier = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Taille (octets)"
    )
    
    hash_fichier = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Hash SHA-256"
    )
    
    # Dates système
    date_entree = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'entrée"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # Historique
    historique_versions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Historique des versions"
    )
    
    historique_consultations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Historique des consultations"
    )
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-date_creation', 'reference']
        indexes = [
            models.Index(fields=['idDoc']),
            models.Index(fields=['reference']),
            models.Index(fields=['phase_archive']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.titre}"

    # ========== MÉTHODES MÉTIER ==========

    def modifier_version(self, nouveau_fichier, utilisateur=None, commentaire=""):
        """
        Crée une nouvelle version du document
        Correspond à 'modifierVersion()' du diagramme
        """
        # Sauvegarder l'ancienne version
        ancienne_version = {
            'version': self.version,
            'fichier': self.fichier.name if self.fichier else None,
            'date': str(timezone.now()),
            'utilisateur': utilisateur.username if utilisateur else 'Système',
            'commentaire': commentaire
        }
        
        self.historique_versions.append(ancienne_version)
        
        # Mettre à jour avec la nouvelle version
        self.version += 1
        self.fichier = nouveau_fichier
        self.date_modification = timezone.now()
        
        # Calculer le hash du nouveau fichier
        if nouveau_fichier:
            self.taille_fichier = nouveau_fichier.size
            self.hash_fichier = self._calculer_hash(nouveau_fichier)
        
        self.save()
        return True, f"Nouvelle version {self.version} créée"

    def _calculer_hash(self, fichier):
        """Calcule le hash SHA-256 d'un fichier"""
        sha256 = hashlib.sha256()
        for chunk in fichier.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()

    def changer_phase(self, nouvelle_phase, utilisateur=None, commentaire=""):
        """
        Change la phase d'archive du document
        Correspond à 'changerPhase()' du diagramme
        """
        ancienne_phase = self.phase_archive
        
        if ancienne_phase == nouvelle_phase:
            return False, "Document déjà dans cette phase"
        
        # Vérifier si la transition est autorisée
        if ancienne_phase.phase_suivante and ancienne_phase.phase_suivante != nouvelle_phase:
            return False, f"Transition non autorisée"
        
        # Mettre à jour la phase
        self.phase_archive = nouvelle_phase
        self.save()
        
        # Mettre à jour le dossier parent si nécessaire
        if self.dossier.phase_archive != nouvelle_phase:
            self.dossier.phase_archive = nouvelle_phase
            self.dossier.save()
        
        return True, f"Document passé en phase {nouvelle_phase.nom}"

    def consulter(self, utilisateur=None):
        """
        Enregistre une consultation du document
        Correspond à 'Consulter()' du diagramme
        """
        consultation = {
            'date': str(timezone.now()),
            'utilisateur': utilisateur.username if utilisateur else 'Anonyme',
            'ip': None  # À remplir si disponible
        }
        
        self.historique_consultations.append(consultation)
        self.save(update_fields=['historique_consultations'])
        
        return True

    def verifier_expiration(self):
        """
        Vérifie si le document a dépassé sa durée de conservation
        Délègue à la phase
        """
        from django.utils import timezone
        date_expiration = self.date_creation + timedelta(
            days=self.phase_archive.duree_conservation * 365
        )
        return timezone.now().date() > date_expiration

    def jours_restants(self):
        """Calcule les jours restants avant expiration"""
        date_expiration = self.date_creation + timedelta(
            days=self.phase_archive.duree_conservation * 365
        )
        delta = date_expiration - timezone.now().date()
        return delta.days

    def est_transferable(self):
        """Détermine si le document peut être transféré"""
        return self.jours_restants() <= 0

    def action_recommandee(self):
        """Retourne l'action recommandée"""
        if self.verifier_expiration():
            if self.phase_archive.phase_suivante:
                return f"Transférer vers {self.phase_archive.phase_suivante.nom}"
            return self.phase_archive.action_finale
        return f"Conserver ({self.jours_restants()} jours restants)"