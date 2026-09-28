"""
Custom decorators for teacher authentication.
"""

from functools import wraps

from django.shortcuts import redirect


def teacher_login_required(view_func):
    """Ensure only authenticated teachers can access protected views."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('teacher_id'):
            return redirect('erp:teacher_login')
        return view_func(request, *args, **kwargs)

    return wrapper
