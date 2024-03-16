from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm, CSVUploadForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post, DataTable, DataRow
from django.contrib import messages
import pandas as pd


@login_required(login_url="/login")
def home(request):
    posts = Post.objects.all()

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
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, "main/create_post.html", {"form": form})


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(request, "registration/sign_up.html", {"form": form})


# below will be the new logic for avionics data


def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_csv(request.FILES["csv_file"])

            except Exception as e:
                print(f"Erorr: {e}")
                print()
                messages.error(request, f"Error uploading CSV file: {e}")
                return render(request, "main/upload_csv.html", {"form": form})

            data_table = DataTable.objects.create(
                description=request.POST.get("description")
            )
            # Process and store the CSV data
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

            return render(
                request,
                "main/upload_csv.html",
                {"form": form, "data_table": data_table},
            )

    else:
        form = CSVUploadForm()

    return render(request, "main/upload_csv.html", {"form": form})
