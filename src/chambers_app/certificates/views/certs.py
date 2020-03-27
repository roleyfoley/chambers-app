from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.views.generic import (
    DetailView, ListView, CreateView,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect

from chambers_app.certificates.forms import (
    CertificateCreateForm, CertDocumenteUploadForm, CertificateUpdateForm
)
from chambers_app.certificates.models import Certificate
from chambers_app.utils.monitoring import statsd_timer


class CertificateQuerysetMixin(object):

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


class CertificateListView(LoginRequired, CertificateQuerysetMixin, ListView):
    template_name = 'certificates/list.html'
    model = Certificate

    @statsd_timer("view.CertificateListView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CertificateCreateView(LoginRequired, CreateView):
    template_name = 'certificates/create.html'
    form_class = CertificateCreateForm

    @statsd_timer("view.CertificateCreateView.dispatch")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        k = super().get_form_kwargs()
        k['user'] = self.request.user
        return k

    def get_success_url(self):
        messages.success(
            self.request,
            "The draft certificate has been created."
        )
        return reverse('certificates:list')


class CertificateDetailView(LoginRequired, DetailView):
    template_name = 'certificates/detail.html'
    model = Certificate

    def get_context_data(self, *args, **kwargs):
        c = super().get_context_data(*args, **kwargs)
        certificate = self.get_object()
        c['file_upload_form'] = CertDocumenteUploadForm(
            certificate=certificate,
            user=self.request.user,
        )
        c['cert_update_form'] = CertificateUpdateForm(
            instance=certificate
        )
        return c

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if 'lodge-certificate' in request.POST:
            if obj.status == Certificate.STATUS_COMPLETE:
                obj.lodge()
                messages.success(request, 'The certificate has been lodged')
                return redirect(obj.get_absolute_url())
        elif 'file_upload' in request.POST:
            form = CertDocumenteUploadForm(
                request.POST, request.FILES,
                certificate=obj,
                user=request.user,
            )
            if form.is_valid():
                form.save()
                obj.save()
                messages.success(request, 'The document has been uploaded')
            else:
                messages.error(request, str(form.errors))
        if 'delete-document' in request.POST:
            try:
                doc = obj.documents.get(id=request.POST.get('delete-document'))
            except ObjectDoesNotExist:
                raise Http404()
            else:
                if doc.file:
                    doc.file.delete(save=False)
                doc.delete()
                obj.save()  # update object status
                messages.success(request, "The document has been deleted")

        if 'certificate-update' in request.POST:
            CertificateUpdateForm(request.POST, instance=obj).save()
            messages.success(request, "The certificate has been updated")

        return redirect(request.path_info)


class CertificateDocDownloadView(LoginRequired, CertificateQuerysetMixin, DetailView):

    def get_object(self):
        try:
            c = self.get_queryset().get(pk=self.kwargs['pk'])
            doc = c.documents.get(id=self.kwargs['doc_id'])
        except ObjectDoesNotExist:
            raise Http404()
        return doc

    def get(self, *args, **kwargs):
        # standard file approach
        document = self.get_object()
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="%s"' % document.file.name
        return response
