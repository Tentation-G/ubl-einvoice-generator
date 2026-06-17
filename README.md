# xml_inv_cn_gen

Générateur de factures et avoirs au format **UBL 2.1 / EN 16931**, à partir de données stockées en base SQL Server.

---

## Arborescence du projet

```
xml_inv_cn_gen/
│
├── _input/
│   ├── backups/
│   ├── base/                    # Templates XML commentés de référence
│   ├── cleaned/                 # Templates XML nettoyés (utilisés en production)
│   │   ├── UC5_INV_EN16931_CLEAN.xml
│   │   └── UC5b_CN_EN16931_CLEAN.xml
│   └── default_attachment/      # Pièces jointes a inserer par defaut
│
├── _output/                     # Fichiers XML générés (pour test)
│
├── gui/
│   └── app.py                   # Interface graphique Tkinter
│
├── generate_in_cn_xml_from_bdd.py   # Script principal (logique métier)
├── app_launcher.bat                 # Lanceur portable (double-clic)
├── requirements.txt
└── .gitignore
```

> Le dossier `python3-13_portable/` n'est **pas** versionné (voir `.gitignore`).
> Il doit être reconstitué localement — voir section **Déploiement portable** ci-dessous.

---

## Prérequis système

- **Windows 10/11** 64 bits
- **Microsoft ODBC Driver for SQL Server** installé sur la machine (composant système, indépendant de Python) ( ¯\_(ツ)_/¯ )
- Accès réseau à la base **SQL Server** `eInvoice` avec authentification Windows (`Trusted_Connection`)
- Vues SQL requises :
  - `v_inv_cn_header_python` — données d'entête de inv/cn
  - `v_inv_cn_lines_python`  — lignes de inv/cn

---

## Lancement (mode portable)

Si le dossier `python3-13_portable/` est présent (voir section **Déploiement** ci-dessous), il suffit de double-cliquer sur :

```
app_launcher.bat
```

L'interface graphique s'ouvre directement, sans installation Python sur la machine.

---

## Déploiement portable

Le projet embarque son propre interpréteur Python pour fonctionner sans installation. Le dossier `python3-13_portable/` n'est pas dans le repo : il faut le reconstituer une fois après clonage.

### Étapes

**1. Télécharger WinPython**

Sur [winpython.github.io](https://winpython.github.io/), télécharger **WinPython64-3.13.x.xdot** (version `dot`, la plus légère).  
Dézipper l'archive.

**2. Copier l'interpréteur dans le projet**

Dans le dossier extrait, copier le sous-dossier **`python`** (celui qui contient `python.exe`) à la racine du projet, et le renommer **`python3-13_portable`**.

```
xml_inv_cn_gen/
└── python3-13_portable/
    ├── python.exe
    ├── pythonw.exe
    ├── Lib/
    └── ...
```

**3. Installer les dépendances**

Ouvrir un `cmd` à la racine du projet et lancer :

```
python3-13_portable\python.exe -m pip install -r requirements.txt
```

> Si PyPI est inaccessible (pare-feu), les wheels offline sont disponibles dans `packages/` :
> ```
> python3-13_portable\python.exe -m pip install --no-index --find-links=packages -r requirements.txt
> ```

**4. Tester**

```
python3-13_portable\python.exe gui\app.py
```

Si la fenêtre s'ouvre et que la connexion SQL fonctionne, le déploiement est terminé.  
Pour l'usage quotidien, utiliser `app_launcher.bat` (double-clic).

---

Les fichiers XML sont écrits dans `DOC_OUTPUT_PATH` avec la convention de nommage :

```
{TypeDoc}_{DocNum}_{CodeClient}_{IssueDate}.xml
```

---

## Configuration

Les paramètres de connexion et les chemins sont définis en constantes en haut de `generate_in_cn_xml_from_bdd.py` :

| Variable | Description |
|---|---|
| `SERVER_NAME` | Nom du serveur SQL Server |
| `DATABASE_NAME` | Base de données cible |
| `DOC_INPUT_PATH` | Dossier des templates XML nettoyés |
| `DOC_OUTPUT_PATH` | Dossier de sortie des XML générés |
| `ATTACHMENT_INPUT_PATH` | Dossier des pièces jointes à embarquer |

---

## Norme et conformité

Les documents générés suivent le profil **EN 16931** (norme européenne de facturation électronique) au format **UBL 2.1**, avec les namespaces :

- `cac` — `urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2`
- `cbc` — `urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2`

Les champs sont préfixés selon la nomenclature **BT** (Business Term) du standard EN 16931.