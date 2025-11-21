from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .models import Movie, Screening, Ticket
from .forms import PurchaseForm
from .utils import attach_pdf_and_send_email

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'cinema/movie_list.html', {'movies': movies})

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    screenings = movie.screenings.all().filter(start_time__gte__now())  # import django.utils.timezone.now if needed
    return render(request, 'cinema/movie_detail.html', {'movie': movie, 'screenings': screenings})

class PurchaseView(View):
    def get(self, request, screening_id):
        screening = get_object_or_404(Screening, id=screening_id)
        form = PurchaseForm()
        return render(request, 'cinema/purchase.html', {'form': form, 'screening': screening})

    def post(self, request, screening_id):
        screening = get_object_or_404(Screening, id=screening_id)
        form = PurchaseForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.screening = screening
            ticket.save()
            # Генерация PDF + отправка на почту
            attach_pdf_and_send_email(ticket)
            return redirect(reverse('cinema:purchase_success', args=[ticket.id]))
        return render(request, 'cinema/purchase.html', {'form': form, 'screening': screening})

def purchase_success(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'cinema/purchase_success.html', {'ticket': ticket})
