from rest_framework import serializers

from chambers_app.certificates.models import Certificate, CertificateDocument
# from chambers_app.organisations.models import ChamberOfCommerce


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateDocument
        fields = (
            'id', 'filename', 'type', 'created_at',
        )
        # read_only_fields = ('id', 'created_at')


class CertShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('id', 'status', 'created_at', 'dst_country')


class CertFullSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = (
            'id', 'status', 'created_at', 'dst_country',
            # business data
            'exporter_info', 'producer_info', 'importer_info', 'transport_info',
            'remarks', 'item_no', 'packages_marks', 'goods_descr',
            'hs_code', 'invoice_info', 'origin_criterion',
            'documents',
        )
        read_only_fields = ('id', 'status', 'created_at', 'documents')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        data = super().validate(data)
        assert self.user
        assert self.user.is_authenticated
        # TODO: for non-draft certificate we can't change anything here
        if self.instance and self.instance.pk is not None:
            if self.instance.status not in (Certificate.STATUS_DRAFT, Certificate.STATUS_COMPLETE):
                raise serializers.ValidationError(
                    "Can't update object - update is available only for draft or complete status"
                )
        # if 'org' in data:
        #     if self.user not in data['org'].users.all():
        #         # we mimic ObjectNotFound exception
        #         org_pk = data['org'].pk
        #         raise serializers.ValidationError(
        #             f'Invalid pk "{org_pk}" - object does not exist.'
        #         )
        return data

    def create(self):
        assert self.user
        kwargs = self.data.copy()
        # kwargs['org'] = ChamberOfCommerce.objects.get(
        #     pk=kwargs['org'],
        #     users__in=[self.user]
        # )
        new_obj = Certificate.objects.create(
            created_by=self.user,
            **kwargs
        )
        return new_obj
