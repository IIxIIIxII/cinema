from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from .models import Movie, Screening
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Ticket, Screening # убедись, что Screening и Ticket добавлены
from .services import send_ticket_email

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'cinema/movie_list.html', {'movies': movies})

def movie_detail(request, movie_id):
    # Ищем фильм по ID, если нет — ошибка 404
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # Ищем все сеансы для этого фильма
    screenings = Screening.objects.filter(movie=movie)
    
    return render(request, 'cinema/movie_detail.html', {
        'movie': movie, 
        'screenings': screenings
    })

# Класс для регистрации
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # После регистрации перекинем на вход
    template_name = 'registration/signup.html'


@login_required  # Только для авторизованных!
def booking(request, screening_id):
    screening = get_object_or_404(Screening, pk=screening_id)
    hall = screening.hall

    # Получаем список уже занятых мест [(ряд, место), (ряд, место)...]
    taken_seats = Ticket.objects.filter(screening=screening).values_list('row', 'seat')

    # Формируем матрицу зала для отрисовки
    # Это будет список рядов, где каждый ряд - список мест
    seat_matrix = []
    for r in range(1, hall.rows + 1):
        row_seats = []
        for s in range(1, hall.seats_per_row + 1):
            is_taken = (r, s) in taken_seats
            row_seats.append({'row': r, 'seat': s, 'is_taken': is_taken})
        seat_matrix.append(row_seats)

    if request.method == 'POST':
        # Получаем данные из формы (ряд и место)
        row = int(request.POST.get('row'))
        seat = int(request.POST.get('seat'))

        # Двойная проверка: не заняли ли место, пока мы думали
        if Ticket.objects.filter(screening=screening, row=row, seat=seat).exists():
            messages.error(request, "Это место уже занято!")
            return redirect('booking', screening_id=screening_id)

        # Создаем билет
        ticket = Ticket.objects.create(
            user=request.user,
            screening=screening,
            row=row,
            seat=seat
        )

        # Отправляем PDF на почту
        try:
            send_ticket_email(ticket)
            messages.success(request, f"Билет куплен! Проверьте почту {request.user.email}")
        except Exception as e:
            messages.warning(request, "Билет куплен, но не удалось отправить письмо.")
            print(e)

        return redirect('movie_list') # Или на страницу "Мои билеты", которую сделаем позже

    return render(request, 'cinema/booking.html', {
        'screening': screening,
        'seat_matrix': seat_matrix
    })


@login_required
def my_tickets(request):
    # Показываем только билеты текущего пользователя, сначала новые
    tickets = Ticket.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'cinema/my_tickets.html', {'tickets': tickets})

@login_required
def cancel_ticket(request, ticket_id):
    # Ищем билет. Важно: ищем только среди билетов ЭТОГО пользователя (user=request.user)
    # Это требование Безопасности: чтобы Петя не удалил билет Васи.
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    
    # Удаляем
    ticket.delete()
    messages.success(request, "Бронь успешно отменена.")
    
    return redirect('my_tickets')