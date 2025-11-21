import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def generate_ticket_pdf(ticket):
    """
    Возвращает байты PDF и имя файла.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Простая верстка билета
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Кинотеатр — Билет")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Имя: {ticket.buyer_name}")
    c.drawString(50, height - 110, f"Фильм: {ticket.screening.movie.title}")
    c.drawString(50, height - 130, f"Зал: {ticket.screening.hall.name}")
    c.drawString(50, height - 150, f"Время сеанса: {ticket.screening.start_time.strftime('%Y-%m-%d %H:%M')}")
    if ticket.seat_number:
        c.drawString(50, height - 170, f"Место: {ticket.seat_number}")
    c.drawString(50, height - 200, f"Цена: {ticket.screening.price} {''}")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Спасибо за покупку! Покажите этот билет на входе.")
    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    filename = f"ticket_{ticket.id}.pdf"
    return pdf, filename

def attach_pdf_and_send_email(ticket):
    pdf_bytes, filename = generate_ticket_pdf(ticket)
    # Сохраняем PDF в поле модели (опционально)
    ticket.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

    # Подготовить письмо
    subject = f"Ваш билет — {ticket.screening.movie.title}"
    body = render_to_string('cinema/email_ticket.txt', {
        'ticket': ticket,
    })
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ticket.buyer_email],
    )
    email.attach(filename, pdf_bytes, 'application/pdf')
    email.send()
