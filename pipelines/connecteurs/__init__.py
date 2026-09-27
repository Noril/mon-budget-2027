from . import fichier, opendatasoft, sdmx

# mode d'accès du catalogue -> module connecteur (metadonnees, telecharger)
CONNECTEURS = {
    "opendatasoft": opendatasoft,
    "fichier": fichier,
    "sdmx": sdmx,
}
