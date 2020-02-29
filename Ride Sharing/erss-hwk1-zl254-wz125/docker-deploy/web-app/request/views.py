from django.shortcuts import render, redirect
from .models import RequestofDriver,RequestofOwner,RequestofSharer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView,DetailView,CreateView,UpdateView,DeleteView)
from .forms import ownerUpdateForm, driverUpdateForm
from django.db.models import Q,F
from django.core.mail import send_mail
from django.contrib.auth.models import User

def home(request):
    context = {
        'posts': RequestofDriver.objects.all() 
    }
    return render(request, 'request/home.html', context)


def about(request):
    return render(request, 'request/about.html', {'title': 'About'})

def test(request):
    return render(request, 'request/disp_driver.html')

# all current open orders for drivers
def allorders(request):
    instance = RequestofDriver.objects.get(driver=request.user)
    rides= RequestofOwner.objects.filter((Q(vehicle=instance.Vehicle)|Q(vehicle ="")),Q(status=0),
        Q(request=instance.s_request)).exclude(Q(owner=request.user)|Q(sharer_name=request.user.username))
    
    for rid in rides:
        #print("original"+rid.total_num)
        rid.total_num =rid.max_pas_num + rid.sharer_pas_num
        #print("after"+rid.total_num)
        rid.save()

    #total =rides.sharer_pas_num+rides.

    #rides.save()
    context = {
            #'posts': RequestofOwner.objects.filter((Q(vehicle=instance.Vehicle)|Q(vehicle ="")),Q(status=0),
            # Q(max_pas_num__lte=instance.Maximumpassengersnumber),Q(request=instance.s_request))
            'posts':rides.filter(total_num__lte=instance.Maximumpassengersnumber)

        }
    return render(request, 'request/disp_driver.html', context)


def driverclaim(request,RequestofOwner_id):
    current = RequestofOwner.objects.get(id = RequestofOwner_id )
    driver_object=RequestofDriver.objects.get(driver = request.user)
    current.status=1
    current.driver_name=driver_object.driver_name
    current.actual_vehicle=driver_object.Vehicle
    current.save()
    send_mail(
        'Ride Confirmation Reminder',
        'Hi. You picked the ride successfully. Have a good trip!',
        'Duke Ride Sharing',
        [request.user.email],
        fail_silently=False,
    )
    send_mail(
        'Ride Confirmation Reminder',
        'Hi. The ride that you requested has been confirmed by a driver successfully. Have a good trip!',
        'Duke Ride Sharing',
        [current.owner.email],
        fail_silently=False,
    )
    sharer = User.objects.filter(username=current.sharer_name).last()
    if sharer:
        send_mail(
            'Ride Confirmation Reminder',
            'Hi. The ride that you want to share has been confirmed by a driver successfully. Have a good trip!',
            'Duke Ride Sharing',
            [sharer.email],
            fail_silently=False,
        )
    context = {
        'posts': RequestofOwner.objects.filter(status=0) 
    }
    return render(request, 'request/disp_driver.html', context)
# history view
def driverhistory(request):
    context = {
        'posts': RequestofOwner.objects.filter(status=1) 
    }
    return render(request, 'request/driverhistory.html', context)

def sharerhistory(request):
    context = {
        'posts': RequestofOwner.objects.filter(sharer_name=request.user.username,status=0) ,
        'unposts': RequestofOwner.objects.filter(sharer_name=request.user.username,status=1)
    }
    return render(request, 'request/sharerhistory.html', context)
