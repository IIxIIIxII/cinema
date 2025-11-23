from django.contrib import admin
from .models import Movie, Hall, Screening, Ticket

admin.site.register(Movie)
admin.site.register(Hall)
admin.site.register(Screening)
admin.site.register(Ticket)