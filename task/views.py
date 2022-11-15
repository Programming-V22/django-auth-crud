# importations django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
#inicio 
def home(request):
    return render(request, 'home.html',)

#registrarse como usuario
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        if request.POST['password1']== request.POST['password2']:
            #register user
            try:
                user= User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html',
                    {'form': UserCreationForm,
                    'error':'Username already exists'
                })
        return render(request, 'signup.html', 
                      {'form': UserCreationForm,
                      'error':'Password do not match'
                      })

@login_required
#funcion mostrar todas las tareas
def tasks(request):
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html',{'tasks':tasks}) 

@login_required
#tareas completedas
def tasks_completed(request):
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('datecompleted')
    return render(request, 'tasks.html',{'tasks':tasks}) 

@login_required
#funcion crear tarea
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html',{'forms': TaskForm}) 
    else:
        try:
            form=TaskForm(request.POST)
            new_task=form.save(commit=False)
            new_task.user=request.user
            print(new_task)
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html',{'forms': TaskForm, 'error': 'Please provided valida data'}) 

@login_required
#funcion editar tarea 
def task_detail(request, task_id):
    if request.method == 'GET':
        task=get_object_or_404(Task,pk=task_id, user=request.user)
        form= TaskForm(instance=task)
        return render(request, 'task_detail.html',{'task':task, 'form':form})
    else:
        try:
            task=get_object_or_404(Task,pk=task_id, user=request.user)
            form=TaskForm(request.POST ,instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html',{'task':task, 'form':form, 'error': "Error Updating task"})

@login_required
#tarea completada 
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted=timezone.now()
        task.save()
    return redirect('tasks')

@login_required
#eliminar tarea
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
    return redirect('tasks')

@login_required
#salir de usuario lagout
def signout(request):
    logout(request)
    return redirect('home')

#ingresar como usuario con cuenta ya registrada
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user=authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error':'Username or Password Is incorrect'})
        else:
            login(request,user)
            return redirect('tasks')            


