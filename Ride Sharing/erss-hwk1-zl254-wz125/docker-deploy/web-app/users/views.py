
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
#这里用了继承的form，为了添加新的field
from .forms import UserRegisterForm
from request.models import RequestofDriver
from request.forms import driverUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('roles')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    _driver=RequestofDriver.objects.filter(driver = request.user)
    context={'driver':_driver}
    return render(request, 'users/profile.html',context)


@login_required
def roles(request):
    #if request.users
    return render(request, 'users/roles.html')

@login_required
def judgedriver(request):
    _driver=RequestofDriver.objects.filter(driver = request.user)
    
        
    if len(_driver)>0:
        if request.method == 'POST':
            driver_form = driverUpdateForm(request.POST)
        #print (p_form.fields.des)
            if driver_form.is_valid():
            #print(RequestofOwner_id)
                current_driver = RequestofDriver.objects.get(driver = request.user)
                _Vehicle = driver_form.cleaned_data.get("Vehicle")
                _Licenseplatenumber = driver_form.cleaned_data.get("License_plate_number")
                _Maximumpassengersnumber = driver_form.cleaned_data.get("Maximum_passengers_number")
                _s_request = driver_form.cleaned_data.get("Special_Request")

                current_driver.Vehicle = _Vehicle
                current_driver.Licenseplatenumber = _Licenseplatenumber
                current_driver.Maximumpassengersnumber = _Maximumpassengersnumber
                current_driver.s_request =_s_request
                current_driver.save()

                messages.success(request, f'Your driver\'s account has been updated!')
                return redirect('driver-pick')
        #return render(request,'request/driverinfoupdate.html', context)
        else:
    #u_form = UserUpdateForm(instance=request.user)
            driver_form = driverUpdateForm()
        context = {
        'form': driver_form }
        return render(request, 'request/driverinfoupdate.html', context)

    else:
        return redirect('driver-create')
    #return render(request, 'request/driverinfoupdate.html', context)


