from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ToDo
from .forms import ToDoForm

def landing(request):
    todos = ToDo.objects.filter(user=request.user) if request.user.is_authenticated else None
    return render(request, 'landing.html', {'todos': todos})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def create_todo(request):
    if request.method == "POST":
        form = ToDoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect('landing')
    else:
        form = ToDoForm()
    return render(request, "create_todo.html", {"form": form})


@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    todo.delete()
    return redirect('landing')

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # or 'landing' depending on your desired redirect page
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import ToDoForm

@login_required
def update_todo(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    
    if request.method == 'POST':
        form = ToDoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('landing')
    else:
        form = ToDoForm(instance=todo)
    
    return render(request, 'update_todo.html', {'form': form})
@login_required
def toggle_status(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    if todo.status == 'Completed':
        todo.status = 'In Progress'
    else:
        todo.status = 'Completed'
    todo.save()
    return redirect('landing')

def about(request):
    return render(request, 'about.html')  # or 'todo_list/about.html' if nested




