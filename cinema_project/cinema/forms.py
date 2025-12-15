from django import forms
# Вам нужно импортировать модель Screening (и, возможно, Hall, если она там)
from .models import Movie, Screening, Hall

class MovieForm(forms.ModelForm):
    """Форма для редактирования информации о фильме."""
    class Meta:
        model = Movie
        # Указываем поля, которые можно редактировать
        fields = ['title', 'description', 'poster', 'duration_minutes']
        
        # Дополнительная настройка для удобства
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ScreeningForm(forms.ModelForm):
    """Форма для создания нового сеанса."""
    class Meta:
        model = Screening
        # Поля, которые нужно заполнять: какой фильм (movie), какой зал (hall), 
        # время начала (start_time), и цена (price)
        fields = ['movie', 'hall', 'start_time', 'price']
        
        widgets = {
            # Удобно использовать встроенный HTML5 виджет для даты и времени
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            # Скрываем поле фильма, если мы пришли со страницы фильма
            'movie': forms.HiddenInput(), 
        }