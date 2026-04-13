from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import SignupForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('shop:home')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})
