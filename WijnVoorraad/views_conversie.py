from WijnVoorraad.forms import StartConversieForm
from WijnVoorraad.models_oudwijn import OudDeelnemer


from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import FormView


class StartConversieView(LoginRequiredMixin, FormView):
    form_class = StartConversieForm
    template_name = "WijnVoorraad/startconversie.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Start conversie"
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["aantal_deelnemers_oud"] = OudDeelnemer.objects.using(
            "oudwijndb"
        ).count()
        return initial

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        url = reverse("WijnVoorraad:voorraadlist")
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
