from lxml import etree
import base64
import pyodbc
import copy

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from pyodbc import Row

SERVER_NAME   = "FR-SD-SQLDIV"
DATABASE_NAME = "eInvoice"
ETL           = "v_inv_cn_header_python"

INPUT_PATH            = os.path.join(BASE_DIR, "_input/")
DOC_INPUT_PATH        = os.path.join(INPUT_PATH, "cleaned/")
ATTACHMENT_INPUT_PATH = os.path.join(INPUT_PATH, "pj_test/")

#DOC_OUTPUT_PATH = os.path.join(BASE_DIR, "_output/")
DOC_OUTPUT_PATH = "C:/Users/campeauxfl/WILO/Wilo_SESEM-IT-PROJETS-eINVOICING - ICD Wilo Sesem - Documents/PRE_PROD_SOURCES_DEPOT/ICD_out/FR-DE-SESEM_e_invoice/QUALITY/OUT_TO_ICD/e_invoice/"

INVOICE_TEMPLATE_INPUT     = DOC_INPUT_PATH + "UC5_INV_EN16931_CLEAN.xml"
CREDIT_NOTE_TEMPLATE_INPUT = DOC_INPUT_PATH + "UC5b_CN_EN16931_CLEAN.xml"

ATTACHMENT_INPUT = "_attachment/"

# TODO : Case Chorus (B2G ? besoin champ additionnels ?)

## Back Pour visu table en front
def fetch_all_header_columns() -> list[str]:
    """
    Récupère les noms de colonnes d'entêtes des facture en base {SERVER_NAME} du serveur {DATABASE_NAME}

    :param None:
        Select de rien sur la table, ne prends que les metaDonnées (les noms de colonnes
    :return list[str]:
        Liste des noms de colonnes
    """

    connH = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
    )

    cursorH = connH.cursor()

    cursorH.execute(f"""
        SELECT
              [Control_DocNum]
            , [Control_CodeCient]
            , [Control_NomClient]
            , [Control_CodeTVA]
            --, [Control_Siret]
            , [BT115_FA_LegalMonetaryTotal_PayableAmount]
        FROM [eInvoice].[dbo].[{ETL}]
        WHERE 1 = 0
    """)

    colonnes = [column[0] for column in cursorH.description]

    connH.close()

    return colonnes

