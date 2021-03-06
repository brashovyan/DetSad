from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.models import Group as Group_user
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Organization, Section, Child, Parent, Garten, Group, Admin_Garten, Admin_Organization
from .forms import RegForm


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    else:
        role = check_role(request)
        if role == 'p':
            parent = Parent.objects.get(person = request.user)
            childs = Child.objects.filter(parents = parent)
            return render(request, 'mainapp/parent_profile.html', {'person': request.user, 'childs':childs })

        elif role == 'o':
            admin_organization = Admin_Organization.objects.get(person=request.user)
            return render(request, 'mainapp/organization_profile.html', {'person': request.user})

        elif role == 'g':
            admin_garten = Admin_Garten.objects.get(person=request.user)
            return render(request, 'mainapp/garten_profile.html', {'person': request.user, 'admin_garten':admin_garten})

        else:
            return HttpResponseRedirect('/login')


def login1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            role = check_role(request)
            if role == 'o' or role == 'g':
                user2 = User.objects.get(id=request.user.id)
                if user2.is_staff == False:
                    user2.is_staff = True
                    user2.save()

            return HttpResponseRedirect("/")
        else:
            error = "Неверный логин или пароль! Проверьте раскладку языка. Также напоминаем, что буквы верхнего и нижнего регистра (строчные и заглавные) отличаются между собой."
            return render(request, 'mainapp/login.html', {'error': error})

    else:
        if request.user.is_authenticated:
            logout(request)
        return render(request, 'mainapp/login.html')


def register(request):
    if request.method == "POST":
        form = RegForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                try:
                    user = User.objects.create_user(username, email, password1)
                except:
                    error = "Данный логин уже занят. Попробуйте другой."
                    form = RegForm()
                    return render(request, 'mainapp/register.html', {'form': form, 'error': error})
                if request.user.is_authenticated:
                    logout(request)
                login(request, user)

                user2 = User.objects.get(username=request.user.username)
                group = Group_user.objects.get(name='Parent')
                user2.groups.add(group)
                Parent.objects.create(person=request.user)
                return HttpResponseRedirect("/")
            else:
                error = "Пароли не совпадают!"
                form = RegForm()
                return render(request, 'mainapp/register.html', {'form': form, 'error':error})

        else:
            error = "Вы ввели некорректные данные! Повторите попытку, заполнив все поля по подсказкам."
            return render(request, 'mainapp/register.html', {'form': form, 'error': error})
    else:
        form = RegForm()
        return render(request, 'mainapp/register.html', {'form': form})


def change_profile(request, id):
    user = User.objects.get(id=id)
    if user == request.user:
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            if first_name != '':
                user.first_name = first_name
            if last_name != '':
                user.last_name = last_name
            user.save()

            return HttpResponseRedirect('/')

        else:
            return render(request, 'mainapp/change_profile.html', {'person': user})
    else:
        return HttpResponseRedirect('/')


