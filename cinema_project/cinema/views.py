from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse # <-- Импорт для отдачи файла
from django.template.loader import render_to_string # <-- Импорт для работы с шаблоном
from xhtml2pdf import pisa # <-- Импорт для генерации PDF
from io import BytesIO # <-- Импорт для работы с файлом в памяти

from .models import Movie, Screening, Ticket 
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
# from .services import send_ticket_email # <-- УДАЛЕНО: Больше не нужен
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin 
from .forms import MovieForm, ScreeningForm 
from django.views.generic.edit import CreateView, DeleteView
import traceback # Можно удалить, так как почта убрана, но пусть будет для общ. отладки


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
    success_url = reverse_lazy('login') 
    template_name = 'registration/signup.html'


@login_required  # Только для авторизованных!
def booking(request, screening_id):
    screening = get_object_or_404(Screening, pk=screening_id)
    hall = screening.hall

    # Получаем список уже занятых мест [(ряд, место), (ряд, место)...]
    taken_seats = Ticket.objects.filter(screening=screening).values_list('row', 'seat')

    # Формируем матрицу зала для отрисовки
    seat_matrix = []
    for r in range(1, hall.rows + 1):
        row_seats = []
        for s in range(1, hall.seats_per_row + 1):
            is_taken = (r, s) in taken_seats
            row_seats.append({'row': r, 'seat': s, 'is_taken': is_taken})
        seat_matrix.append(row_seats)

    if request.method == 'POST':
        # Получаем данные из формы (ряд и место)
        try:
            row = int(request.POST.get('row'))
            seat = int(request.POST.get('seat'))
        except (ValueError, TypeError):
            messages.error(request, "Некорректный выбор места.")
            return redirect('booking', screening_id=screening_id)


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

        # УСПЕШНАЯ ПОКУПКА: Перенаправляем на скачивание
        messages.success(request, "Билет успешно куплен!")
        return redirect('download_ticket', ticket_id=ticket.id) 

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
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    
    # Удаляем
    ticket.delete()
    messages.success(request, "Бронь успешно отменена.")
    
    return redirect('my_tickets')


# --- CRUD Views for Admin ---

class MovieUpdateView(UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'cinema/movie_edit.html' 
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get_success_url(self):
        return reverse_lazy('movie_detail', kwargs={'movie_id': self.object.pk})
    

class MovieCreateView(UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'cinema/movie_create.html' 
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get_success_url(self):
        return reverse_lazy('movie_detail', kwargs={'movie_id': self.object.pk})
    
class ScreeningCreateView(UserPassesTestMixin, CreateView):
    model = Screening
    form_class = ScreeningForm
    template_name = 'cinema/screening_create.html'
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get_initial(self):
        initial = super().get_initial()
        movie_id = self.kwargs.get('movie_id')
        if movie_id:
            try:
                movie = Movie.objects.get(pk=movie_id)
                initial['movie'] = movie
            except Movie.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs.get('movie_id')
        if movie_id:
             try:
                context['movie'] = Movie.objects.get(pk=movie_id)
             except Movie.DoesNotExist:
                pass
        return context

    def get_success_url(self):
        movie_id = self.object.movie.pk
        return reverse_lazy('movie_detail', kwargs={'movie_id': movie_id})
    
class MovieDeleteView(UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = 'cinema/movie_confirm_delete.html' 
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get_success_url(self):
        return reverse_lazy('movie_list')
    
@login_required
def download_ticket(request, ticket_id):
    """
    Генерирует PDF-файл билета и принудительно скачивает его.
    """
    # 1. Проверка безопасности: ищем билет только для текущего пользователя
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    
    # 2. Генерация HTML
    context = {'ticket': ticket}
    html_string = render_to_string('cinema/ticket_pdf.html', context)

    # 3. Генерация PDF в память
    result = BytesIO()
    
    # Генерация PDF
    pdf = pisa.pisaDocument(
        BytesIO(html_string.encode("UTF-8")), 
        result
    )

    if pdf.err:
        # Если генерация не удалась, выдаем ошибку пользователю
        print(f"Ошибка генерации PDF: {pdf.err}")
        messages.error(request, "Не удалось создать PDF-файл. Пожалуйста, попробуйте позже.")
        return redirect('my_tickets')

    # 4. Отправка файла пользователю
    # Устанавливаем заголовки для скачивания
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    
    return response