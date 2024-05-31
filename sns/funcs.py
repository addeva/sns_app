from .models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def get_user_by_token(request, token, fail_msg, fail_url, success_msg, success_url):
    try:
        user = User.objects.get(token=token)
    except User.DoesNotExist:
        messages.error(request, fail_msg)
        return HttpResponseRedirect(reverse(fail_url))
    request.session["user_id"] = user.id
    messages.success(request, success_msg)
    return HttpResponseRedirect(reverse(success_url))