def logout1(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def child_info(request, id):
    if request.user.is_authenticated:
        role = check_role(request)
        if role == 'p':
            parent = Parent.objects.get(person=request.user)
            childs = Child.objects.filter(parents=parent)
            child = Child.objects.get(id=id)
            sections = child.sections.all()
            s = float(0)
            section_list = []
            for section in sections:
                section_list.append([section, section.load])
                s += section.load
            if child in childs:
                return render(request, 'mainapp/child_info.html', {'child':child, 'load_all':s, 'role':role, "section_list": section_list})
            else:
                return HttpResponseRedirect('/')

        elif role == 'o' or role == 'g':
            child = Child.objects.get(id=id)
            sections = child.sections.all()
            s = float(0)
            section_list = []
            for section in sections:
                section_list.append([section, section.load])
                s += section.load
            return render(request, 'mainapp/child_info.html', {'child': child, 'load_all': s, 'role':role, "section_list": section_list})

        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


def add_section_child(request):
    if request.user.is_authenticated:
        if check_role(request) == 'p':
            if request.method == 'POST':
                try:
                    c = request.POST['selected_child']
                    child = Child.objects.get(id=c)
                    s = request.POST['selected_section']
                    section = Section.objects.get(id=s)
                    child.sections.add(section)
                    return HttpResponseRedirect('/')

                except:
                    parent = Parent.objects.get(person=request.user)
                    childs = Child.objects.filter(parents=parent)
                    sections = Section.objects.all()
                    error = "Произошла ошибка!"
                    return render(request, 'mainapp/add_section_child.html', {'childs': childs, 'sections': sections, 'error':error})

            else:
                parent = Parent.objects.get(person=request.user)
                childs = Child.objects.filter(parents=parent)
                sections = Section.objects.all()
                return render(request, 'mainapp/add_section_child.html', {'childs':childs, 'sections':sections})
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/login')


def sections(request):
    if request.user.is_authenticated:
        sections = Section.objects.all()
        return render(request, 'mainapp/sections.html', {'sections': sections})
    else:
        return HttpResponseRedirect('/login')


def load_childs(request):
    if request.user.is_authenticated:
        if check_role(request) == 'g':
            admin_garten = Admin_Garten.objects.get(person=request.user)
            garten = admin_garten.garten
            groups = Group.objects.filter(garten = garten)
            childs = []
            ld = {}


            for group in groups:
                for child in Child.objects.filter(group=group):
                    s = 0
                    for section in child.sections.all():
                        s += section.load
                    childs.append(child)
                    ld[child.id]=s

            role = check_role(request)
            return render(request, 'mainapp/load_childs.html', {'garten':garten, 'ld':ld, 'role':role, 'groups':groups, 'childs':childs})

        elif check_role(request) == 'o':
            gartens = Garten.objects.all()
            childs = []


            for garten in gartens:
                for group in Group.objects.filter(garten=garten):
                    for child in Child.objects.filter(group=group):
                        childs.append(child)

            role = check_role(request)
            return render(request, 'mainapp/load_childs.html', {'gartens': gartens, 'childs':childs, 'role': role})
        else:

            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/login')


def garten_search(request):
    if request.user.is_authenticated:
        if check_role(request) == 'g' or check_role(request) == 'o':
            if request.method == 'POST':
                ser = request.POST.get('search')
                result = []

                gartens = Garten.objects.all()
                for garten in gartens:
                    if ser.title() in str(garten.title).title() or ser in str(garten.number).title():
                        if garten not in result:
                            result.append(garten)

                role = check_role(request)
                return render(request, 'mainapp/garten_search.html', {'result':result, 'role':role})
            else:
                role = check_role(request)
                return render(request, 'mainapp/garten_search.html', {'role':role})
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/login')


def garten(request, id):
    if request.user.is_authenticated:
        if check_role(request) == 'g' or check_role(request) == 'o':
            garten = Garten.objects.get(id=id)
            childs = []
            for group in Group.objects.filter(garten=garten):
                for child in Child.objects.filter(group=group):
                    childs.append(child)
            role = check_role(request)
            return render(request, 'mainapp/garten.html', {'garten':garten, 'childs':childs, 'role':role})
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')


def add_parent(request):
    if request.user.is_authenticated:
        if check_role(request) == 'g':
            if request.method == 'POST':
                try:
                    c = request.POST['selected_child']
                    child = Child.objects.get(id=c)
                    p = request.POST['selected_parent']
                    parent = Parent.objects.get(id=p)
                    child.parents.add(parent)
                    return HttpResponseRedirect('/')
                except:
                    childs = Child.objects.all()
                    parents = Parent.objects.all()
                    error = 'Произошла ошибка'
                    return render(request, 'mainapp/add_parent.html', {'childs': childs, 'parents': parents, 'error':error})

            else:
                childs = Child.objects.all()
                parents = Parent.objects.all()
                return render(request, 'mainapp/add_parent.html', {'childs':childs, 'parents': parents})
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')


def add_section(request):
    if request.user.is_authenticated:
        if check_role(request) == 'o':
            if request.method == 'POST':
                try:
                    o = request.POST['selected_organization']
                    organization = Organization.objects.get(id=o)
                    title = request.POST.get('title')
                    coach = request.POST.get('coach')
                    load = request.POST.get('load')
                    load = load.replace('%', '')
                    load = float(load)
                    Section.objects.create(title=title, organization=organization, coach=coach, load=load)
                    return HttpResponseRedirect('/')
                except:
                    organizations = Organization.objects.all()
                    error = 'Произошла ошибка'
                    return render(request, 'mainapp/add_section.html', {'organizations': organizations, 'error':error})

            else:
                organizations = Organization.objects.all()
                return render(request, 'mainapp/add_section.html', {'organizations': organizations})
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')


def add_organization(request):
    if request.user.is_authenticated:
        if check_role(request) == 'o':
            if request.method == 'POST':
                try:
                    title = request.POST.get('title')
                    Organization.objects.create(title=title)
                    return HttpResponseRedirect('/add_section')
                except:
                    error = 'Произошла ошибка'
                    return render(request, 'mainapp/add_organization.html', {'error':error})

            else:
                return render(request, 'mainapp/add_organization.html')
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/login')


def add_garten(request):
    if request.user.is_authenticated:
        if check_role(request) == 'o':
            if request.method == 'POST':
                try:
                    title = request.POST.get('title')
                    number = request.POST.get('number')
                    number = int(number)
                    director = request.POST.get('director')
                    Garten.objects.create(title=title, director=director, number=number)
                    return HttpResponseRedirect('/')
                except:
                    error = 'Произошла ошибка'
                    return render(request, 'mainapp/add_garten.html', {'error':error})

            else:
                return render(request, 'mainapp/add_garten.html')
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')


def check_role(request):
    try:
        if User.objects.filter(pk=request.user.id, groups__name='Parent').exists():
            role = 'p'
        elif User.objects.filter(pk=request.user.id, groups__name='Admin_organization').exists():
            role = 'o'
        elif User.objects.filter(pk=request.user.id, groups__name='Admin_garten').exists():
            role = 'g'
        else:
            role = 'error'
    except:
        role = 'error'

    return role


def add_child(request):
    if request.user.is_authenticated:
        if check_role(request) == 'g':
            if request.method == 'POST':
                try:
                    Firstname = request.POST.get('Firstname')
                    Lastname = request.POST.get('Lastname')
                    Secondname = request.POST.get('Secondname')
                    date = request.POST.get('date')
                    id = request.POST['selected_group']
                    group = Group.objects.get(id=id)

                    Child.objects.create(Firstname=Firstname, Lastname=Lastname, Secondname=Secondname, date=date, group=group)

                    return HttpResponseRedirect('/')
                except:
                    gartens = Garten.objects.all()
                    error = 'Произошла ошибка'
                    return render(request, 'mainapp/add_child.html', {'error': error, 'gartens':gartens})

            else:
                admin_garten = Admin_Garten.objects.get(person=request.user)
                garten = admin_garten.garten
                groups = Group.objects.filter(garten=garten)

                return render(request, 'mainapp/add_child.html', {'groups':groups})
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')


def group_search(request):
    if request.user.is_authenticated:
        if check_role(request) == 'g':
            if request.method == 'POST':
                ser = request.POST.get('search')
                result_groups = []
                result_childs = []

                admin_garten = Admin_Garten.objects.get(person=request.user)
                garten = admin_garten.garten
                groups = Group.objects.filter(garten=garten)

                for group in groups:
                    if ser.title() in str(group.title).title():
                        if group not in result_groups:
                            result_groups.append(group)

                for group in groups:
                    for child in Child.objects.filter(group = group):
                        if ser.title() in child.Lastname.title() or ser.title() in child.Firstname.title() or ser.title() in child.Secondname.title():
                            if child not in result_childs:
                                result_childs.append(child)

                role = check_role(request)
                return render(request, 'mainapp/group_search.html', {'result_groups': result_groups, 'role': role, 'result_childs':result_childs})
            else:
                role = check_role(request)
                return render(request, 'mainapp/group_search.html', {'role': role})
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/login')


def group_info(request, id):
    if request.user.is_authenticated:
        if check_role(request) == 'g':
            group = Group.objects.get(id=id)
            childs = Child.objects.filter(group=group)
            role = check_role(request)
            return render(request, 'mainapp/group_info.html', {'group':group, 'childs':childs, 'role':role})
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/login')







