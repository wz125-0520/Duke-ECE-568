from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class OwnerNSharer(models.Model):
	usrname = models.ForeignKey(User, on_delete=models.CASCADE)
	destination = models.CharField(max_length=100)
    ##content = models.TextField()
	time_start= models.DateTimeField(default=timezone.now)
	time_end= models.DateTimeField(default=timezone.now)
	vehicletype=models.CharField(max_length=100)

	def __str__(self):
		return self.destination




