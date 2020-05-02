from django import forms

# from chambers_app.organisations.models import ChamberOfCommerce

from .models import Certificate, CertificateDocument, RecipientCountry


class CertificateCreateForm(forms.ModelForm):

    class Meta:
        model = Certificate
        fields = (
            'dst_country',
            'exporter_info', 'producer_info', 'importer_info', 'transport_info',
            'remarks', 'item_no', 'packages_marks', 'goods_descr', 'hs_code',
            'invoice_info', 'origin_criterion',
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # where user participates
        # self.fields['org'].queryset = (
        #     self.user.chambersofcommerce.all()
        #     if not self.user.is_staff
        #     else ChamberOfCommerce.objects.all()
        # )
        # self.fields['org'].help_text = (
        #     "User must have access to the organisation to create "
        #     "certificates on it's behalf"
        # )

        recipients = RecipientCountry.objects.all()
        self.fields['dst_country'].choices = (
            [
                (rec.country, f"{rec.country.name} ({rec.agreement_name})")
                for rec
                in recipients
            ]
        )
        self.fields['dst_country'].help_text = (
            "Countries list is limited to the trade agreements entered in the system"
        )

    def save(self, *args, **kwargs):
        self.instance.created_by = self.user
        return super().save(*args, **kwargs)


class CertificateUpdateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = (
            'exporter_info', 'producer_info', 'importer_info', 'transport_info',
            'remarks', 'item_no', 'packages_marks', 'goods_descr', 'hs_code',
            'invoice_info', 'origin_criterion',
        )


class CertDocumenteUploadForm(forms.ModelForm):
    class Meta:
        model = CertificateDocument
        fields = ('file', 'type')

    def __init__(self, *args, **kwargs):
        self.certificate = kwargs.pop('certificate')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.certificate = self.certificate
        self.instance.created_by = self.user
        return super().save(*args, **kwargs)
