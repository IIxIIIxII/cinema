from django.db import models
from django.conf import settings

class Hall(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)

    def __str__(self):
        return self.title

class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings')
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.movie.title} — {self.start_time} ({self.hall.name})"

class Ticket(models.Model):
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    seat_number = models.CharField(max_length=20, blank=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='tickets_pdfs/', blank=True, null=True)

    def __str__(self):
        return f"Билет: {self.buyer_name} — {self.screening}"