def fetch_all_header() -> list[pyodbc.Row]:
    """
    Récupère toute les ligne d'entêtes des facture en base {SERVER_NAME} du serveur {DATABASE_NAME}

    :param None:
        Maxi select de la base -> visu tableau de l'app
    :return rowH:
        objet pyodbc.Row : colonnes de la ligne d'entête
    """

    connH = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
    )

    cursorH = connH.cursor()
    cursorH.execute(f"""
                    SELECT
                        [Control_TypeDoc]
                            , [Control_DocNum]
                            , [Control_CodeCient]
                            , [Control_NomClient]
                            , [Control_CodeTVA]
                            , [Control_Siret]
                            , [Control_Process_B2B_B2C_B2G_eRephorsFR]
                            , [Control_TVA_Piece]
                            , [Control_TVA_Taux]
                            , [Control_StatTiersFamille]
                            , [Control_StatTiersWiloRepp]
                            , [Control_DestFacture]
                            , [Control_DestFacture_Email]
                            , [UBL_FA_XML_Encode]
                            , [UBL_FA_SpecSchema]
                            , [BT0_FA_UBLVersionID]
                            , [BT24_FA_CustomizationID]
                            , [BT23_FA_ProfileID]
                            , [BT1_FA_ID]
                            , [BT2_FA_IssueDate]
                            , [BT9_F_DueDate]
                            , [BT3_FA_InvoiceCreditNoteTypeCode]
                            , [BT22_FA_Note_REG]
                            , [BT22_FA_Note_ABL]
                            , [BT22_FA_Note_AAI]
                            , [BT22_FA_Note_PMD]
                            , [BT22_FA_Note_PMT]
                            , [BT22_FA_Note_AAB]
                            , [BT22_FA_Note_BAR]
                            , [BT5_FA_DocumentCurrencyCode]
                            , [BT19_FA_AccountingCost]
                            , [BT10_FA_BuyerReference]
                            , [BT73_FA_InvoicePeriod_StartDate]
                            , [BT74_FA_InvoicePeriod_EndDate]
                            , [BT8_FA_InvoicePeriod_DescriptionCode]
                            , [BT13_FA_OrderReference_ID]
                            , [BT14_FA_OrderReference_SalesOrderID]
                            , [BT25_A_BillingReference_InvoiceDocumentReference_ID]
                            , [BT26_A_BillingReference_InvoiceDocumentReference_IssueDate]
                            , [BT34_FA_AccountingSupplierParty_Party_EndpointID_SchemeID]
                            , [BT34_FA_AccountingSupplierParty_Party_EndpointID]
                            , [BT28_FA_AccountingSupplierParty_Party_PartyName_Name]
                            , [BT35_FA_AccountingSupplierParty_Party_PostalAddress_StreetName]
                            , [BT36_FA_AccountingSupplierParty_Party_PostalAddress_AdditionalStreetName]
                            , [BT37_FA_AccountingSupplierParty_Party_PostalAddress_CityName]
                            , [BT38_FA_AccountingSupplierParty_Party_PostalAddress_PostalZone]
                            , [BT40_FA_AccountingSupplierParty_Party_PostalAddress_Country_IdentificationCode]
                            , [BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_CompanyID]
                            , [BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_TaxScheme_ID]
                            , [BT27_FA_AccountingSupplierParty_Party_PartyLegalEntity_RegistrationName]
                            , [BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID_Scheme]
                            , [BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID]
                            , [BT33_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyLegalForm]
                            , [BT41_FA_AccountingSupplierParty_Party_Contact_Name]
                            , [BT42_FA_AccountingSupplierParty_Party_Contact_Telephone]
                            , [BT43_FA_AccountingSupplierParty_Party_Contact_ElectronicMail]
                            , [BT49_FA_AccountingCustomerParty_Party_EndpointID_Scheme]
                            , [BT49_FA_AccountingCustomerParty_Party_EndpointID]
                            , [BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID_Scheme]
                            , [BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID]
                            , [BT50_FA_AccountingCustomerParty_Party_PostalAddress_StreetName]
                            , [BT51_FA_AccountingCustomerParty_Party_PostalAddress_AdditionalStreetName]
                            , [BT52_FA_AccountingCustomerParty_Party_PostalAddress_CityName]
                            , [BT53_FA_AccountingCustomerParty_Party_PostalAddress_PostalZone]
                            , [BT55_FA_AccountingCustomerParty_Party_PostalAddress_Country_IdentificationCode]
                            , [BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_CompanyID]
                            , [BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_TaxScheme_ID]
                            , [BT44_FA_AccountingCustomerParty_Party_PartyLegalEntity_RegistrationName]
                            , [BT57_FA_AccountingCustomerParty_Party_Contact_Telephone]
                            , [BT58_FA_AccountingCustomerParty_Party_ElectronicMail]
                            , [BT75_FA_Delivery_DeliveryLocation_Address_StreetName]
                            , [BT76_FA_Delivery_DeliveryLocation_Address_AdditionalStreetName]
                            , [BT77_FA_Delivery_DeliveryLocation_Address_CityName]
                            , [BT78_FA_Delivery_DeliveryLocation_Address_PostalZone]
                            , [BT80_Delivery_FA_DeliveryLocation_Address_Country_IdentificationCode]
                            , [BT70_FA_Delivery_DeliveryParty_PartyName_Name]
                            , [BT81_FA_PaymentMeans_PaymentMeansCode_Name]
                            , [BT81_FA_PaymentMeans_PaymentMeansCode]
                            , [BT83_FA_PaymentMeans_PaymentID]
                            , [BT84_FA_PaymentMeans_PayeeFinancialAccount_ID]
                            , [BT85_FA_PaymentMeans_PayeeFinancialAccount_Name]
                            , [BT86_FA_PaymentMeans_PayeeFinancialAccount_FinancialInstitutionBranch_ID]
                            , [BT20_FA_PaymentTerms_Note]
                            , [BT110_FA_TaxTotal_TaxAmount_currencyID]
                            , [BT110_FA_TaxTotal_TaxAmount]
                            , [BT116_FA_TaxTotal_TaxSubtotal_TaxableAmount_currencyID]
                            , [BT116_FA_TaxTotal_TaxSubtotal_TaxableAmount]
                            , [BT117_FA_TaxTotal_TaxSubtotal_TaxAmount_currencyID]
                            , [BT117_FA_TaxTotal_TaxSubtotal_TaxAmount]
                            , [BT118_FA_TaxTotal_TaxSubtotal_TaxCategory_ID]
                            , [BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_Percent]
                            , [BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_TaxScheme_ID]
                            , [BT106_FA_LegalMonetaryTotal_LineExtensionAmount_currencyID]
                            , [BT106_FA_LegalMonetaryTotal_LineExtensionAmount]
                            , [BT109_FA_LegalMonetaryTotal_TaxExclusiveAmount_currencyID]
                            , [BT109_FA_LegalMonetaryTotal_TaxExclusiveAmount]
                            , [BT112_FA_LegalMonetaryTotal_TaxInclusiveAmount_currencyID]
                            , [BT112_FA_LegalMonetaryTotal_TaxInclusiveAmount]
                            , [BT115_FA_LegalMonetaryTotal_PayableAmount_currencyID]
                            , [BT115_FA_LegalMonetaryTotal_PayableAmount]
                    FROM [eInvoice].[dbo].[{ETL}]
                    """)

    #rowAH = cursorH.fetchall()
    rowAH = []
    while True:
        try:
            row = cursorH.fetchone()
            if row is None:
                break
            rowAH.append(row)
        except Exception as e:
            print(f"Ligne ignorée : {e}")
    connH.close()

    return rowAH

