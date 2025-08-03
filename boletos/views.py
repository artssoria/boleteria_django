from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Boleto, Bus
from django import forms
from django.db import models
from django.db.models import Count, F
from datetime import datetime
from reportlab.pdfgen import canvas
from django.http import HttpResponse


class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = '__all__'
        widgets = {
            'fecha_viaje': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'hora_salida': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
        }


def crear_boleto(request):
    bus_id = request.GET.get('bus')
    bus = None
    asientos_ocupados = []
    total_asientos = []
    form = BoletoForm(request.POST or None)

    from django.db.models import Count, F
    buses = Bus.objects.annotate(
        vendidos=Count('boleto')
    ).filter(capacidad__gt=F('vendidos'))

    if bus_id:
        try:
            bus = Bus.objects.get(pk=bus_id)
            asientos_ocupados = list(Boleto.objects.filter(bus=bus).values_list('asiento', flat=True))
            total_asientos = list(range(1, bus.capacidad + 1))
        except Bus.DoesNotExist:
            bus = None

    if request.method == 'POST':
        if form.is_valid():
            boleto = form.save(commit=False)
            ocupados = Boleto.objects.filter(bus=boleto.bus).values_list('asiento', flat=True)
            if boleto.asiento in ocupados:
                form.add_error('asiento', f'El asiento {boleto.asiento} ya está ocupado.')
            elif boleto.asiento > boleto.bus.capacidad:
                form.add_error('asiento', 'Este asiento supera la capacidad del bus.')
            else:
                boleto.save()
                return redirect('listar_boletos')

    return render(request, 'boletos/crear_boleto.html', {
        'form': form,
        'asientos_ocupados': asientos_ocupados,
        'total_asientos': total_asientos,
        'bus_seleccionado': bus,
        'buses': buses,
    })
    
def listar_boletos(request):
    boletos = Boleto.objects.all().order_by('-fecha_viaje')
    return render(request, 'boletos/listar_boletos.html', {'boletos': boletos})

def buscar_boletos(request):
    consulta = request.GET.get('q', '')
    boletos = Boleto.objects.all()

    if consulta:
        boletos = boletos.filter(
            models.Q(destino__icontains=consulta) |
            models.Q(bus__empresa__icontains=consulta)
        )

    return render(request, 'boletos/buscar_boletos.html', {'boletos': boletos, 'consulta': consulta})

def detalle_boleto(request, pk):
    boleto = get_object_or_404(Boleto, pk=pk)
    return render(request, 'boletos/detalle_boleto.html', {'boleto': boleto})

def editar_boleto(request, pk):
    boleto = get_object_or_404(Boleto, pk=pk)
    if request.method == 'POST':
        form = BoletoForm(request.POST, instance=boleto)
        if form.is_valid():
            form.save()
            return redirect('listar_boletos')
    else:
        form = BoletoForm(instance=boleto)
    return render(request, 'boletos/editar_boleto.html', {'form': form})

def eliminar_boleto(request, pk):
    boleto = get_object_or_404(Boleto, pk=pk)
    if request.method == 'POST':
        boleto.delete()
        return redirect('listar_boletos')
    return render(request, 'boletos/eliminar_boleto.html', {'boleto': boleto})
    
def filtrar_por_fecha(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    boletos = Boleto.objects.all().order_by('-fecha_viaje')

    if desde and hasta:
        try:
            f_desde = datetime.strptime(desde, '%Y-%m-%d').date()
            f_hasta = datetime.strptime(hasta, '%Y-%m-%d').date()
            boletos = boletos.filter(fecha_viaje__range=(f_desde, f_hasta))
        except ValueError:
            pass 

    return render(request, 'boletos/filtro_fecha.html', {
        'boletos': boletos,
        'desde': desde,
        'hasta': hasta
    })
    
def registro_usuario(request):
    if request.method  == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('inicio')
    else:
        form = UserCreationForm()
    return render(request, 'boletos/registro.html', {'form':form})

import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader  # <-- Importante
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Boleto

def generar_pdf_boleto(request, pk):
    boleto = get_object_or_404(Boleto, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleto_{boleto.pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    x = 3 * cm
    y = height - 3 * cm

    # Título
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor("#0d6efd"))
    p.drawCentredString(width / 2, y, "🚍 Boletería Jujuy")
    y -= 1 * cm
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, y, "Comprobante oficial de pasaje")

    y -= 1 * cm
    p.setLineWidth(0.5)
    p.line(x, y, width - x, y)

    # Info del boleto
    y -= 1.5 * cm
    datos = [
        ("Pasajero:", boleto.nombre_pasajero),
        ("Destino:", boleto.destino),
        ("Fecha y Hora:", f"{boleto.fecha_viaje} - {boleto.hora_salida}"),
        ("Precio:", f"${boleto.precio}"),
        ("Bus:", str(boleto.bus)),
        ("Asiento:", str(boleto.asiento))
    ]

    for label, value in datos:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(x, y, label)
        p.setFont("Helvetica", 12)
        p.drawString(x + 4 * cm, y, value)
        y -= 1 * cm

    # Generar QR
    qr_texto = f"""Pasajero: {boleto.nombre_pasajero}
Destino: {boleto.destino}
Fecha: {boleto.fecha_viaje}
Hora: {boleto.hora_salida}
Asiento: {boleto.asiento}
Bus: {boleto.bus}"""

    qr_img = qrcode.make(qr_texto)
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)

    # Convertir el buffer a una imagen que ReportLab pueda usar
    qr_reader = ImageReader(buffer)
    p.drawImage(qr_reader, width - 6 * cm, 3 * cm, width=4 * cm, height=4 * cm)

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 2 * cm, "Gracias por viajar con Boletería Jujuy")

    p.showPage()
    p.save()
    return response