from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class RequestofDriver(models.Model):
	Vehicle = models.CharField(max_length=100)
	Licenseplatenumber = models.IntegerField(default=0)
	Maximumpassengersnumber = models.IntegerField(default=0)
	isDriver = models.BooleanField(default=False)
	driver = models.ForeignKey(User, on_delete=models.CASCADE)
	s_request =models.CharField(max_length=100,blank=True,verbose_name='Special Request')
	driver_name=models.CharField(max_length=100)
	def get_absolute_url(self):
		return reverse('driver-pick')


class RequestofOwner(models.Model):

	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	des= models.CharField(max_length=200, verbose_name='Destination')
	start_time = models.DateTimeField(verbose_name='Start Time', help_text='Format: 2019-01-01 12:00')
	status= models.IntegerField(default=0, verbose_name='Ride Status (open, confirmed, complete)')
	share_valid = models.BooleanField(default=False, verbose_name='Do you want to share the ride with others?')
	#$share_max_num = models.IntegerField(verbose_name='The maximum sharers you can accept')
	max_pas_num = models.IntegerField(verbose_name=" Maximum Number of Passengers", default=0)
	#currentnum=	models.IntegerField(default=max_pas_num)
	total_num=models.IntegerField(default=0)

	sharer_pas_num = models.IntegerField(default=0)

	request = models.CharField(max_length=200,blank=True)
	vehicle = models.CharField(max_length=200, verbose_name='Vehicle Type',blank=True)
	sharer_name = models.CharField(max_length=200)
	driver_name =models.CharField(max_length=200)	
	actual_vehicle=models.CharField(max_length=200)
	def get_absolute_url(self):
		return reverse('owner-orders')

class RequestofSharer(models.Model):
	sharer = models.ForeignKey(User, on_delete=models.CASCADE)
	des = models.CharField(max_length=200, verbose_name='Destination')
	start_date_0 = models.DateTimeField(verbose_name='Earliest acceptable start date', help_text='Format: 2019-01-01 12:00')
	start_date_1 = models.DateTimeField(verbose_name='Latest acceptable start date', help_text='Format: 2019-01-01 12:00')
	sharer_num = models.IntegerField(default=1)

	def get_absolute_url(self):
		return reverse('sharer-join-view' )