## Back Pour gen factu
def fetch_header(num_fact : int) -> pyodbc.Row:
    """
    Récupère la ligne d'entête de facture en base {SERVER_NAME} du serveur {DATABASE_NAME},
    basé sur le numéro de facture / d'avoir

    :param num_fact:
        numéro de facture / avoir d'entête de document a recuperer
    :return rowH:
        objet pyodbc.Row : colonnes de la ligne d'entête
    """

    connH = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
    )

    cursorH = connH.cursor()
    cursorH.execute(f"""
                    SELECT
                           [Control_TypeDoc]
                          ,[Control_DocNum]
                          ,[Control_CodeCient]
                          ,[Control_NomClient]
                          ,[Control_CodeTVA]
                          ,[Control_Siret]
                          ,[Control_Process_B2B_B2C_B2G_eRephorsFR]
                          ,[Control_TVA_Piece]
                          ,[Control_TVA_Taux]
                          ,[Control_StatTiersFamille]
                          ,[Control_StatTiersWiloRepp]
                          ,[Control_DestFacture]
                          ,[Control_DestFacture_Email]
                          ,[UBL_FA_XML_Encode]
                          ,[UBL_FA_SpecSchema]
                          ,[BT0_FA_UBLVersionID]
                          ,[BT24_FA_CustomizationID]
                          ,[BT23_FA_ProfileID]
                          ,[BT1_FA_ID]
                          ,[BT2_FA_IssueDate]
                          ,[BT9_F_DueDate]
                          ,[BT3_FA_InvoiceCreditNoteTypeCode]
                          ,[BT22_FA_Note_REG]
                          ,[BT22_FA_Note_ABL]
                          ,[BT22_FA_Note_AAI]
                          ,[BT22_FA_Note_PMD]
                          ,[BT22_FA_Note_PMT]
                          ,[BT22_FA_Note_AAB]
                          ,[BT22_FA_Note_BAR]
                          ,[BT5_FA_DocumentCurrencyCode]
                          ,[BT19_FA_AccountingCost]
                          ,[BT10_FA_BuyerReference]
                          ,[BT73_FA_InvoicePeriod_StartDate]
                          ,[BT74_FA_InvoicePeriod_EndDate]
                          ,[BT8_FA_InvoicePeriod_DescriptionCode]
                          ,[BT13_FA_OrderReference_ID]
                          ,[BT14_FA_OrderReference_SalesOrderID]
                          ,[BT25_A_BillingReference_InvoiceDocumentReference_ID]
                          ,[BT26_A_BillingReference_InvoiceDocumentReference_IssueDate]
                          ,[BT34_FA_AccountingSupplierParty_Party_EndpointID_SchemeID]
                          ,[BT34_FA_AccountingSupplierParty_Party_EndpointID]
                          ,[BT28_FA_AccountingSupplierParty_Party_PartyName_Name]
                          ,[BT35_FA_AccountingSupplierParty_Party_PostalAddress_StreetName]
                          ,[BT36_FA_AccountingSupplierParty_Party_PostalAddress_AdditionalStreetName]
                          ,[BT37_FA_AccountingSupplierParty_Party_PostalAddress_CityName]
                          ,[BT38_FA_AccountingSupplierParty_Party_PostalAddress_PostalZone]
                          ,[BT40_FA_AccountingSupplierParty_Party_PostalAddress_Country_IdentificationCode]
                          ,[BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_CompanyID]
                          ,[BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_TaxScheme_ID]
                          ,[BT27_FA_AccountingSupplierParty_Party_PartyLegalEntity_RegistrationName]
                          ,[BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID_Scheme]
                          ,[BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID]
                          ,[BT33_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyLegalForm]
                          ,[BT41_FA_AccountingSupplierParty_Party_Contact_Name]
                          ,[BT42_FA_AccountingSupplierParty_Party_Contact_Telephone]
                          ,[BT43_FA_AccountingSupplierParty_Party_Contact_ElectronicMail]
                          ,[BT49_FA_AccountingCustomerParty_Party_EndpointID_Scheme]
                          ,[BT49_FA_AccountingCustomerParty_Party_EndpointID]
                          ,[BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID_Scheme]
                          ,[BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID]
                          ,[BT50_FA_AccountingCustomerParty_Party_PostalAddress_StreetName]
                          ,[BT51_FA_AccountingCustomerParty_Party_PostalAddress_AdditionalStreetName]
                          ,[BT52_FA_AccountingCustomerParty_Party_PostalAddress_CityName]
                          ,[BT53_FA_AccountingCustomerParty_Party_PostalAddress_PostalZone]
                          ,[BT55_FA_AccountingCustomerParty_Party_PostalAddress_Country_IdentificationCode]
                          ,[BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_CompanyID]
                          ,[BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_TaxScheme_ID]
                          ,[BT44_FA_AccountingCustomerParty_Party_PartyLegalEntity_RegistrationName]
                          ,[BT57_FA_AccountingCustomerParty_Party_Contact_Telephone]
                          ,[BT58_FA_AccountingCustomerParty_Party_ElectronicMail]
                          ,[BT75_FA_Delivery_DeliveryLocation_Address_StreetName]
                          ,[BT76_FA_Delivery_DeliveryLocation_Address_AdditionalStreetName]
                          ,[BT77_FA_Delivery_DeliveryLocation_Address_CityName]
                          ,[BT78_FA_Delivery_DeliveryLocation_Address_PostalZone]
                          ,[BT80_Delivery_FA_DeliveryLocation_Address_Country_IdentificationCode]
                          ,[BT70_FA_Delivery_DeliveryParty_PartyName_Name]
                          ,[BT81_FA_PaymentMeans_PaymentMeansCode_Name]
                          ,[BT81_FA_PaymentMeans_PaymentMeansCode]
                          ,[BT83_FA_PaymentMeans_PaymentID]
                          ,[BT84_FA_PaymentMeans_PayeeFinancialAccount_ID]
                          ,[BT85_FA_PaymentMeans_PayeeFinancialAccount_Name]
                          ,[BT86_FA_PaymentMeans_PayeeFinancialAccount_FinancialInstitutionBranch_ID]
                          ,[BT20_FA_PaymentTerms_Note]
                          ,[BT110_FA_TaxTotal_TaxAmount_currencyID]
                          ,[BT110_FA_TaxTotal_TaxAmount]
                          ,[BT116_FA_TaxTotal_TaxSubtotal_TaxableAmount_currencyID]
                          ,[BT116_FA_TaxTotal_TaxSubtotal_TaxableAmount]
                          ,[BT117_FA_TaxTotal_TaxSubtotal_TaxAmount_currencyID]
                          ,[BT117_FA_TaxTotal_TaxSubtotal_TaxAmount]
                          ,[BT118_FA_TaxTotal_TaxSubtotal_TaxCategory_ID]
                          ,[BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_Percent]
                          ,[BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_TaxScheme_ID]
                          ,[BT106_FA_LegalMonetaryTotal_LineExtensionAmount_currencyID]
                          ,[BT106_FA_LegalMonetaryTotal_LineExtensionAmount]
                          ,[BT109_FA_LegalMonetaryTotal_TaxExclusiveAmount_currencyID]
                          ,[BT109_FA_LegalMonetaryTotal_TaxExclusiveAmount]
                          ,[BT112_FA_LegalMonetaryTotal_TaxInclusiveAmount_currencyID]
                          ,[BT112_FA_LegalMonetaryTotal_TaxInclusiveAmount]
                          ,[BT115_FA_LegalMonetaryTotal_PayableAmount_currencyID]
                          ,[BT115_FA_LegalMonetaryTotal_PayableAmount]
                      FROM [eInvoice].[dbo].[v_inv_cn_header_python]
    
                      WHERE [Control_DocNum] = {num_fact}
                      """)

    rowH = cursorH.fetchone()
    connH.close()

    return rowH

