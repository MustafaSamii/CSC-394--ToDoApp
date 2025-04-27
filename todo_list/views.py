from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.utils import timezone
from .models import ToDo, Team
from .forms import ToDoForm, CustomUserCreationForm, TeamForm
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.utils.safestring import mark_safe
from django.http import JsonResponse

def landing(request):
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    todos = ToDo.objects.filter(user=request.user).order_by(
        Case(
            When(status='Not Started', then=0),
            When(status='In Progress', then=1),
            When(status='Paused', then=2),
            When(status='Completed', then=3),
            default=4,
            output_field=IntegerField(),
        )
    )
    f_categ = request.GET.get('category') # Filter for category
    f_team = request.GET.get('team')    # Filter for team
    
    all_teams = Team.objects.all().distinct()
    dis_categ = set()
    for each in todos:
        dis_categ.add(each.category)
    
    categs = list(dis_categ)
    
    if f_categ: # Apply category filter if it exist
        if f_categ == 'None':
            todos = todos.filter(category__exact=None)
        else:
            todos = todos.filter(category = f_categ)
            all_teams = Team.objects.filter( todo__user = request.user, todo__category = f_categ).distinct()
    
    if f_team: # Apply team filter if it exist
        todos = todos.filter(team__id = f_team)
        
    for todo in todos:
        if todo.status == 'In Progress' and todo.start_time:
            accumulated = todo.elapsed_time.total_seconds() if todo.elapsed_time else 0
            todo.initial_elapsed = accumulated + (timezone.now() - todo.start_time).total_seconds()
        else:
            todo.initial_elapsed = todo.elapsed_time.total_seconds() if todo.elapsed_time else 0

    context = {
        'todos': todos,
        'categories': categs,
        'pick_category': f_categ,
        'pick_team': f_team,
        'teams': all_teams, 
    }
    return render(request, 'dashboard.html', context)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Registration successful. Please log in.")
                return redirect('login')
            except IntegrityError:
                form.add_error(None, "A user with that email already exists.")
        else:
            messages.error(request, "Failed to register successfully. Please try again.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def custom_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def create_todo(request):
    is_create = False
    if request.method == "POST":
        form = ToDoForm(request.POST, user=request.user)
        if 'create' in request.POST:
            is_create = True
            if form.is_valid():
                todo = form.save(commit=False)
                todo.user = request.user
                if not todo.assigned_to:
                    todo.assigned_to = request.user
                if todo.status == 'In Progress':
                    todo.start_time = timezone.now()
                    todo.elapsed_time = timezone.timedelta(0)
                todo.save()
                messages.success(request, "ToDo created successfully!")
                return redirect('dashboard')
        return render(request, 'create_todo.html', {
            'form': form, 'is_create': is_create
        })
    form = ToDoForm(user=request.user)
    return render(request, 'create_todo.html', {
        'form': form, 'is_create': False
    })

@login_required
def get_team_members(request):
    """
    AJAX endpoint: given ?team_id=, return JSON list of {id,email}.
    """
    team_id = request.GET.get('team_id')
    members = []
    if team_id:
        try:
            team = Team.objects.get(pk=team_id)
            members = [
                {'id': u.id, 'email': u.email}
                for u in team.members.all()
            ]
        except Team.DoesNotExist:
            members = []
    return JsonResponse({'members': members})


@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    todo.delete()
    messages.success(request, "ToDo deleted successfully.")
    return redirect('dashboard')

@login_required
def update_todo(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    previous_status = todo.status  # Save previous status
    if request.method == 'POST':
        form = ToDoForm(request.POST, instance=todo, user=request.user)
        if form.is_valid():
            updated_todo = form.save(commit=False)
            # If changing to "In Progress" and wasn't already, set start_time
            if updated_todo.status == 'In Progress' and (previous_status != 'In Progress' or not updated_todo.start_time):
                updated_todo.start_time = timezone.now()
            elif updated_todo.status != 'In Progress':
                updated_todo.start_time = None
            updated_todo.save()
            messages.success(request, "ToDo updated successfully.")
            return redirect('dashboard')
    else:
        form = ToDoForm(instance=todo, user=request.user)
    return render(request, 'update_todo.html', {'form': form})

@login_required
def update_todo_status(request, todo_id, action):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    now = timezone.now()
    if action == 'start':
        if todo.status in ['Not Started', 'Completed']:
            todo.status = 'In Progress'
            todo.start_time = now
            todo.elapsed_time = timezone.timedelta(0)
            messages.success(request, "ToDo started.")
        else:
            messages.error(request, "Cannot start a ToDo in its current state.")
    elif action == 'pause':
        if todo.status == 'In Progress' and todo.start_time:
            delta = now - todo.start_time
            todo.elapsed_time = (todo.elapsed_time or timezone.timedelta(0)) + delta
            todo.status = 'Paused'
            todo.start_time = None
            messages.success(request, "ToDo paused.")
        else:
            messages.error(request, "Only active ToDos can be paused.")
    elif action == 'resume':
        if todo.status == 'Paused':
            todo.status = 'In Progress'
            todo.start_time = now
            messages.success(request, "ToDo resumed.")
        else:
            messages.error(request, "Only paused ToDos can be resumed.")
    elif action == 'stop':
        if todo.status == 'In Progress' and todo.start_time:
            delta = now - todo.start_time
            todo.elapsed_time = (todo.elapsed_time or timezone.timedelta(0)) + delta
            todo.status = 'Completed'
            todo.start_time = None
            messages.success(request, "ToDo stopped.")
        else:
            messages.error(request, "Only active ToDos can be stopped.")
    else:
        messages.error(request, "Invalid action.")
    todo.save()
    return redirect('dashboard')

# --- Teams Views ---

@login_required
def teams_list(request):
    teams = Team.objects.all()
    return render(request, 'teams_list.html', {'teams': teams})

@login_required
def team_details(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    from django.contrib.auth.models import User
    if request.method == "POST":
        if 'update_team' in request.POST:
            form = TeamForm(request.POST, instance=team)
            if form.is_valid():
                form.save()
                messages.success(request, "Team details updated successfully!")
            else:
                messages.error(request, "Please correct the errors below.")
        elif 'remove_member' in request.POST:
            member_id = request.POST.get("remove_member")
            try:
                member = User.objects.get(id=member_id)
                team.members.remove(member)
                messages.success(request, "Member removed successfully!")

                if not team.members.exists():
                    name_team = team.name
                    team.delete()
                    messages.success(request, mark_safe(f"No members left in <strong>{name_team}</strong>. <strong>{name_team}</strong> deleted successfully."))
                    return redirect('teams_list')
                
            except User.DoesNotExist:
                messages.error(request, "Member does not exist.")
        else:
            new_member_email = request.POST.get("new_member", "").strip().lower()
            if new_member_email:
                try:
                    user_to_add = User.objects.get(email=new_member_email)
                    if user_to_add in team.members.all():
                        messages.error(request, "This member is already added to the team.")
                    else:
                        team.members.add(user_to_add)
                        messages.success(request, "Member added successfully!")
                except User.DoesNotExist:
                    messages.error(request, "No user with that email exists.")
            else:
                messages.error(request, "Please enter a valid email address.")
        return redirect('team_details', team_id=team.id)
    form = TeamForm(instance=team)
    return render(request, 'team_details.html', {'team': team, 'form': form})

def create_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            # Automatically add the creator as a team member
            team.owner = request.user
            team.save()
            team.members.add(request.user)
            messages.success(request, "Team created successfully!")
            return redirect('team_details', team_id=team.id)
        else:
            return render(request, 'create_team.html', {'form':form})
    else:
        form = TeamForm()
    return render(request, 'create_team.html', {'form': form})



def about(request):
    return render(request, 'about.html')

@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    team.delete()
    messages.success(request, "Team deleted successfully.")
    return redirect('teams_list')


@login_required
def toggle_status(request, todo_id):
    todo = get_object_or_404(ToDo, id=todo_id, user=request.user)
    now = timezone.now()
    # Toggle between "In Progress" and "Completed"
    if todo.status == 'In Progress' and todo.start_time:
        # Calculate elapsed time
        delta = now - todo.start_time
        todo.elapsed_time = (todo.elapsed_time or timezone.timedelta(0)) + delta
        todo.status = 'Completed'
        todo.start_time = None
        messages.success(request, "ToDo marked as completed.")
    else:
        # Otherwise, set to In Progress
        todo.status = 'In Progress'
        todo.start_time = now
        messages.success(request, "ToDo marked as in progress.")
    todo.save()
    return redirect('dashboard')

@login_required
def todos_list(request):
    # no longer needed, since /todos now goes to dashboard()
    return dashboard(request)
    
@login_required
def get_categ_teams(request):
    get_categ = request.GET.get('category')
    filter_team = Team.objects.filter(todo__category = get_categ, todo__user = request.user).distinct().values('id', 'name')
    
    return JsonResponse({'teams': list(filter_team)})

