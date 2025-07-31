from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Boleto
from django import forms
from django.db import models

class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = '__all__'

def crear_boleto(request):
    if request.method == 'POST':
        form = BoletoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_boleto')
    else:
        form = BoletoForm()

    return render(request, 'boletos/crear_boleto.html', {'form': form})

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


from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import io

def generar_pdf_boleto(request, pk):
    boleto = get_object_or_404(Boleto, pk=pk)
    template = get_template("boletos/comprobante_pdf.html")
    html = template.render({"boleto": boleto})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=boleto_{boleto.id}.pdf"

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    return response