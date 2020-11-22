from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):   
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    address = models.CharField(max_length = 50, verbose_name="Address", default = '', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


PACKAGE_STATUS = (
    ("created", "created"),
    ("in the warehouse", "in the warehouse"),
    ("out for delivery", "out for delivery"),
    ("delivered", "delivered")
)

EVALUATION_STATUS = (
    ("excellent", "excellent"),
    ("good", "good"),
    ("fair", "fair"),
    ("dissatisfied", "dissatisfied")
)

class Package(models.Model):
    packageid = models.BigIntegerField()
    owner = models.CharField(max_length = 30, null=True)
    destx = models.IntegerField(null=True)
    desty = models.IntegerField(null=True)
    packagestatus = models.CharField(max_length = 30, choices = PACKAGE_STATUS, default = 'created')
    description = models.TextField(blank = True, default = '')
    truckid = models.IntegerField(null=True)
    evaluation = models.CharField(max_length = 30, choices = EVALUATION_STATUS, default = 'none')


    def __str__(self):
        return f'{self.packageid}'

    #When submit, the webpage will go to the certain place
    def get_absolute_url(self):
        return reverse('package-list')

TRUCK_STATUS = (
    ("idle", "idle"),
    ("on the way to warehouse", "on the way to warehouse"),
    ("arrived at warehouse", "arrived at warehouse"),
    ("delivering", "delivering")
)

class Truck(models.Model):
    truckid = models.IntegerField()
    truckstatus = models.CharField(max_length = 40, choices = TRUCK_STATUS, default = 'idle')

    def __str__(self):
        return f'{self.truckid}'


class Search(models.Model):
    trackingNumber = models.BigIntegerField()

    def __str__(self):
        return f'{self.trackingNumber}'

    #When submit, the webpage will go to the certain place
    def get_absolute_url(self):
        return reverse('search-list')