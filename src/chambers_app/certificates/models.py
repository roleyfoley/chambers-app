import os
import logging
import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django_countries.fields import CountryField

from chambers_app.utils.monitoring import statsd_timer

logger = logging.getLogger(__name__)


class RecipientCountry(models.Model):
    country = CountryField()
    agreement_name = models.CharField(max_length=256, blank=True, default='')

    def __str__(self):
        return str(self.country)

    class Meta:
        ordering = ('country',)
        verbose_name_plural = "recipient countries"


class Certificate(models.Model):
    # User creates a certificate in this status
    STATUS_DRAFT = 'draft'
    # and then all conditions of a valid one are met - we change status to this
    STATUS_COMPLETE = 'complete'
    # user has reviewed the certificate and wants to send it further
    STATUS_LODGED = 'lodged'
    # we sent it further
    STATUS_SENT = 'sent'
    # we got some message that our certifiate was accepted by a remote party
    STATUS_ACCEPTED = 'accepted'
    # or not accepted
    STATUS_REJECTED = 'rejected'
    # or even has already used by the receiver
    STATUS_ACQUITTED = 'acquitted'
    # some error, mostly the internal one
    STATUS_ERROR = 'error'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_LODGED, 'Lodged'),
        (STATUS_SENT, 'Sent'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_ACQUITTED, 'Acquitted'),
        (STATUS_ERROR, 'Error'),
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    org = models.ForeignKey('organisations.ChamberOfCommerce', models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)

    acquitted_at = models.DateTimeField(blank=True, null=True)
    acquitted_details = JSONField(
        default=list, blank=True,
        help_text="Acquittal events received"
    )

    intergov_details = JSONField(
        default=dict, blank=True,
        help_text="Details about communication with the Intergov"
    )

    dst_country = CountryField("Destination country")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # business fields
    exporter_info = models.TextField(
        "Exporter’s name, address and country",
        blank=True, default='',
        max_length=10000,
    )
    producer_info = models.TextField(
        "Producer’s name and address",
        blank=True, default='',
        max_length=10000,
    )
    importer_info = models.TextField(
        "Importer’s name, address and country",
        blank=True, default='',
        max_length=10000,
    )
    transport_info = models.TextField(
        "Means of transport and route",
        blank=True, default='',
        max_length=10000,
        help_text="Departure date, Vessel/Flight/Train/Vehicle No., Port of loading, Port of discharge"
    )
    remarks = models.TextField(max_length=8000, blank=True, default='')
    item_no = models.TextField("Item number (max. 20)", max_length=8000, blank=True, default='')
    packages_marks = models.TextField(
        "Marks and numbers on packages",
        max_length=8000, blank=True, default=''
    )
    goods_descr = models.TextField(
        "Number and kind of packages; description of goods",
        max_length=8000, blank=True, default=''
    )
    hs_code = models.CharField("HS Code", max_length=6, blank=True, default='')
    invoice_info = models.CharField("Invoice number and date", max_length=200, blank=True, default='')
    origin_criterion = models.TextField(
        "Origin criterion",
        max_length=2000, blank=True, default=''
    )

    class Meta:
        ordering = ('-created_at',)

    def get_absolute_url(self):
        return reverse('certificates:detail', args=[self.pk])

    def __str__(self):
        status = self.get_status_display()
        return f"{status} certificate {self.short_id} for {self.org}"

    @statsd_timer("model.Certificate.save")
    def save(self, *args, **kwargs):
        if self.status == self.STATUS_DRAFT and self.is_completed:
            self.status = self.STATUS_COMPLETE
        if self.status == self.STATUS_COMPLETE and not self.is_completed:
            self.status = self.STATUS_DRAFT
        super().save(*args, **kwargs)

    @statsd_timer("model.Certificate.lodge")
    def lodge(self):
        from chambers_app.certificates.tasks import (
            notify_about_certificate_created,
            send_certificate,
        )
        self.status = Certificate.STATUS_LODGED
        self.save()
        notify_about_certificate_created.apply_async(args=[self.id], countdown=3)
        send_certificate.apply_async(
            kwargs=dict(
                certificate_id=self.id
            ),
            countdown=2,  # to let the object settle in the DB
        )
        return

    @property
    def is_completed(self):
        return all([
            self.required_documents_uploaded
        ])

    @property
    def short_id(self):
        return str(self.id)[-6:]

    def get_iterable_fields(self):
        def skip_it(what, obj):
            if what.startswith('_'):
                return True
            if what.endswith('_id'):
                return True
            if what.startswith('created') or what == 'created_by_id':
                return True
            if what == 'acquitted_details':
                return True
            return False

        return [
            (k, v)
            for k, v
            in self.__dict__.items()
            if not skip_it(k, self)
        ]

    def get_iterable_readable_fields(self):
        """
        Return list of turples:
        (field_name, field_value, field_readable_name)
        """
        result = []
        readable_field_names = {}
        for field in self._meta.fields:
            readable_field_names[field.name] = field.verbose_name
        readable_field_names['id'] = 'Internal ID'
        for name, value in self.get_iterable_fields():
            if name == 'id':
                continue
            try:
                value = getattr(self, "get_{}_display".format(name))()
            except Exception:
                pass
            result.append(
                (name, value, readable_field_names.get(name, name).capitalize())
            )
        return result

    @cached_property
    def required_documents_uploaded(self):
        """
        True if the conditions were met
        """
        has_information_form = self.documents.filter(
            type=CertificateDocument.TYPE_INFORMATION_FORM
        ).exists()
        # has_evidence_of_o = self.documents.filter(
        #     type=CertificateDocument.TYPE_EVIDENCE_OF_ORIGIN
        # ).exists()
        has_evidence_of_o = True
        return has_information_form and has_evidence_of_o

    @property
    def can_be_updated(self):
        return self.status in [
            self.STATUS_DRAFT,
            self.STATUS_COMPLETE
        ]


class CertificateDocument(models.Model):
    TYPE_INFORMATION_FORM = 'Exporters Information Form Update'
    TYPE_EVIDENCE_OF_ORIGIN = 'Evidence of origin'
    TYPE_EXTRA_INT = 'extra_int'
    TYPE_EXTRA_UPSTREAM = 'extra_upstream'

    TYPE_CHOICES = (
        (TYPE_INFORMATION_FORM, '[Upstream] Exporters Information Form Update, required'),
        (TYPE_EVIDENCE_OF_ORIGIN, '[Local] Evidence of origin, optional'),
        (TYPE_EXTRA_INT, '[Local] Extra document'),
        (TYPE_EXTRA_UPSTREAM, '[Upstream] Extra document'),
    )

    EXTERNAL_TYPES = (
        # document types to be uploaded to upstream
        TYPE_INFORMATION_FORM,
        TYPE_EXTRA_UPSTREAM,
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    certificate = models.ForeignKey(
        Certificate, models.CASCADE,
        related_name="documents"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)

    file = models.FileField(upload_to='certificate-application-documents')
    type = models.CharField(max_length=40, choices=TYPE_CHOICES)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.file)

    @property
    def is_upstream(self):
        return '[upstream]' in self.get_type_display().lower()

    @cached_property
    def filename(self):
        """Return just file name, without the path"""
        try:
            return os.path.basename(self.file.name)
        except Exception:
            return 'file.bin'

    @property
    def short_filename(self):
        if len(self.filename) > 25:
            if '.' in self.filename:
                return self.filename[:15] + '...' + self.filename[-10:]
            return self.filename[:22] + '...'
        return self.filename
