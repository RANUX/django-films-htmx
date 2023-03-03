from django.db.models import Max
from films.models import UserFilms
from django.db.models import Case, When, F

def get_max_order(user) -> int:
    existing_films = UserFilms.objects.filter(user=user)
    if not existing_films.exists():
        return 1
    else:
        current_max = existing_films.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


# def reorder(user):
#     existing_films = UserFilms.objects.filter(user=user)
#     if not existing_films.exists():
#         return
#     number_of_films = existing_films.count()
#     new_ordering = range(1, number_of_films+1)
    
#     for order, user_film in zip(new_ordering, existing_films):
#         user_film.order = order
#         user_film.save()



def reorder(user):
    existing_films = UserFilms.objects.filter(user=user)
    if not existing_films.exists():
        return
    number_of_films = existing_films.count()
    new_ordering = range(1, number_of_films+1)

    # Create a list of tuples with the ID and new order for each UserFilm
    id_order_pairs = [(film.id, order) for order, film in zip(new_ordering, existing_films)]

    # Use the update() method to perform a bulk update on all UserFilms for this user
    UserFilms.objects.filter(id__in=[film[0] for film in id_order_pairs]).update(
        order=Case(
            *[When(id=film[0], then=film[1]) for film in id_order_pairs],
            output_field=F('order')
        )
    )