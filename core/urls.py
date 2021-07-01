from django.urls import path
from . import views

app_name = "core" 

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("update/", views.update_profile, name="update"),
    path("update_profile_success/", views.update_profile_success, name="update_profile_success"),
    # path("upload/", views.image_upload_view, name="upload")
    path("upload/", views.post, name="upload"),
    path("preprocess/", views.preprocess_image, name="preprocess"),
    path("crop/", views.main_view, name="crop"),
    path("trim/", views.trim_image, name="trim"),
    path("frame/", views.frame_image, name="frame"),
    path("convert/", views.convert_image_to_png, name="convert"),
    path("removebackground/", views.remove_background_image, name="removebackground"),
]
