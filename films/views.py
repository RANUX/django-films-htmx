from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, View, ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Case, When, IntegerField

from .models import Film, UserFilms
from .forms import RegisterForm
from .utils import get_max_order, reorder

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)


class CheckUsername(View):
    def post(self, request):
        username = request.POST.get('username')
        if get_user_model().objects.filter(username=username).exists():
            return HttpResponse("<div id='username-error' class='error'>This username already exists</div>")
        return HttpResponse("<div id='username-error' class='success'>This username is available</div>")


class FilmList(LoginRequiredMixin, ListView):
    template_name = 'films.html'
    model = Film
    context_object_name = 'films'
    paginate_by = 10

    def get_queryset(self):
        return UserFilms.objects.select_related('film').filter(user=self.request.user)

    def get_template_names(self):
        if self.request.htmx:
            return 'partials/film-list-elements.html'
        return 'films.html'

class AddFilm(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get('filmname')

        film, _ = Film.objects.get_or_create(name=name) 

        if not UserFilms.objects.filter(film=film, user=request.user).exists():
            UserFilms.objects.create(
                film=film, 
                user=request.user, 
                order=get_max_order(request.user )
            )

        films = UserFilms.objects.select_related('film').filter(user=request.user)
        messages.success(request, f'Added {name} to list of films')
        return render(request, 'partials/film-list.html', { 'films': films })

class DeleteFilm(LoginRequiredMixin, View):
    def delete(self, request, pk):
        UserFilms.objects.get(pk=pk).delete()
        reorder(user=request.user)
        films = UserFilms.objects.select_related('film').filter(user=request.user)
        return render(request, 'partials/film-list.html', { 'films': films })

class SearchFilm(LoginRequiredMixin, View):
    def post(self, request):
        search_text = request.POST.get('search')
        user_films = UserFilms.objects.filter(user=request.user)
        results = Film.objects.filter(name__icontains=search_text).exclude(
            name__in=user_films.values_list('film__name', flat=True)
        )
        return render(request, 'partials/search-results.html', { 'results': results })

class ClearTextContent(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('')

class SortFilms(LoginRequiredMixin, View):
    def post(self, request):
        film_pks_order = request.POST.getlist('film_order')
        films = []
        updated_films = []

        # Get a queryset of UserFilms objects related to the user making the request
        userfilms = UserFilms.objects.select_related('film').filter(user=self.request.user)

        # Loop through each film pk in the film_pks_order list
        for idx, film_pk in enumerate(film_pks_order, start=1):
            # userfilm = UserFilms.objects.get(pk=film_pk)
            # Get the UserFilms object with a primary key matching the current film_pk without hitting db
            userfilm = next(u for u in userfilms if u.pk == int(film_pk))

            # If the order of the UserFilms object doesn't match the current index, update it
            if userfilm.order != idx:
                userfilm.order = idx
                updated_films.append(userfilm)
            # userfilm.save()
            films.append(userfilm)

        # Update the order values for all UserFilms objects that were modified
        UserFilms.objects.bulk_update(updated_films, ['order'])

        # In this code, we first convert the list of film primary keys to integers 
        # (assuming they were originally strings).
        # Next, we use the Case and When functions from Django's ORM to build 
        # a series of conditional expressions that will update the order 
        # field of each UserFilms object with the corresponding value from the enumerate function.
        # Finally, we use the update method to perform a bulk update of all 
        # UserFilms objects whose primary keys are in the film_pks_order list,
        #  using the conditional expressions we built with Case and When. 
        # We then retrieve the updated UserFilms objects using a standard queryset filter.
        # This approach is more efficient than updating each UserFilms object individually, 
        # as it reduces the number of database queries required to update the objects.

        # film_pks_order = request.POST.getlist('film_order')
        # film_pks_order = [int(pk) for pk in film_pks_order]

        # # Build a Case/When statement to update the order field for each UserFilms object
        # cases = [When(pk=pk, then=order) for order, pk in enumerate(film_pks_order, start=1)]

        # # Use bulk update to update the order field for all UserFilms objects at once
        # UserFilms.objects.filter(pk__in=film_pks_order, user=self.request.user).update(order=Case(*cases, output_field=IntegerField()))

        # # Retrieve the updated UserFilms objects
        #films = UserFilms.objects.select_related('film').filter(pk__in=film_pks_order, user=self.request.user)

        return render(request, 'partials/film-list.html', { 'films': films })



class FilmDetail(LoginRequiredMixin, DetailView):
    model = UserFilms
    template_name = 'partials/film-detail.html'
    context_object_name = 'userfilm'


class FilmsPartial(LoginRequiredMixin, ListView):
    model = UserFilms
    template_name = 'partials/film-list.html'
    context_object_name = 'films'

    def get_queryset(self):
        return self.model.objects.select_related('film').filter(user=self.request.user)

class UploadPhoto(LoginRequiredMixin, DetailView):
    model = UserFilms
    template_name = 'partials/film-detail.html'
    context_object_name = 'userfilm'

    def post(self, request, **kwargs):
        self.object = self.get_object()
        photo = request.FILES.get('photo')
        self.object.film.photo.save(photo.name, photo)
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)