from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO


# Функции link_callback больше нет


def send_ticket_email(ticket):
    """
    Генерирует PDF из HTML-шаблона и отправляет на почту пользователя.
    """
    # 1. Данные для шаблона билета
    context = {'ticket': ticket}
    html_string = render_to_string('cinema/ticket_pdf.html', context)

    # 2. Генерация PDF в память
    result = BytesIO()
    
    # Генерация PDF. link_callback больше не нужен.
    pdf = pisa.pisaDocument(
        BytesIO(html_string.encode("UTF-8")), 
        result
    )
    
    if pdf.err:
        # Для отладки
        print("Ошибка генерации PDF:", pdf.err)
        return

    # 3. Создание письма
    email = EmailMessage(
        subject=f'Ваш билет: {ticket.screening.movie.title}',
        body=f'Здравствуйте, {ticket.user.username}! Спасибо за покупку. Ваш билет во вложении.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ticket.user.email],
    )

    # 4. Прикрепление PDF
    email.attach(f'ticket_{ticket.id}.pdf', result.getvalue(), 'application/pdf')

    # 5. Отправка
    email.send()