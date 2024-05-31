import os
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from .tokens import TokenGenerator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import User, Post
from django.core.paginator import Paginator
from .funcs import get_user_by_token

# forms
from .forms import SignupForm
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, AuthenticationForm


# info & pre-settings
load_dotenv()
site = os.getenv("site")
app = "SNS"
appmail = os.getenv("EMAIL_HOST_USER")
f_appmail = f"{app} <{appmail}>"


def index(request):
    if request.method == "POST":
        user = request.user
        content = request.POST["content"]
        new_post = Post(user=user, content=content)
        new_post.save()
    posts = Post.objects.all().order_by("-id")
    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)
    return render(request, "index.html", {"page_obj": page_obj})


def signup(request):
    match request.method:
        case "GET":
            form = SignupForm()
            return render(request, "signup.html", {"form": form})
        case "POST":
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                token_generator = TokenGenerator()
                token = token_generator.make_token(user)
                user.token = token
                user.save()
                link = site + reverse("verify_email", kwargs={"token": token})
                subject = f"Email Verification - {app}"
                body = render_to_string("verify_email.html", {"username": user.username, "app": app, "link": link})
                email = EmailMessage(subject, body, f_appmail, [user.email])
                email.content_subtype = "html"
                email.send()
                messages.success(request, f"Welcome {user.username}. Please check your email for verification email.")
                return HttpResponseRedirect(reverse("signup"))
            else:
                messages.error(request, "Invalid username or email.")
                return render(request, "signup.html", {"form": form})


def verify_email(request, token):
    # fail: redirect to "signup"
    # success: redirect to "set_password"
    return get_user_by_token(request, token, "Invalid or expired link.", "signup", "Email verified. Now you can set your password.", "set_password")


def reset_password(request, token):
    # fail: redirect to "get_reset_password_email"
    # success: redirect to "set_password"
    return get_user_by_token(request, token, "Invalid or expired link.", "get_reset_password_email", "Now you can reset your password.", "set_password")


def set_password(request):
    match request.method:
        case "GET":
            user_id = request.session.get("user_id")
            if user_id:
                user = User.objects.get(id=user_id)
                form = SetPasswordForm(user)
                return render(request, "set_password.html", {"form": form})
            else:
                messages.error(request, "Invalid or expired link.")
                return HttpResponseRedirect(reverse("signup"))
        case "POST":
            user_id = request.session.get("user_id")
            user = User.objects.get(id=user_id)
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                token_generator = TokenGenerator()
                # assign new token to user so that the previous link gets invalid
                user.token = token_generator.make_token(user)
                user.save()
                return HttpResponseRedirect(reverse("login"))
            else:
                messages.error(request, "Error setting password.")
                return render(request, "set_password.html", {"form": form})


def get_reset_password_email(request):
    match request.method:
        case "GET":
            form = PasswordResetForm()
            return render(request, "get_reset_password_email.html", {"form": form})
        case "POST":
            form = PasswordResetForm(data=request.POST)
            if form.is_valid():
                user = User.objects.get(email=form.cleaned_data["email"])
                link = site + reverse("reset_password", kwargs={"token": user.token})
                subject = f"Reset Password - {app}"
                body = render_to_string("reset_password_email.html", {"username": user.username, "app": app, "link": link})
                email = EmailMessage(subject, body, f_appmail, [user.email])
                email.content_subtype = "html"
                email.send()
                messages.success(request, "Please check your email for resetting password.")
                return render(request, "get_reset_password_email.html", {"form": form})
            else:
                messages.error(request, "Error requiring sending email ...")
                return render(request, "get_reset_password_email.html", {"form": form})


def login_view(request):
    match request.method:
        case "GET":
            form = AuthenticationForm(request)
            return render(request, "login.html", {"form": form})
        case "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    if user != request.user:
        not_owner = True
    else:
        not_owner = False
    if request.user not in user.followers.all():
        not_following = True
    else:
        not_following = False

    posts = Post.objects.filter(user=user).order_by("-id")
    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    return render(
        request,
        "profile.html",
        {
            "person": user,
            "not_owner": not_owner,
            "not_following": not_following,
            "profile": profile,
            "page_obj": page_obj,
        },
    )


def follow(request, user_id):
    user = User.objects.get(id=user_id)
    not_owner = True

    # add the request user as a follower
    user.followers.add(request.user)

    # add the user to the request user's following
    request.user.followings.add(user)
    not_following = False

    posts = Post.objects.filter(user=user).order_by("-id")
    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    return render(
        request,
        "profile.html",
        {
            "person": user,
            "not_owner": not_owner,
            "not_following": not_following,
            "page_obj": page_obj,
        },
    )


def unfollow(request, user_id):
    user = User.objects.get(id=user_id)
    not_owner = True

    # add the request user as a follower
    user.followers.remove(request.user)

    # add the user to the request user's following
    request.user.followings.remove(user)
    not_following = True

    posts = Post.objects.filter(user=user).order_by("-id")
    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    return render(
        request,
        "profile.html",
        {
            "person": user,
            "not_owner": not_owner,
            "not_following": not_following,
            "page_obj": page_obj,
        },
    )


def following(request):
    user = request.user
    if user.followings.all().count() == 0:
        page_obj = None
    else:
        posts = Post.objects.filter(user__in=user.followings.all()).order_by("-id")
        p = Paginator(posts, 10)
        page_number = request.GET.get("page")
        page_obj = p.get_page(page_number)
    return render(
        request,
        "following.html",
        {"user": user, "page_obj": page_obj},
    )


def toggle_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.user not in post.likers.all():
        post.likers.add(request.user)
        liked = True
    else:
        post.likers.remove(request.user)
        liked = False
    return JsonResponse({"liked": liked, "like_count": post.likers.count()})


def edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    post.content = request.POST["content"]
    post.save()
    next_url = request.POST.get('next', reverse("index"))
    return HttpResponseRedirect(next_url)