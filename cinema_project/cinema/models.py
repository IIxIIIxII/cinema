from django.db import models
from django.contrib.auth.models import User

# 1. Фильм
class Movie(models.Model):
    title = models.CharField("Название фильма", max_length=100)
    description = models.TextField("Описание")
    poster = models.ImageField("Постер", upload_to='posters/', blank=True, null=True)
    duration_minutes = models.IntegerField("Длительность (мин)")

    def __str__(self):
        return self.title

# 2. Зал
class Hall(models.Model):
    name = models.CharField("Название зала", max_length=50)
    rows = models.IntegerField("Количество рядов")
    seats_per_row = models.IntegerField("Мест в ряду")

    def __str__(self):
        return f"{self.name} ({self.rows}x{self.seats_per_row})"

# 3. Сеанс (Связывает Фильм и Зал)
class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name="Зал")
    start_time = models.DateTimeField("Время начала")
    price = models.DecimalField("Цена билета", max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d.%m %H:%M')}"

# 4. Билет (Покупка)
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='tickets')
    row = models.IntegerField("Ряд")
    seat = models.IntegerField("Место")
    booked_at = models.DateTimeField(auto_now_add=True) # Дата покупки

    class Meta:
        # Защита: нельзя купить два билета на одно и то же место
        unique_together = ('screening', 'row', 'seat')

    def __str__(self):
        return f"Билет: {self.screening.movie.title} (Ряд {self.row}, Место {self.seat})"