def fetch_lines(num_fact : int) -> list[pyodbc.Row]:
    """
    Récupère les lignes de facture / d'avoir en base {SERVER_NAME} du serveur {DATABASE_NAME},
    basé sur le numéro de facture / d'avoir

    :param num_fact:
        numéro de facture / avoir de lignes du document a recuperer
    :return rowH:
        list[pyodbc.Row] : liste des lignes de colonnes de la facture / avoir
    """

    connL = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
    )

    cursorL = connL.cursor()
    cursorL.execute(f"""
                    SELECT
                        [Control_TypeDoc]
                            , [Control_DocNum]
                            , [Control_CodeCient]
                            , [Control_NomClient]
                            , [Control_CodeTVA]
                            , [Control_Siret]
                            , [Control_Process_B2B_B2C_B2G_eRephorsFR]
                            , [Control_TVA_Piece]
                            , [Control_TVA_Taux]
                            , [BT0_InvoiceLine_CreditNoteLine_Numero]
                            , [BT126_InvoiceLine_CreditNoteLine_ID]
                            , [BT129_InvoiceLine_CreditNoteLine_InvoicedQuantity_CreditedQuantity_uniteCode]
                            , [BT129_InvoiceLine_CreditNoteLine_InvoicedQuantity_CreditedQuantity]
                            , [BT131_InvoiceLine_CreditNoteLine_LineExtensionAmount_CurrencyID]
                            , [BT131_InvoiceLine_CreditNoteLine_LineExtensionAmount]
                            , [Control_QxU_Totalligne]
                            , [BT154_InvoiceLine_CreditNoteLine_Item_Description]
                            , [BT153_InvoiceLine_CreditNoteLine_Item_Name]
                            , [BT156_InvoiceLine_CreditNoteLine_Item_BuyersItemIdentification_SellersItemIdentification_ID]
                            , [BT151_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_ID]
                            , [BT152_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_Percent]
                            , [BT151_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_TaxScheme_ID] -- BT151_0
                            , [BT146_InvoiceLine_CreditNoteLine_Price_PriceAmount_currencyID]
                            , [BT146_InvoiceLine_CreditNoteLine_Price_PriceAmount]
                            , [BT149_InvoiceLine_CreditNoteLine_Price_BaseQuantity_uniteCode]
                            , [BT149_InvoiceLine_CreditNoteLine_Price_BaseQuantity]
                    FROM [eInvoice].[dbo].[v_inv_cn_lines_python]

                    WHERE [Control_DocNum] = {num_fact}
                    """)

    rowsL = cursorL.fetchall()
    connL.close()
    
    return rowsL

