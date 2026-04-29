# xml_inv_cn_gen

Générateur de factures et avoirs au format **UBL 2.1 / EN 16931**, à partir de données stockées en base SQL Server.

Ce script Python interroge la base `eInvoice`, récupère les entêtes et lignes de documents, puis injecte les valeurs dans des templates XML conformes aux normes européennes de facturation électronique.

---

## Fonctionnalités

- **Factures (Invoice)** et **Avoirs (CreditNote)** — génération à partir d'un même pipeline, avec sélection automatique du template adapté.
- **Processus B2B / B2C** supportés (B2G en réflexion).
- **Pièces jointes** encodées en base64 directement embarquées dans le XML (`EmbeddedDocumentBinaryObject`).
- **Génération unitaire** (par numéro de document) ou **en masse** (tous les documents présents en table).

---

## Arborescence du projet

```
xml_inv_cn_gen/
│
├── _input/
│   ├── backups/
│   ├── base/                    # Templates XML commentés de référence
│   │   ├── UC5_F..._INV_...xml
│   │   └── UC5b_F..._CN_...xml
│   ├── cleaned/                 # Templates XML nettoyés (utilisés en production)
│   │   ├── UC5_INV_EN16931_CLEAN.xml
│   │   └── UC5b_CN_EN16931_CLEAN.xml
│   └── pj_test/                 # Pièces jointes de test
│
├── _output/                     # Fichiers XML générés
│   ├── CreditNote_26140022_C0000010_2026-01-20.xml
│   ├── Invoice_25144441_C0000010_2025-11-27.xml
│   └── ...
│
├── Archive/                     # Anciennes versions / archives
├── generate_in_cn_xml_from_bdd.py   # Script principal
├── requirements.txt
├── .gitignore
└── .venv/
```

---

## Prérequis

- **Python 3.10+**
- **SQL Server** accessible avec authentification Windows (`Trusted_Connection`)
- Base de données `eInvoice` avec les vues :
  - `v_inv_cn_header_python` - données d'entête
  - `v_inv_cn_lines_python` - lignes de document

### Dépendances Python

```
lxml
pyodbc
base64
copy
```

Installation :

```bash
pip install -r requirements.txt
```

> Le driver ODBC *SQL Server* doit être installé sur la machine. (apparement)

---

## Utilisation

### Génération d'un document unique

```python
from generate_in_cn_xml_from_bdd import fact_bdd_to_xml

fact_bdd_to_xml(25144441)  # Facture
fact_bdd_to_xml(26140022)  # Avoir
```

### Génération de tous les documents en table

```python
from generate_in_cn_xml_from_bdd import gen_all_doc_in_table

gen_all_doc_in_table()
```

Les fichiers XML sont écrits dans `_output/` avec la convention de nommage :

```
{TypeDoc}_{DocNum}_{CodeClient}_{IssueDate}.xml
```

---

## Configuration

Les paramètres de connexion et les chemins sont définis en constantes en haut du script :

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

---