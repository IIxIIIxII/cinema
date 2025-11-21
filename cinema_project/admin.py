from django.contrib import admin
from .models import Movie, Hall, Screening, Ticket

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes')

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'price')
    list_filter = ('hall', 'start_time', 'movie')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'buyer_email', 'screening', 'created_at')
    readonly_fields = ('created_at', 'pdf_file')
