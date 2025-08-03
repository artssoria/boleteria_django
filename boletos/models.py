from django.db import models

class Bus(models.Model):
    empresa = models.CharField(max_length=100)
    numero_interno = models.CharField(max_length=20)
    chofer = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField(default=60)

    def __str__(self):
        return f"{self.empresa} - Interno {self.numero_interno}"

class Boleto(models.Model):
    nombre_pasajero = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_viaje = models.DateField()
    hora_salida = models.TimeField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    asiento = models.PositiveIntegerField()
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_pasajero} - {self.destino} ({self.fecha_viaje})"