# edit history
def drivercomplete(request,RequestofOwner_id):
    current = RequestofOwner.objects.get(id = RequestofOwner_id )
    current.status=2
    current.save()
    send_mail(
        'Ride Confirmation Reminder',
        'Hi. You completed the ride successfully. Have a good trip!',
        'Duke Ride Sharing',
        [request.user.email],
        fail_silently=False,
    )
    send_mail(
        'Ride Confirmation Reminder',
        'Hi. The ride that you requested has been completed by a driver successfully. Have a good trip!',
        'Duke Ride Sharing',
        [current.owner.email],
        fail_silently=False,
    )
    sharer = User.objects.filter(username=current.sharer_name).last()
    if sharer:
        send_mail(
            'Ride Confirmation Reminder',
            'Hi. The ride that you want to share has been completed by a driver successfully. Have a good trip!',
            'Duke Ride Sharing',
            [sharer.email],
            fail_silently=False,
        )

    context = {
        'posts': RequestofOwner.objects.filter(status=1) 
    }
    return render(request, 'request/driverhistory.html', context)
#&Q(start_time=(start, end))
# sharer view
def sharerjoinview(request):

    curr_sharer = RequestofSharer.objects.filter(sharer = request.user).last()
    start = curr_sharer.start_date_0
    end = curr_sharer.start_date_1
    Destination=curr_sharer.des

    context = {
        'posts': RequestofOwner.objects.filter(Q(status=0),Q(des=Destination), Q(start_time__gte=start), 
                                               Q(start_time__lte=end)).exclude(Q(owner=request.user)|Q(sharer_name=request.user.username))}

    return render(request, 'request/sharerjoinview.html', context)

def sharercancel(request,RequestofOwner_id):
    curr = RequestofSharer.objects.filter(sharer = request.user).last()
    start = curr.start_date_0
    end = curr.start_date_1
    Destination=curr.des


    current = RequestofOwner.objects.get(id = RequestofOwner_id )
    current.sharer_pas_num-=request.user.requestofsharer_set.last().sharer_num
    #current.total_num-=request.user.requestofsharer_set.last().sharer_num
    current.sharer_name=""
    current.save()
    context = {
        'posts': RequestofOwner.objects.filter(Q(status=0), Q(sharer_name=request.user.username)),
        'unposts': RequestofOwner.objects.filter(sharer_name=request.user.username,status=1)}

    return render(request, 'request/sharerhistory.html', context)
    #return redirect('sharer-create')

def sharerjoin(request,RequestofOwner_id):
    current = RequestofOwner.objects.get(id = RequestofOwner_id )
    print(RequestofOwner_id)
    #current.max_pas_num +=request.user.requestofsharer_set.last().sharer_num
    current.sharer_name=request.user.username
    print("sharername"+current.sharer_name)
    current.sharer_pas_num+=request.user.requestofsharer_set.last().sharer_num
    #ride.share_name = request.user.username
    current.save()
    currelist=RequestofOwner.objects.filter(sharer_name=request.user.username,status=0) 
    context = {
        'posts': currelist,
        'unposts': RequestofOwner.objects.filter(sharer_name=request.user.username,status=1)
    }
    return render(request, 'request/sharerhistory.html', context)


class PostListView(ListView):
    model = RequestofDriver
    template_name = 'request/home.html'  # <app>/<model>_<viewtype>.html
    #context_object_name = 'posts'

def orders(request):
    context={'posts':RequestofOwner.objects.filter(Q(status =0), Q(owner=request.user)),
                'unposts':RequestofOwner.objects.filter(Q(status =1), Q(owner=request.user))}
    return render(request, 'request/orders.html',context)


def detail (request, RequestofOwner_id):
    if request.method == 'POST':
        p_form = ownerUpdateForm(request.POST)
        #print (p_form.fields.des)
        if p_form.is_valid():
            print(RequestofOwner_id)
            current = RequestofOwner.objects.get(id = RequestofOwner_id )
             
            _des = p_form.cleaned_data.get("Destination")
            
            _start_time = p_form.cleaned_data.get("Start_Time")
            #_status= p_form.cleaned_data.get("des")
            _share_valid = p_form.cleaned_data.get("Share_Valid")
            #$share_max_num = models.IntegerField(verbose_name='The maximum sharers you can accept')
            _max_pas_num = p_form.cleaned_data.get("Maximum_Passagener_Number")
            _request = p_form.cleaned_data.get("Special_Request")
            _vehicle = p_form.cleaned_data.get("Vehicle_Type")


            current.des = _des;
            current.start_time = _start_time
            current.share_valid = _share_valid
            current.max_pas_num = _max_pas_num 
            current.request = _request
            current.vehicle = _vehicle

            current.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('owner-orders')
    else:
    #u_form = UserUpdateForm(instance=request.user)
        p_form = ownerUpdateForm()

    context = {
        'form': p_form
}

    return render(request, 'request/order_update.html', context)


