"""Un connecteur par mode d'accès : le module pipelines/connecteurs/<mode>.py expose metadonnees() et telecharger().

Ajouter un mode = ajouter un fichier ; aucun registre à tenir à jour.
"""

from __future__ import annotations

import importlib
from types import ModuleType


def connecteur(mode: str) -> ModuleType | None:
    try:
        return importlib.import_module(f"{__name__}.{mode.replace('-', '_')}")
    except ModuleNotFoundError:
        return None
