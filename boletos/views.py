from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Boleto
from django import forms
from django.db import models
from datetime import datetime

class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = '__all__'

def crear_boleto(request):
    if request.method == 'POST':
        form = BoletoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_boletos') 
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
