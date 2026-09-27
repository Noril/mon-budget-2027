from . import fichier, opendatasoft

# mode d'accès du catalogue -> module connecteur (metadonnees, telecharger)
CONNECTEURS = {
    "opendatasoft": opendatasoft,
    "fichier": fichier,
}
