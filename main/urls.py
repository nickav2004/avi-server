from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("sign-up", views.sign_up, name="sign_up"),
    path("create-post", views.create_post, name="create_up"),
    path("data-table/<int:id>", views.data_table, name="data_table"),
    path("graphics/<int:id>", views.graphics, name="graphics"),
    path("control-center", views.control_panel, name="control_panel"),
]
