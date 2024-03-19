from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Post, DataTable, DataRow
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
import pandas as pd
import json


@login_required(login_url="/login")
def home(request):
    posts = Post.objects.all().order_by("-created_at")

    if request.method == "POST":
        post_id = request.POST.get("post-id")
        user_id = request.POST.get("user-id")

        if post_id:
            post = Post.objects.filter(id=post_id).first()
            if post and (
                post.author == request.user or request.user.has_perm("main.delete_post")
            ):
                post.delete()
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    group = Group.objects.get(name="default")
                    group.user_set.remove(user)
                except:
                    pass

                try:
                    group = Group.objects.get(name="mod")
                    group.user_set.remove(user)
                except:
                    pass

    return render(request, "main/home.html", {"posts": posts})


@login_required(login_url="/login")
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == "POST":
        print("hit post")
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            print("hit")

            try:
                df = pd.read_csv(request.FILES["csv_file"])

            except Exception as e:
                print(f"Erorr: {e}")
                print()
                messages.error(request, f"Error uploading CSV file: {e}")
                return render(request, "main/create-post", {"form": form})

            data_table = DataTable.objects.create(post=post)

            for index, row in df.iterrows():
                DataRow.objects.create(
                    data_table=data_table,
                    global_time_ns=int(row["Global Time (ns from Epoch)"]),
                    local_time_ms=float(row["Local Time (ms from test)"]),
                    upstream_pressure_psia=float(
                        row["Upsteam Pressure (psia)"]
                    ),  # Check for typos in your CSV headers
                    downstream_pressure_psia=float(row["Downstream Pressure (psia)"]),
                    mass_flow_rate_kgs=float(row["Mass Flow Rate (kg/s)"]),
                    tank_volume_percent=float(row["Tank Volume (%)"]),
                )

            return redirect("data_table", data_table.id)

        else:
            print(form.errors)

    else:
        form = PostForm()

    return render(request, "main/create_post.html", {"form": form})


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            group, created = Group.objects.get_or_create(name="default")

            if created:
                content_type = ContentType.objects.get_for_model(Post)

                add_post_permission = Permission.objects.get(
                    content_type=content_type, codename="add_post"
                )
                view_post_permission = Permission.objects.get(
                    content_type=content_type, codename="view_post"
                )
                group.permissions.add(add_post_permission, view_post_permission)

            user.groups.add(group)
            login(request, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(request, "registration/sign_up.html", {"form": form})


# below will be the new logic for avionics data


@login_required(login_url="/login")
def data_table(request, id):
    data_table = DataTable.objects.get(id=id)
    data_rows = data_table.datarow_set.order_by("local_time_ms")
    paginator = Paginator(data_rows, 50)  # 100 rows per page
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    return render(
        request,
        "main/data_table.html",
        {"data_table": data_table, "page_obj": page_obj},
    )


@login_required(login_url="/login")
def graphics(request, id):
    data_table = DataTable.objects.get(id=id)

    times = data_table.datarow_set.order_by("local_time_ms").values_list(
        "local_time_ms", flat=True
    )
    up_pressure = data_table.datarow_set.order_by("local_time_ms").values_list(
        "upstream_pressure_psia", flat=True
    )
    down_pressure = data_table.datarow_set.order_by("local_time_ms").values_list(
        "downstream_pressure_psia", flat=True
    )

    datasets = [
        {
            "label": "Upstream Pressure",
            "data": list(up_pressure),
            "borderColor": "rgb(255, 99, 132)",
            "fill": False,
        },
        {
            "label": "Downstream Pressure",
            "data": list(down_pressure),
            "borderColor": "rgb(54, 162, 235)",
            "fill": False,
        },
    ]

    context = {
        "times": json.dumps(list(times), cls=DjangoJSONEncoder),
        "datasets": json.dumps(datasets, cls=DjangoJSONEncoder),
    }

    return render(request, "main/charts.html", context)


@login_required(login_url="/login")
def control_panel(request):

    return render(request, "main/control_panel.html")
