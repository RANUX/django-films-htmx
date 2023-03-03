from django.urls import path
from films import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("films/", views.FilmList.as_view(), name='film-list'),
]

htmx_urlpatterns = [
    path('check-username/', views.CheckUsername.as_view(), name='check-username'),
    path('add-film/', views.AddFilm.as_view(), name='add-film'),
    path('delete-film/<int:pk>/', views.DeleteFilm.as_view(), name='delete-film'),
    path('search-film/', views.SearchFilm.as_view(), name='search-film'),
    path('clear/', views.ClearTextContent.as_view(), name='clear'),
    path('sort/', views.SortFilms.as_view(), name='sort'),
    path('detail/<int:pk>/', views.FilmDetail.as_view(), name='detail'),
    path('film-list-partial', views.FilmsPartial.as_view(), name='film-list-partial'),
    path('upload-photo/<int:pk>/', views.UploadPhoto.as_view(), name='upload-photo'),
]

urlpatterns += htmx_urlpatterns