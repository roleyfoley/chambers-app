import os

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins, generics, views, serializers
from rest_framework.response import Response

from chambers_app.certificates.models import Certificate, CertificateDocument

from .serializers import CertShortSerializer, CertFullSerializer, DocumentSerializer


class QsMixin(object):
    def get_queryset(self):
        qs = Certificate.objects.all()
        user = self.request.user
        if user.is_superuser:
            # no further checks for the superuser
            return qs
        my_orgs = user.chambersofcommerce.all()
        return qs.filter(
            org__in=my_orgs
        ) | qs.filter(
            created_by=user
        )

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])


class CertificateViewSet(QsMixin, generics.GenericAPIView, viewsets.ViewSet, mixins.UpdateModelMixin):
    queryset = Certificate.objects.all()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        kwargs['user'] = self.request.user
        return CertFullSerializer(*args, **kwargs)

    def list(self, request):
        # The only difference from the base list() procedure is providing a short serializer
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = CertShortSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CertShortSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        obj = serializer.create()
        return Response(
            CertShortSerializer(obj).data,
            status=status.HTTP_201_CREATED,
        )


class CertStatusPatchView(QsMixin, views.APIView):

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        new_status = request.data.get('status')
        if new_status not in (Certificate.STATUS_LODGED,):
            raise serializers.ValidationError(
                    "Can't update object - incorrect status value"
                )
        if new_status == Certificate.STATUS_LODGED and obj.status == obj.STATUS_COMPLETE:
            obj.lodge()
        return Response(
            CertShortSerializer(obj).data
        )


class DocumentUploadView(QsMixin, views.APIView):
    # a little too raw view, but given the complicated nature of the request

    def _validate_request(self):
        # do sanity check
        if not self.request.META['CONTENT_TYPE'].startswith('multipart/form-data'):
            raise serializers.ValidationError("multipart/form-data expected")
        if 'file' not in self.request.FILES:
            raise serializers.ValidationError("The file 'file' expected as multipart/form-data")
        if 'type' not in self.request.POST:
            raise serializers.ValidationError("Please provide the document type")
        return

    def post(self, request, *args, **kwargs):
        """
        Save the stored file.
        curl -X POST -F "file=@somefile.jpg" -H "Authorization: Token XXX" http://127.0.0.1:5255/api/v0/file/multipart/
        """
        self._validate_request()
        # TODO: check if fileobj is a file and it's readable and so on
        file_obj = request.FILES['file']
        file_type = request.POST.get('type')
        cert = self.get_object()

        if cert.status not in (Certificate.STATUS_COMPLETE, Certificate.STATUS_DRAFT):
            raise serializers.ValidationError("Can't upload file - wrong status of the certificate")

        document = CertificateDocument.objects.create(
            certificate=cert,
            created_by=request.user,
            type=file_type,
        )
        document.file.save(file_obj.name, file_obj, save=True)

        cert.save()

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )


class DocumentDetailsView(QsMixin, views.APIView):

    def delete(self, request, *args, **kwargs):
        cert = self.get_object()
        if cert.status not in (Certificate.STATUS_COMPLETE, Certificate.STATUS_DRAFT):
            raise serializers.ValidationError("Can't delete file - wrong status of the certificate")

        doc = get_object_or_404(
            cert.documents,
            pk=self.kwargs['docpk']
        )
        if doc.file:
            if os.path.isfile(doc.file.path):
                os.remove(doc.file.path)
        doc.delete()

        cert.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
