from django.db import models
from django.contrib.auth.models import User


class Gasto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    categoria = models.CharField(max_length=100)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.categoria} - {self.valor}"


class MetaFinanceira(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mes = models.DateField()
    valor_meta = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Meta {self.mes}"