class DriverCreateView(LoginRequiredMixin, CreateView):
    model = RequestofDriver
    fields = ['Vehicle', 'Licenseplatenumber','Maximumpassengersnumber','s_request','driver_name']
    #template_name = 'request/home.html'

    def form_valid(self, form):

        form.instance.isDriver=True
        print("confirm:",form.instance.isDriver)
        form.instance.driver= self.request.user
        
        return super().form_valid(form)

class SharerCreateView(LoginRequiredMixin, CreateView):
    model = RequestofSharer
    fields = ['des', 'start_date_0','start_date_1','sharer_num']

    #template_name = 'request/home.html'
    #success_url = "{url 'sharer-join-view' id }"
    def form_valid(self, form):
        print(form.instance.id)
        #form.instance.isDriver=True
        #print("confirm:",form.instance.isDriver)
        form.instance.sharer= self.request.user
        
        return super().form_valid(form)


'''
class DriverUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RequestofDriver
    fields = ['Vehicle', 'Licenseplatenumber','Maximumpassengersnumber']
    template_name = 'request/disp_driver.html'
    #context_object_name = 'posts'
    def form_valid(self, form):
        form.instance.driver= self.request.user
        print("Update" )
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.driver:
            return True
        return False

'''
def driverupdate(request):
    if request.method == 'POST':
        driver_form = driverUpdateForm(request.POST)
        #print (p_form.fields.des)
        if driver_form.is_valid():
            #print(RequestofOwner_id)
            current_driver = RequestofDriver.objects.get(driver = request.user)
            _Vehicle = driver_form.cleaned_data.get("Vehicle")
            _Licenseplatenumber = driver_form.cleaned_data.get("License_plate_number")
            _Maximumpassengersnumber = driver_form.cleaned_data.get("Maximum_passengers_number")
            _specialrequest=driver_form.cleaned_data.get("Special_Request")
            _driver_name=driver_form.cleaned_data.get("Driver_name")

            current_driver.Vehicle = _Vehicle
            current_driver.Licenseplatenumber = _Licenseplatenumber
            current_driver.Maximumpassengersnumber = _Maximumpassengersnumber
            current_driver.s_request = _specialrequest
            
            current_driver.driver_name = _driver_name


            current_driver.save()
            messages.success(request, f'Your driver\'s account has been updated!')
            return redirect('driver-pick')
    else:
    #u_form = UserUpdateForm(instance=request.user)
        driver_form = driverUpdateForm()

    context = {
        'form': driver_form      
}

    return render(request, 'request/disp_driver.html', context)


class DriverDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = RequestofDriver
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.driver:
            return True
        return False

class OwnerCreateView(LoginRequiredMixin, CreateView):
    model = RequestofOwner
    fields = ['des','start_time','share_valid','max_pas_num','request','vehicle']
    #template_name = 'request/home.html'
    #def status_change(self, form)


    def form_valid(self, form):
        #form.instance.total_num=form.instance.max_pas_num
        form.instance.owner= self.request.user
        return super().form_valid(form)




'''
def driverInfo(request):
    if request.method == 'POST':
        p_form = DriverUpdateForm(request.POST)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
    #u_form = UserUpdateForm(instance=request.user)
        p_form = DriverUpdateForm()

        context = {
        'p_form': p_form
}

    return render(request, 'request/driverInfo.html', context)
'''