def add_attachment(output_doc : etree._Element, rowH : pyodbc.Row, NS : dict[str, str]) -> None:
    """
    Ajout piece joint encodé en base64 dans le xml

    :param output_doc:
        document xml
    :param rowH:
        Valeurs entete du document pour nommage fichier
    :param NS:
        NameSpace : cac, cbc
    :return:
        None
    """

    #f"{DOC_OUTPUT_PATH}{rowH.Control_TypeDoc}_{rowH.Control_DocNum}_{rowH.Control_CodeCient}_{rowH.BT2_FA_IssueDate}.xml"

    # TODO : Voir comment le file est recuperer pour ensuite le passer en parametre | in_file_name
    file = ATTACHMENT_INPUT_PATH + "FK20260123456789.pdf"

    attachment_name = f"{rowH.Control_TypeDoc}_{rowH.Control_DocNum}_{rowH.Control_CodeCient}_{rowH.BT2_FA_IssueDate}_attachment.pdf"
    with open(file, "rb") as f:
        attachment_encoded = base64.b64encode(f.read()).decode("utf-8")

    output_doc.find("cac:AdditionalDocumentReference/cbc:ID", namespaces=NS).text = "ATTACHMENT_001"
    output_doc.find("cac:AdditionalDocumentReference/cbc:DocumentTypeCode", namespaces=NS).text = "916"

    output_doc.find("cac:AdditionalDocumentReference/cac:Attachment/cbc:EmbeddedDocumentBinaryObject", namespaces=NS).set("mimeCode", "application/pdf")
    output_doc.find("cac:AdditionalDocumentReference/cac:Attachment/cbc:EmbeddedDocumentBinaryObject", namespaces=NS).set("filename", attachment_name)
    output_doc.find("cac:AdditionalDocumentReference/cac:Attachment/cbc:EmbeddedDocumentBinaryObject", namespaces=NS).text = attachment_encoded

