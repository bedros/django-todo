import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from todo.models import Task, TaskList
from todo.utils import staff_only


@staff_only
@login_required
def del_list(request, list_id: int, list_slug: str) -> HttpResponse:
    """Delete an entire list. Only staff members should be allowed to access this view.
    """
    task_list = get_object_or_404(TaskList, id=list_id)

    # Ensure user has permission to delete list. Admins can delete all lists.
    # Get the group this list belongs to, and check whether current user is a member of that group.
    # FIXME: This means any group member can delete lists, which is probably too permissive.
    if task_list.group not in request.user.groups.all() and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        TaskList.objects.get(id=task_list.id).delete()
        messages.success(request, "{list_name} is gone.".format(list_name=task_list.name))
        return redirect("todo:lists")
    else:
        task_count_done = Task.objects.filter(task_list=task_list.id, completed=True).count()
        task_count_undone = Task.objects.filter(task_list=task_list.id, completed=False).count()
        task_count_total = Task.objects.filter(task_list=task_list.id).count()

    context = {
        "task_list": task_list,
        "task_count_done": task_count_done,
        "task_count_undone": task_count_undone,
        "task_count_total": task_count_total,
    }

    return render(request, "todo/del_list.html", context)
