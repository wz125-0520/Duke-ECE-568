from django import forms
from .models import RequestofOwner


class ownerUpdateForm(forms.Form):
	Destination = forms.CharField(max_length=200)
	Start_Time = forms.DateTimeField(help_text='Format: 2019-01-01 12:00')
	Share_Valid = forms.BooleanField(required=False)
	Maximum_Passagener_Number = forms.IntegerField()
	Special_Request = forms.CharField(max_length=200,required=False)
	Vehicle_Type = forms.CharField(max_length=200,required=False)
	
class driverUpdateForm(forms.Form):
	Vehicle = forms.CharField(max_length=100)
	License_plate_number = forms.IntegerField()
	Maximum_passengers_number = forms.IntegerField()
	Special_Request = forms.CharField(max_length=200,required=False)
	Driver_name=forms.CharField(max_length=200)