# L'authentique coeur de la machine
def fact_bdd_to_xml(num_fact : int) -> None: # -> XML_UBL2
    """
    Génère un fichier xml en respectant les normes ULB2, en suivant les champs
    requis par les besoin de SESEM.

    :formats supportés a date:
        B2B: facture - avoir
        B2C: facture - avoir (valeur placeholder en base pour le siret)

    :param num_fact:
        numéro de facture / d'avoir du document a generer
    :return NONE:
        génère un fichier .xml
    """

    # == Recuperation Data Header ==
    rowH = fetch_header(num_fact)
    # == Recuperation Data Lines ==
    rowsL = fetch_lines(num_fact)

    CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    NS = {"cac": CAC, "cbc": CBC}

    type_doc = rowH.Control_TypeDoc

    match(type_doc):
        case "Invoice":
            # Template input
            input_doc = INVOICE_TEMPLATE_INPUT

            template_xml = etree.parse(input_doc)
            template_root = template_xml.getroot()

            # Invoice
            output_doc = copy.deepcopy(template_root)

        case "CreditNote":
            # Template input
            input_doc = CREDIT_NOTE_TEMPLATE_INPUT

            template_xml = etree.parse(input_doc)
            template_root = template_xml.getroot()

            # Credit Note
            output_doc = copy.deepcopy(template_root)

        case _:
            raise ValueError(f"Invalid typeDoc Value : {type_doc}")

    # == Devise ==
    # currency = rowH.BT5_FA_DocumentCurrencyCode
    
    # == Header ==
    output_doc.find("cbc:UBLVersionID", namespaces=NS).text    = rowH.BT0_FA_UBLVersionID
    output_doc.find("cbc:CustomizationID", namespaces=NS).text = rowH.BT24_FA_CustomizationID
    output_doc.find("cbc:ProfileID", namespaces=NS).text       = rowH.BT23_FA_ProfileID
    output_doc.find("cbc:ID", namespaces=NS).text              = str(rowH.BT1_FA_ID)
    output_doc.find("cbc:IssueDate", namespaces=NS).text       = rowH.BT2_FA_IssueDate
    if type_doc == "Invoice":
        output_doc.find("cbc:DueDate", namespaces=NS).text     = rowH.BT9_F_DueDate

    # InvoiceTypeCode
    if type_doc == "Invoice":
            output_doc.find("cbc:InvoiceTypeCode", namespaces=NS).text = str(rowH.BT3_FA_InvoiceCreditNoteTypeCode)
    elif type_doc == "CreditNote":
            output_doc.find("cbc:CreditNoteTypeCode", namespaces=NS).text = str(rowH.BT3_FA_InvoiceCreditNoteTypeCode)

    # ...
    # :Note
    for note in output_doc.findall("cbc:Note", namespaces=NS):
        # Const
        if note.text and note.text.startswith("#REG#"):
            note.text = rowH.BT22_FA_Note_REG
        elif note.text and note.text.startswith("#ABL#"):
            note.text = rowH.BT22_FA_Note_ABL
        elif note.text and note.text.startswith("#AAI#"):
            note.text = rowH.BT22_FA_Note_AAI
        elif note.text and note.text.startswith("#PMD#"):
            note.text = rowH.BT22_FA_Note_PMD
        elif note.text and note.text.startswith("#PMT#"):
            note.text = rowH.BT22_FA_Note_PMT
        elif note.text and note.text.startswith("#AAB#"):
            note.text = rowH.BT22_FA_Note_AAB
        # Var
        elif note.text and note.text.startswith("#BAR#"):
            note.text = rowH.BT22_FA_Note_BAR
    # ...

    output_doc.find("cbc:DocumentCurrencyCode", namespaces=NS).text = rowH.BT5_FA_DocumentCurrencyCode
    output_doc.find("cbc:AccountingCost", namespaces=NS).text       = rowH.BT19_FA_AccountingCost
    output_doc.find("cbc:BuyerReference", namespaces=NS).text       = rowH.BT10_FA_BuyerReference

    output_doc.find("cac:InvoicePeriod/cbc:StartDate", namespaces=NS).text       = rowH.BT73_FA_InvoicePeriod_StartDate
    output_doc.find("cac:InvoicePeriod/cbc:EndDate", namespaces=NS).text         = rowH.BT74_FA_InvoicePeriod_EndDate
    output_doc.find("cac:InvoicePeriod/cbc:DescriptionCode", namespaces=NS).text = str(rowH.BT8_FA_InvoicePeriod_DescriptionCode)

    output_doc.find("cac:OrderReference/cbc:ID", namespaces=NS).text           = rowH.BT13_FA_OrderReference_ID
    output_doc.find("cac:OrderReference/cbc:SalesOrderID", namespaces=NS).text = rowH.BT14_FA_OrderReference_SalesOrderID

    if type_doc == "CreditNote":
        output_doc.find("cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", namespaces=NS).text        = str(rowH.BT25_A_BillingReference_InvoiceDocumentReference_ID)
        output_doc.find("cac:BillingReference/cac:InvoiceDocumentReference/cbc:IssueDate", namespaces=NS).text = str(rowH.BT26_A_BillingReference_InvoiceDocumentReference_IssueDate)

    # output_doc.find("cac:AdditionalDocumentReference/cbc:ID", namespaces=NS).set("schemeID", "IT MDFD")  # BT-18 (Identifiant d'objet facturé) : REF_CLIENT2514
    # output_doc.find("cac:AdditionalDocumentReference/cbc:ID", namespaces=NS).text               = "MDFD" # BT-18 (Identifiant d'objet facturé) : REF_CLIENT2514
    # output_doc.find("cac:AdditionalDocumentReference/cbc:DocumentTypeCode", namespaces=NS).text = "130"  # 130

    # == Supplier ==
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cbc:EndpointID", namespaces=NS).set("schemeID", rowH.BT34_FA_AccountingSupplierParty_Party_EndpointID_SchemeID)
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cbc:EndpointID", namespaces=NS).text        = rowH.BT34_FA_AccountingSupplierParty_Party_EndpointID
    # output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=NS).set("schemeID", "0088 MDFD") # BT-29-0 (Identifiant du vendeur (Global ID)) : 587451236587
    # output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=NS).text = "MDFD"                # BT-29-0 (Identifiant du vendeur (Global ID)) : 587451236587
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", namespaces=NS).text = rowH.BT28_FA_AccountingSupplierParty_Party_PartyName_Name

    # Adresse vendeur
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:StreetName", namespaces=NS).text                     = rowH.BT35_FA_AccountingSupplierParty_Party_PostalAddress_StreetName
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:AdditionalStreetName", namespaces=NS).text           = rowH.BT36_FA_AccountingSupplierParty_Party_PostalAddress_AdditionalStreetName
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CityName", namespaces=NS).text                       = rowH.BT37_FA_AccountingSupplierParty_Party_PostalAddress_CityName
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces=NS).text                     = rowH.BT38_FA_AccountingSupplierParty_Party_PostalAddress_PostalZone
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode", namespaces=NS).text = rowH.BT40_FA_AccountingSupplierParty_Party_PostalAddress_Country_IdentificationCode

    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS).text = rowH.BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_CompanyID
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID", namespaces=NS).text = rowH.BT31_FA_AccountingSupplierParty_Party_PartyTaxScheme_TaxScheme_ID

    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces=NS).text = rowH.BT27_FA_AccountingSupplierParty_Party_PartyLegalEntity_RegistrationName
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS).set("schemeID", rowH.BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID_Scheme)
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS).text        = rowH.BT30_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyID
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyLegalForm", namespaces=NS).text = rowH.BT33_FA_AccountingSupplierParty_Party_PartyLegalEntity_CompanyLegalForm

    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone", namespaces=NS).text      = rowH.BT42_FA_AccountingSupplierParty_Party_Contact_Telephone
    output_doc.find("cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=NS).text = rowH.BT43_FA_AccountingSupplierParty_Party_Contact_ElectronicMail

    # == Customer ==
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cbc:EndpointID", namespaces=NS).set("schemeID", rowH.BT49_FA_AccountingCustomerParty_Party_EndpointID_Scheme)
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cbc:EndpointID", namespaces=NS).text = rowH.BT49_FA_AccountingCustomerParty_Party_EndpointID
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=NS).set("schemeID", rowH.BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID_Scheme)
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=NS).text = rowH.BT46_FA_AccountingCustomerParty_Party_PartyIdentification_ID

    # Adresse acheteur
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:StreetName", namespaces=NS).text                     = rowH.BT50_FA_AccountingCustomerParty_Party_PostalAddress_StreetName
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:AdditionalStreetName", namespaces=NS).text           = rowH.BT51_FA_AccountingCustomerParty_Party_PostalAddress_AdditionalStreetName
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName", namespaces=NS).text                       = rowH.BT52_FA_AccountingCustomerParty_Party_PostalAddress_CityName
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces=NS).text                     = rowH.BT53_FA_AccountingCustomerParty_Party_PostalAddress_PostalZone
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode", namespaces=NS).text = rowH.BT55_FA_AccountingCustomerParty_Party_PostalAddress_Country_IdentificationCode

    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS).text        = rowH.BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_CompanyID
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID", namespaces=NS).text = rowH.BT48_FA_AccountingCustomerParty_Party_PartyTaxScheme_TaxScheme_ID

    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces=NS).text = rowH.BT44_FA_AccountingCustomerParty_Party_PartyLegalEntity_RegistrationName
    # output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS).set("schemeID", "0002 MDFD") # BT-47 (Identifiant d’enregistrement  légal de l'acheteur
    # output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS).text        = "MDFD"         # BT-47 (Identifiant d’enregistrement  légal de l'acheteur

    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone", namespaces=NS).text      = rowH.BT57_FA_AccountingCustomerParty_Party_Contact_Telephone
    output_doc.find("cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=NS).text = rowH.BT58_FA_AccountingCustomerParty_Party_ElectronicMail

    # == Livraison ==
    output_doc.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:StreetName", namespaces=NS).text                     = rowH.BT75_FA_Delivery_DeliveryLocation_Address_StreetName
    output_doc.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:AdditionalStreetName", namespaces=NS).text           = rowH.BT76_FA_Delivery_DeliveryLocation_Address_AdditionalStreetName
    output_doc.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:CityName", namespaces=NS).text                       = rowH.BT77_FA_Delivery_DeliveryLocation_Address_CityName
    output_doc.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cbc:PostalZone", namespaces=NS).text                     = rowH.BT78_FA_Delivery_DeliveryLocation_Address_PostalZone
    output_doc.find("cac:Delivery/cac:DeliveryLocation/cac:Address/cac:Country/cbc:IdentificationCode", namespaces=NS).text = rowH.BT80_Delivery_FA_DeliveryLocation_Address_Country_IdentificationCode

    output_doc.find("cac:Delivery/cac:DeliveryParty/cac:PartyName/cbc:Name", namespaces=NS).text = rowH.BT70_FA_Delivery_DeliveryParty_PartyName_Name

    # == Payement ==
    output_doc.find("cac:PaymentMeans/cbc:PaymentMeansCode", namespaces=NS).set("name", rowH.BT81_FA_PaymentMeans_PaymentMeansCode_Name)
    output_doc.find("cac:PaymentMeans/cbc:PaymentMeansCode", namespaces=NS).text                                            = rowH.BT81_FA_PaymentMeans_PaymentMeansCode
    output_doc.find("cac:PaymentMeans/cbc:PaymentID", namespaces=NS).text                                                   = rowH.BT83_FA_PaymentMeans_PaymentID
    output_doc.find("cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:ID", namespaces=NS).text                                = rowH.BT84_FA_PaymentMeans_PayeeFinancialAccount_ID
    output_doc.find("cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:Name", namespaces=NS).text                              = rowH.BT85_FA_PaymentMeans_PayeeFinancialAccount_Name
    output_doc.find("cac:PaymentMeans/cac:PayeeFinancialAccount/cac:FinancialInstitutionBranch/cbc:ID", namespaces=NS).text = rowH.BT86_FA_PaymentMeans_PayeeFinancialAccount_FinancialInstitutionBranch_ID

    output_doc.find("cac:PaymentTerms/cbc:Note", namespaces=NS).text = rowH.BT20_FA_PaymentTerms_Note

    output_doc.find("cac:TaxTotal/cbc:TaxAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:TaxTotal/cbc:TaxAmount", namespaces=NS).text = str(rowH.BT110_FA_TaxTotal_TaxAmount)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", namespaces=NS).text = str(rowH.BT116_FA_TaxTotal_TaxSubtotal_TaxableAmount)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount", namespaces=NS).text = str(rowH.BT117_FA_TaxTotal_TaxSubtotal_TaxAmount)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID", namespaces=NS).text               = rowH.BT118_FA_TaxTotal_TaxSubtotal_TaxCategory_ID
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent", namespaces=NS).text          = str(rowH.BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_Percent)
    output_doc.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", namespaces=NS).text = rowH.BT119_FA_TaxTotal_TaxSubtotal_TaxCategory_TaxScheme_ID

    output_doc.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces=NS).text = str(rowH.BT106_FA_LegalMonetaryTotal_LineExtensionAmount)
    output_doc.find("cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces=NS).set("currencyID",rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces=NS).text = str(rowH.BT109_FA_LegalMonetaryTotal_TaxExclusiveAmount)
    output_doc.find("cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", namespaces=NS).set("currencyID",rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", namespaces=NS).text = str(rowH.BT112_FA_LegalMonetaryTotal_TaxInclusiveAmount)

    # output_doc.find("cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    # output_doc.find("cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount", namespaces=NS).text = str(rowH.BT107_FA_LegalMonetaryTotal_AllowanceTotalAmount)
    # output_doc.find("cac:LegalMonetaryTotal/cbc:ChargeTotalAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    # output_doc.find("cac:LegalMonetaryTotal/cbc:ChargeTotalAmount", namespaces=NS).text    = str(rowH.BT108_FA_LegalMonetaryTotal_ChargeTotalAmount)
    # output_doc.find("cac:LegalMonetaryTotal/cbc:PrepaidAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    # output_doc.find("cac:LegalMonetaryTotal/cbc:PrepaidAmount", namespaces=NS).text        = str(rowH.BT113_FA_LegalMonetaryTotal_PrepaidAmount)

    output_doc.find("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=NS).set("currencyID", rowH.BT5_FA_DocumentCurrencyCode)
    output_doc.find("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=NS).text = str(rowH.BT115_FA_LegalMonetaryTotal_PayableAmount)

    # == Lines ==
    # = Invoice =
    line_tag = "InvoiceLine" if type_doc == "Invoice" else "CreditNoteLine"
    qty_tag = "InvoicedQuantity" if type_doc == "Invoice" else "CreditedQuantity"

    for rowL in rowsL:
        # Creation De la Balise
        line = etree.SubElement(output_doc, f"{{{CAC}}}{line_tag}")

        etree.SubElement(line, f"{{{CBC}}}ID").text = str(rowL.BT126_InvoiceLine_CreditNoteLine_ID)

        qty = etree.SubElement(line, f"{{{CBC}}}{qty_tag}")
        qty.set("unitCode", rowL.BT129_InvoiceLine_CreditNoteLine_InvoicedQuantity_CreditedQuantity_uniteCode)
        qty.text = str(rowL.BT129_InvoiceLine_CreditNoteLine_InvoicedQuantity_CreditedQuantity)

        line_ext_amount = etree.SubElement(line, f"{{{CBC}}}LineExtensionAmount")
        line_ext_amount.set("currencyID", rowL.BT131_InvoiceLine_CreditNoteLine_LineExtensionAmount_CurrencyID)
        line_ext_amount.text = str(rowL.BT131_InvoiceLine_CreditNoteLine_LineExtensionAmount)

        # Item
        item = etree.SubElement(line, f"{{{CAC}}}Item")

        etree.SubElement(item, f"{{{CBC}}}Description").text = rowL.BT154_InvoiceLine_CreditNoteLine_Item_Description
        etree.SubElement(item, f"{{{CBC}}}Name").text = rowL.BT153_InvoiceLine_CreditNoteLine_Item_Name

        tax_category = etree.SubElement(item, f"{{{CAC}}}ClassifiedTaxCategory")
        etree.SubElement(tax_category, f"{{{CBC}}}ID").text = rowL.BT151_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_ID
        etree.SubElement(tax_category, f"{{{CBC}}}Percent").text = str(rowL.BT152_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_Percent)

        tax_scheme = etree.SubElement(tax_category, f"{{{CAC}}}TaxScheme")
        etree.SubElement(tax_scheme, f"{{{CBC}}}ID").text = rowL.BT151_InvoiceLine_CreditNoteLine_Item_ClassifiedTaxCategory_TaxScheme_ID

        # Price
        price = etree.SubElement(line, f"{{{CAC}}}Price")

        price_amount = etree.SubElement(price, f"{{{CBC}}}PriceAmount")
        price_amount.set("currencyID", rowL.BT146_InvoiceLine_CreditNoteLine_Price_PriceAmount_currencyID)
        price_amount.text = str(rowL.BT146_InvoiceLine_CreditNoteLine_Price_PriceAmount)

        base_qty = etree.SubElement(price, f"{{{CBC}}}BaseQuantity")
        base_qty.set("unitCode", rowL.BT149_InvoiceLine_CreditNoteLine_Price_BaseQuantity_uniteCode)
        base_qty.text = str(rowL.BT149_InvoiceLine_CreditNoteLine_Price_BaseQuantity)

    # == Attachment ==
    add_attachment(output_doc, rowH, NS)

    # == Creation du fichier ==

    # Indentation
    etree.indent(output_doc, space="     ")

    etree.ElementTree(output_doc).write(
        f"{DOC_OUTPUT_PATH}{rowH.Control_TypeDoc}_{rowH.Control_DocNum}_{rowH.Control_CodeCient}_{rowH.BT2_FA_IssueDate}.xml",
        xml_declaration=True,
        encoding="UTF-8"
    )

def gen_all_doc_in_table():
    """
    Génère tout les documents de la table [eInvoice].[dbo].[v_inv_cn_lines_python]
    Table (pour l'instant) destiné a stocker les documents a generer.

    :return NONE:
        appel.s consécutif.s de <fact_bdd_to_xml(num_fact : int)>
    """

    # Connexion en base
    connListNum = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
    )

    cursorListNum = connListNum.cursor()
    cursorListNum.execute("""
                    SELECT 
                        [Control_DocNum] 
                    FROM [eInvoice].[dbo].[v_inv_cn_lines_python]
                    """)

    # Recuperation de la liste des numero de doc en table
    listNum = cursorListNum.fetchall()
    connListNum.close()

    # Cleaning de la "list" (qui est un item "row") en liste de int
    cleanListNum = []
    for num in listNum:
        cleanListNum.append(int(num[0]))

    # Verif temporaire
    # print(cleanListNum)

    # Gen de tout les documents en table
    for num in cleanListNum:
        fact_bdd_to_xml(num)

def gen_all_doc_in_list(list_id_doc: list):
    for count, id in enumerate(list_id_doc, 1):
        fact_bdd_to_xml(id)
        yield f"{count}/{len(list_id_doc)}"

if __name__ == "__main__":
    #gen_all_doc_in_table()

    '''
    Exemple d'utilisation individuel (/!\\ tape dans la table {ETL})
    fact_bdd_to_xml(26140022) # CN
    fact_bdd_to_xml(25144441) # INV
    
    rows = fetch_all_header()
    cols = fetch_all_header_columns()

    for r in rows :
        print(r)

    for c in cols :
        print(c)
    '''