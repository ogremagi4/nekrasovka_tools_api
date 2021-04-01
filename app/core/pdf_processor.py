from PDFNetPython3 import *


class PdfProcessor():
    def __init__(self) -> None:
        PDFNet.Initialize()
        

    def certify_pdf(self, filepath, stamp_path, cert_field_name, pfx_path, pfx_passwd, output_filepath):
        doc = PDFDoc(filepath)
        last_page = doc.GetPage(doc.GetPageCount())
        annot1 = TextWidget.Create(doc, Rect(50, 550, 350, 600), "TextWidgetField")
        last_page.AnnotPushBack(annot1)
        certification_sig_field = doc.CreateDigitalSignatureField(cert_field_name)
        widgetAnnot = SignatureWidget.Create(doc, Rect(0, 100, 200, 150), certification_sig_field)
        last_page.AnnotPushBack(widgetAnnot)
        
        # img = Image.Create(doc.GetSDFDoc(), stamp_path)
        # widgetAnnot.CreateSignatureAppearance(img)
        certification_sig_field.SetDocumentPermissions(DigitalSignatureField.e_annotating_formfilling_signing_allowed)
        certification_sig_field.SetFieldPermissions(DigitalSignatureField.e_include, ['TextWidgetField'])
        certification_sig_field.CertifyOnNextSave(pfx_path, pfx_passwd)
        certification_sig_field.SetLocation('Moscow, RU')
        certification_sig_field.SetReason('Document certification.')
        certification_sig_field.SetContactInfo('http://nekrasovka.ru/')
        doc.Save(output_filepath, 0)
    
    def sign_pdf(self, filepath, stamp_path, cert_field_name, pfx_path, pfx_passwd, output_filepath):
        doc = PDFDoc(filepath)
        last_page = doc.GetPage(doc.GetPageCount())
        signature_digsig_field = doc.CreateDigitalSignatureField(cert_field_name)
        signature_widget = SignatureWidget.Create(doc, Rect(0, 100, 200, 150), signature_digsig_field)
        last_page.AnnotPushBack(signature_widget)
        signature_digsig_field.SetDocumentPermissions(DigitalSignatureField.e_annotating_formfilling_signing_allowed)
        

        img = Image.Create(doc.GetSDFDoc(), stamp_path)
        signature_widget.CreateSignatureAppearance(img)


        signature_digsig_field.SignOnNextSave(pfx_path, pfx_passwd)

        doc.Save(output_filepath, SDFDoc.e_incremental)


        




    

