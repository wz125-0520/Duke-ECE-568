from django.shortcuts import render, redirect
from .models import Profile, Package, Search
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.core.mail import send_mail
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'ups/home.html')


class SearchCreateView(CreateView):
    model = Search
    fields = ['trackingNumber']

    def form_valid(self, form):
        return super().form_valid(form)


class SearchListView(ListView):
    template_name = 'ups/search_list.html'

    def get_queryset(self):
        s = Search.objects.last()
        return Package.objects.filter(packageid=s.trackingNumber)


class PackageListView(ListView):
    model = Package
    template_name = 'ups/package_list.html'

    def get_queryset(self):
        return Package.objects.filter(owner=self.request.user.username)


class PackageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Package
    fields = ['destx', 'desty']

    def form_valid(self, form):
        form.instance.owner = self.request.user.username
        return super().form_valid(form)

    def test_func(self):
        package = self.get_object()
        if self.request.user.username == package.owner:
            return True
        return False


class PackageEvaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Package
    fields = ['evaluation']

    def form_valid(self, form):
        form.instance.owner = self.request.user.username
        return super().form_valid(form)

    def test_func(self):
        package = self.get_object()
        if self.request.user.username == package.owner:
            return True
        return False



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'You account have already created. You can login now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'ups/register.html', {'form': form})



@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'ups/profile.html', context)