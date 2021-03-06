from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from todo.models import Task
from todo.utils import toggle_task_completed


@login_required
def toggle_done(request, task_id: int) -> HttpResponse:
    """Toggle the completed status of a task from done to undone, or vice versa.
    Redirect to the list from which the task came.
    """

    task = get_object_or_404(Task, pk=task_id)

    # Permissions
    if not (
        (request.user.is_superuser)
        or (task.created_by == request.user)
        or (task.assigned_to == request.user)
        or (task.task_list.group in request.user.groups.all())
    ):
        raise PermissionDenied

    toggle_task_completed(task.id)
    messages.success(request, "Task status changed for '{}'".format(task.title))

    return redirect(
        reverse(
            "todo:list_detail",
            kwargs={"list_id": task.task_list.id, "list_slug": task.task_list.slug},
        )
    )
