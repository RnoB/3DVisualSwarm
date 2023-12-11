from django.db import models
from django.utils import timezone


class experiments(models.Model):
    expId = models.CharField(max_length=200)
    repId = models.CharField(max_length=200)
    date = models.CharField(max_length=200)
    N = models.IntegerField()
    nPhi = models.IntegerField()
    dt = models.FloatField()
    v0 = models.FloatField()
    drag = models.FloatField()
    Vuu = models.FloatField()
    Vpp = models.FloatField()
    Vzz = models.FloatField()
    Vu = models.FloatField()
    Vp = models.FloatField()
    Vz = models.FloatField()
    dVu = models.FloatField()
    dVp = models.FloatField()
    dVz = models.FloatField()
    dtVu = models.FloatField()
    dtVp = models.FloatField()
    dtVz = models.FloatField()
    youtube = models.CharField(max_length=200)