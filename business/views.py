from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .models import BusinessModel
from .forms import CreateBusinessForm
from django.views import View

# add createview def get post
class CreateBusinessView(LoginRequiredMixin, View):
    template_name = 'business/create.html'
    form = CreateBusinessForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form()})

    def post(self, request, *args, **kwargs):
        form = self.form(self.request.POST)
        if form.is_valid():
            new_data = request.POST.dict()
            del new_data['csrfmiddlewaretoken']
            BusinessModel.objects.create(manager=request.user, **new_data)
            return redirect('user_business_details')

        else:
            return render(request, self.template_name, {'form': self.form()})
