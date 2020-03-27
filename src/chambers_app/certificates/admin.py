from django.contrib import admin

from .models import (
    Certificate, CertificateDocument, RecipientCountry,
)


@admin.register(RecipientCountry)
class RecipientCountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'agreement_name')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'org', 'dst_country', 'status')
    list_filter = ('status',)


@admin.register(CertificateDocument)
class CertificateDocumentAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'type', 'file', 'certificate')
