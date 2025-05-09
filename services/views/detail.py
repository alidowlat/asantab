from django.views.generic import DetailView

from services.models import Service


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_product = self.object