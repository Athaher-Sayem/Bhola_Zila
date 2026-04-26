from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task
from .forms import TaskForm, TaskStatusForm


@login_required
def task_list(request):
    user = request.user
    if user.can_post:
        # Admins/2nd admins see all tasks they created + tasks assigned to them
        my_tasks = Task.objects.filter(assigned_to=user).select_related('assigned_by')
        created_tasks = Task.objects.filter(assigned_by=user).select_related('assigned_to')
    else:
        my_tasks = Task.objects.filter(assigned_to=user).select_related('assigned_by')
        created_tasks = Task.objects.none()
    return render(request, 'tasks/list.html', {
        'my_tasks': my_tasks,
        'created_tasks': created_tasks,
    })


@login_required
def task_create(request):
    if not request.user.can_post:
        messages.error(request, 'Only admins can assign tasks.')
        return redirect('tasks:list')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, f'Task assigned to {task.assigned_to.name}.')
            return redirect('tasks:list')
    else:
        form = TaskForm()
    return render(request, 'tasks/form.html', {'form': form})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Only assigned user or creator can view
    if task.assigned_to != request.user and task.assigned_by != request.user and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('tasks:list')
    form = TaskStatusForm(initial={'status': task.status})
    return render(request, 'tasks/detail.html', {'task': task, 'form': form})


@login_required
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.assigned_to != request.user and not request.user.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('tasks:list')
    if request.method == 'POST':
        form = TaskStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            task.status = new_status
            if new_status == 'done' and not task.completed_at:
                task.completed_at = timezone.now()
            elif new_status != 'done':
                task.completed_at = None
            task.save()
            messages.success(request, f'Task status updated to "{new_status}".')
    return redirect('tasks:detail', pk=pk)


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user.is_admin or task.assigned_by == request.user:
        if request.method == 'POST':
            task.delete()
            messages.success(request, 'Task deleted.')
            return redirect('tasks:list')
    else:
        messages.error(request, 'Permission denied.')
    return redirect('tasks:list')