from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.http import require_POST
from .models import Students, School, Role
from .forms import StudentForm
from django.contrib import messages
User = get_user_model()


from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Role, School

def register_students(request):
    schools = School.objects.all()
    valid_roles = ["admin", "principal", "teacher"]

    if request.method == "POST":
        username = request.POST.get("user", "").strip()
        password = request.POST.get("password", "").strip()
        email = request.POST.get("email", "").strip()
        role_name = request.POST.get("role", "").strip().lower()
        school_id = request.POST.get("school")

        if not username:
            messages.error(request, "Username is required.")
            return redirect("register")

        if not password:
            messages.error(request, "Password is required.")
            return redirect("register")

        if not email:
            messages.error(request, "Email is required.")
            return redirect("register")

        if role_name not in valid_roles:
            messages.error(request, "Invalid role. Allowed roles: admin, principal, teacher.")
            return redirect("register")

        if role_name == "admin":
            if Role.objects.filter(role="admin").exists():
                messages.error(request, "Admin already exists. Only one admin allowed.")
                return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)

        school_obj = None
        if school_id:
            school_obj = School.objects.filter(id=school_id).first()

        Role.objects.create(user=user, role=role_name, school=school_obj)

        messages.success(request, "Registered successfully!")
        return redirect("/login")

    return render(request, "register.html", {"schools": schools})


def login_student(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("students")
        return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")


@require_POST
def logout_student(request):
    logout(request)
    return render(request, "base.html")


def home_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        age = request.POST.get("age")
        city = request.POST.get("city")
        Students.objects.create(name=name, age=age, city=city, add_uid=request.user if request.user.is_authenticated else None)
        return redirect("/")
    data = Students.objects.all()
    return render(request, "base.html", {"Students": data})


def add_student(request):
    role = get_role(request.user)
    if role not in ["admin", "principal", "teacher"]:
        return HttpResponseForbidden("You cannot add students.")

    if request.method == "POST":
        name = request.POST.get("name").strip()
        age = request.POST.get("age")
        city = request.POST.get("city").strip()
        school_id = request.POST.get("school")

        # Get the school object
        school_obj = None
        if school_id:
            school_obj = School.objects.filter(id=school_id).first()
        else:
            # if no school selected, use logged user's school (for principal/teacher)
            role_obj = Role.objects.filter(user=request.user).first()
            if role_obj and role_obj.school:
                school_obj = role_obj.school

        # Create the student
        Students.objects.create(
            name=name,
            age=age,
            city=city,
            school=school_obj,
            user=request.user,       # creator
            add_uid=request.user     # added by
        )

        messages.success(request, "Student added successfully!")
        return redirect("students")

    # GET request → show form
    schools = School.objects.all()
    return render(request, "add_student.html", {"schools": schools})





def get_students(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        logged_role = Role.objects.get(user=request.user)
    except Role.DoesNotExist:
        logged_role = None

    # ADMIN → can see all students
    if logged_role and logged_role.role == "admin":
        students = Students.objects.select_related("school", "user", "add_uid").all()

    # PRINCIPAL → can see students of their own school
    elif logged_role and logged_role.role == "principal":
        students = Students.objects.select_related("school", "user", "add_uid").filter(
            school=logged_role.school
        )

    # TEACHER → can see only students they added
    elif logged_role and logged_role.role == "teacher":
        students = Students.objects.select_related("school", "user", "add_uid").filter(
            add_uid=request.user
        )

    else:
        students = Students.objects.none()

    return render(request, "students.html", {"students": students})




def get_user(request):
    users = User.objects.filter(is_active=True).select_related("role_profile")
    return render(request, "user.html", {"users": users})


def edit_students(request, id):
    student = get_object_or_404(Students, id=id)
    form = StudentForm(instance=student)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("students")
    return render(request, "edit.html", {"form": form})


def delete_students(request, id):
    student = get_object_or_404(Students, id=id)
    my_role = get_role(request.user)

    if my_role == "admin":
        student.delete()
        return redirect("students")

    if my_role == "principal":
        if student.school and Role.objects.filter(user=request.user, school=student.school).exists():
            student.delete()
            return redirect("students")
        return HttpResponseForbidden("You cannot delete this student.")

    if my_role == "teacher":
        if student.user == request.user:
            student.delete()
            return redirect("students")
        return HttpResponseForbidden("You cannot delete this student.")

    return HttpResponseForbidden("You do not have permission.")



def delete_user(request, id):
    logged_user = request.user
    target_user = get_object_or_404(User, id=id)
    logged_role = None
    target_role = None
    try:
        logged_role = Role.objects.get(user=logged_user).role
    except Role.DoesNotExist:
        logged_role = None
    try:
        target_role = Role.objects.get(user=target_user).role
    except Role.DoesNotExist:
        target_role = None
    if logged_user == target_user:
        return HttpResponseForbidden("You cannot deactivate yourself.")
    if logged_role == "admin":
        target_user.is_active = False
        target_user.save()
        users = User.objects.filter(is_active=True).select_related("role_profile")
        return render(request, "user.html", {"users": users})
    if logged_role == "principle":
        if target_role in ["teacher"]:
            target_user.is_active = False
            target_user.save()
            users = User.objects.filter(is_active=True).select_related("role_profile")
            return render(request, "user.html", {"users": users})
    return redirect("user")


def add_school(request):
    if request.method == "POST":
        sch_name = request.POST.get("sch_name")
        address = request.POST.get("address")
        principal_id = request.POST.get("principal")
        principal_obj = None
        if principal_id:
            try:
                principal_obj = User.objects.get(id=principal_id)
            except User.DoesNotExist:
                principal_obj = None
        else:
            if request.user.is_authenticated:
                principal_obj = request.user
        School.objects.create(sch_name=sch_name, address=address, principal=principal_obj)
        return redirect("register")
    principals = User.objects.filter(is_active=True)
    return render(request, "add_school.html", {"principals": principals})


def get_school(request):
    schools = School.objects.select_related("principal").prefetch_related("teachers", "students").all()
    return render(request, "school_list.html", {"school": schools})


def get_role(user):
    try:
        return Role.objects.get(user=user).role
    except Role.DoesNotExist:
        return None

