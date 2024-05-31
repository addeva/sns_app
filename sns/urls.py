from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("following", views.following, name="following"),
    path("set_password", views.set_password, name="set_password"),
    path(
        "get_reset_password_email",
        views.get_reset_password_email,
        name="get_reset_password_email",
    ),
    path("reset_password/<str:token>", views.reset_password, name="reset_password"),
    path("verify_email/<str:token>", views.verify_email, name="verify_email"),
    path("toggle_like/<int:post_id>", views.toggle_like, name="toggle_like"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("profile/<int:user_id>/follow", views.follow, name="follow"),
    path("profile/<int:user_id>/unfollow", views.unfollow, name="unfollow"),
]
