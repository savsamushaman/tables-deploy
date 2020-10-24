from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import BusinessModel
from .forms import CreateBusinessForm
from django.views.generic import CreateView


class CreateBusinessView(LoginRequiredMixin, CreateView):
    model = BusinessModel
    template_name = 'business/create.html'
    form_class = CreateBusinessForm
    success_url = reverse_lazy('user_details')

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)
