from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget, authenticated_userid #has_permission

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import aliased

from .security import userfinder
from .models import (DBSession, Employee, Department, User, Group, Location, Region,
                     Country, Job, Job_History, ITEMS_PER_PAGE, SummaryQuery)

from .forms import (DepartmentForm, EmployeeForm, LoginForm, UserForm, GroupForm,
                    RegionForm, CountryForm, LocationForm, JobForm)

from paginate import Page

import json
from webob import Request


@view_config(route_name='login', renderer='login.jinja2',
             permission='view')
@forbidden_view_config(renderer='login.jinja2')#For customizing default 404 forbidden template
def login(request):
    came_from = request.referer or request.route_url('home')
    login_url = request.route_url('login')
    if came_from == login_url:
        came_from = '/' # never use the login form itself as came_from

    login = ''

    form = LoginForm(request.POST, came_from, login, csrf_context=request.session)

    message = ''

    if request.method == 'POST' and form.validate():
        login = request.params['login']
        password = request.params['password']
        if userfinder(login, password) == True:
            headers = remember(request, login)
            request.session.flash('User: '+ login + ' logged in!')
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return {'form' : form,
            'message' : message}


@view_config(route_name='logout',
             permission='view')
def logout(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location = loc, headers = headers)



@view_config(route_name='home', renderer='home.jinja2', request_method='GET',
             permission='view')
def home(request):
    return {'project': 'My Ninja',
            'logged_in': authenticated_userid(request)}


@view_config(route_name='department_view', renderer='department_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='department_view:page', renderer='department_r.jinja2', request_method='GET',
             permission='view')
def department_view(request):
    #Sorting custom code
    sort_value = 'hr_departments_department_name'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        departments = DBSession.query(Department, Location, Employee).\
            outerjoin(Location, Department.location_id==Location.location_id).\
            outerjoin(Employee, Department.manager_id==Employee.employee_id).\
            order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)

    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('department_view:page', page=p) + '?sort=' + sort_value
    records = Page(departments, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'departments': records,
            'logged_in': authenticated_userid(request)}



@view_config(route_name='department_add', renderer='department_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def department_add(request):
    form = DepartmentForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        dep = Department(department_name = form.department_name.data,
                         manager = form.manager.data,
                         location = form.location.data)
        DBSession.add(dep)
        request.session.flash('Department Added!')
        return HTTPFound(location=request.route_url('department_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}

@view_config(route_name='department_edit', renderer='department_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def department_edit(request):
    department = DBSession.query(Department).filter(Department.department_id==request.matchdict['dep_id']).first()
    form = DepartmentForm(request.POST, department, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        form.populate_obj(department)
        DBSession.add(department)
        request.session.flash('Department Updated!')
        return HTTPFound(location=request.route_url('department_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='employee_view', renderer='employee_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='employee_view:page', renderer='employee_r.jinja2', request_method='GET',
             permission='view')
def employee_view(request):
    #Sorting custom code
    sort_value = 'hr_employees_first_name'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        employees = DBSession.query(Employee, Department).outerjoin(Department,
                                                               Employee.department_id==Department.department_id).\
            filter(Employee.end_date==None).order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)

    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('employee_view:page', page=p) + '?sort=' + sort_value
    records = Page(employees, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'employees': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='employee_add', renderer='employee_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def employee_add(request):
    form = EmployeeForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        emp = Employee(first_name = form.first_name.data,
                       last_name = form.last_name.data,
                       email = form.email.data,
                       phone_number = form.phone_number.data,
                       salary = form.salary.data,
                       hire_date = form.hire_date.data,
                       end_date = form.end_date.data,
                       job = form.job.data,
                       department = form.department.data,
                       manager = form.manager.data)
        DBSession.add(emp)
        request.session.flash('Employee Added!')
        return HTTPFound(location=request.route_url('employee_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='employee_edit', renderer='employee_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def employee_edit(request):
    try:
        employee = DBSession.query(Employee).filter(Employee.employee_id==request.matchdict['emp_id']).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    if employee is None:
        return HTTPNotFound('Employee not found!')
    form = EmployeeForm(request.POST, employee, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        #Add job history when end_date provided
        if form.end_date.data:
            job_hist = Job_History(employee_id = form.employee_id.data,
                                      start_date = form.hire_date.data,
                                      end_date = form.end_date.data,
                                      job = form.job.data,
                                      department = form.department.data)
            DBSession.add(job_hist)
        #Update Employee
        employee.first_name = form.first_name.data
        employee.last_name = form.last_name.data
        employee.email = form.email.data
        employee.phone_number = form.phone_number.data
        employee.salary = form.salary.data
        employee.hire_date = form.hire_date.data
        employee.job = form.job.data
        employee.department = form.department.data
        employee.manager = form.manager.data
        employee.end_date = form.end_date.data
        DBSession.add(employee)
        request.session.flash('Employee Updated!')
        return HTTPFound(location=request.route_url('employee_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='region_view', renderer='region_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='region_view:page', renderer='region_r.jinja2', request_method='GET',
             permission='view')
def region_view(request):
    #Sorting custom code
    sort_value = 'hr_regions_region_name'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        regions = DBSession.query(Region).order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)

    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('region_view:page', page=p) + '?sort=' + sort_value
    records = Page(regions, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'regions': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='region_add', renderer='region_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def region_add(request):
    form = RegionForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        reg = Region(region_name = form.region_name.data)
        DBSession.add(reg)
        request.session.flash('Region Added!')
        return HTTPFound(location=request.route_url('region_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='region_edit', renderer='region_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def region_edit(request):
    region = DBSession.query(Region).filter(Region.region_id==request.matchdict['reg_id']).first()
    form = RegionForm(request.POST, region, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        form.populate_obj(region)
        DBSession.add(region)
        request.session.flash('Region Updated!')
        return HTTPFound(location=request.route_url('region_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='country_view', renderer='country_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='country_view:page', renderer='country_r.jinja2', request_method='GET',
             permission='view')
def country_view(request):
    #Sorting custom code
    sort_value = 'hr_countries_country_name'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        countries = DBSession.query(Country, Region).outerjoin(Region, Country.region_id==Region.region_id).\
            order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('country_view:page', page=p) + '?sort=' + sort_value
    records = Page(countries, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'countries': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='country_add', renderer='country_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def country_add(request):
    form = CountryForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        con = Country(country_id = form.country_id.data.upper(),
                      country_name = form.country_name.data,
                      region = form.region.data)
        DBSession.add(con)
        request.session.flash('Country Added!')
        return HTTPFound(location=request.route_url('country_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='country_edit', renderer='country_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def country_edit(request):
    country = DBSession.query(Country).filter(Country.country_id==request.matchdict['con_id']).first()
    form = CountryForm(request.POST, country, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        country.country_id = form.country_id.data.upper()
        country.country_name = form.country_name.data
        country.region = form.region.data
        DBSession.add(country)
        request.session.flash('Country Updated!')
        return HTTPFound(location=request.route_url('country_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='job_view', renderer='job_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='job_view:page', renderer='job_r.jinja2', request_method='GET',
             permission='view')
def job_view(request):
    #Sorting custom code
    sort_value = 'hr_jobs_job_title'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        jobs = DBSession.query(Job).order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #Pagination logic
    current_page = int(request.matchdict.get('page', '1'))
    url_for_page = lambda p: request.route_url('job_view:page', page=p) + '?sort=' + sort_value
    records = Page(jobs, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'jobs': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='job_add', renderer='job_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def job_add(request):
    form = JobForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        job = Job(job_title = form.job_title.data,
                  min_salary = form.min_salary.data,
                  max_salary = form.max_salary.data)
        DBSession.add(job)
        request.session.flash('Job Added!')
        return HTTPFound(location=request.route_url('job_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='job_edit', renderer='job_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def job_edit(request):
    job = DBSession.query(Job).filter(Job.job_id==request.matchdict['job_id']).first()
    form = JobForm(request.POST, job, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        job.job_title = form.job_title.data
        job.min_salary = form.min_salary.data
        job.max_salary = form.max_salary.data
        DBSession.add(job)
        request.session.flash('Job Updated!')
        return HTTPFound(location=request.route_url('job_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}



@view_config(route_name='location_view', renderer='location_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='location_view:page', renderer='location_r.jinja2', request_method='GET',
             permission='view')
def location_view(request):
    #Sorting custom code
    sort_value = 'hr_locations_street_address'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')
    try:
        locations = DBSession.query(Location, Country).outerjoin(Country, Location.country_id==Country.country_id).\
            order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('location_view:page', page=p) + '?sort=' + sort_value
    records = Page(locations, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'locations': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='location_add', renderer='location_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def location_add(request):
    form = LocationForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        loc = Location(street_address = form.street_address.data,
                      city = form.city.data,
                      postal_code = form.postal_code.data,
                      state_province = form.state_province.data,
                      country = form.country.data.country)
        DBSession.add(loc)
        request.session.flash('Location Added!')
        return HTTPFound(location=request.route_url('location_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='location_edit', renderer='location_f.jinja2', request_method=['GET','POST'],
             permission='edit')
def location_edit(request):
    location = DBSession.query(Location).filter(Location.location_id==request.matchdict['loc_id']).first()
    form = LocationForm(request.POST, location, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        location.street_address = form.street_address.data
        location.city = form.city.data
        location.postal_code = form.postal_code.data
        location.state_province = form.state_province.data
        location.country = form.country.data.country
        DBSession.add(location)
        request.session.flash('Location Updated!')
        return HTTPFound(location=request.route_url('location_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}



@view_config(route_name='user_view', renderer='user_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='user_view:page', renderer='user_r.jinja2', request_method='GET',
             permission='view')
def user_view(request):

    #Sorting custom code
    sort_value = 'sec_user_username'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        users = DBSession.query(User).order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)

    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('user_view:page', page=p) + '?sort=' + sort_value
    records = Page(users, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'users': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='user_add', renderer='user_f.jinja2', request_method=['GET','POST'],
             permission='admin')
def user_add(request):
    form = UserForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        usr = User()
        form.populate_obj(usr)
        #Employee(username=form.username.data, pwd=form.pwd.data)
        DBSession.add(usr)
        request.session.flash('User Added!')
        return HTTPFound(location=request.route_url('home'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='user_edit', renderer='user_f.jinja2', request_method=['GET','POST'],
             permission='admin')
def user_edit(request):
    try:
        user = DBSession.query(User).filter(User.id==request.matchdict['usr_id']).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    form = UserForm(request.POST, user, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        DBSession.add(user)
        request.session.flash('User Updated!')
        return HTTPFound(location=request.route_url('home'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='group_view', renderer='group_r.jinja2', request_method='GET',
             permission='view')
@view_config(route_name='group_view:page', renderer='group_r.jinja2', request_method='GET',
             permission='view')
def group_view(request):

    #Sorting custom code
    sort_value = 'sec_group_groupname'
    if request.GET.get('sort'):
        sort_value = request.GET.get('sort')

    try:
        groups = DBSession.query(Group).order_by(sort_value).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)

    #Pagination logic
    current_page = int(request.matchdict.get('page','1'))
    url_for_page = lambda p: request.route_url('group_view:page', page=p) + '?sort=' + sort_value
    records = Page(groups, current_page, url_maker=url_for_page, items_per_page=ITEMS_PER_PAGE)

    return {'records': records,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='group_add', renderer='group_f.jinja2', request_method=['GET','POST'],
             permission='admin')
def group_add(request):
    form = GroupForm(request.POST, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        gro = Group()
        form.populate_obj(gro)
        #Employee(username=form.username.data, pwd=form.pwd.data)
        DBSession.add(gro)
        request.session.flash('Group Added!')
        return HTTPFound(location=request.route_url('group_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='group_edit', renderer='group_f.jinja2', request_method=['GET','POST'],
             permission='admin')
def group_edit(request):
    try:
        group = DBSession.query(Group).filter(Group.id==request.matchdict['gro_id']).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    form = GroupForm(request.POST, group, csrf_context=request.session)
    if request.method == 'POST' and form.validate():
        form.populate_obj(group)
        DBSession.add(group)
        request.session.flash('Group Updated!')
        return HTTPFound(location=request.route_url('group_view'))
    return {'form': form,
            'logged_in': authenticated_userid(request)}


@view_config(route_name='summary_view', renderer='json', request_method=['GET'],
             permission='view')
def summary_view(request):
    query = SummaryQuery()
    result = [{'Region': r, 'Country': c, 'Location': lc+', '+ls, 'Department': d, 'Employees': e}
                          for r, c, lc, ls, d, e in query]
    #It is possible to dump alchemy response directly but there will be no keys
    #result = json.dumps(query)
    result_json = result

    return result_json

@view_config(route_name='summary_rep', renderer='summary_r.jinja2', request_method=['GET'],
             permission='view')
def summary_rep(request):
    #Imitating external REST service call
    r = Request.blank('http://localhost:6553/reports/summary')
    resp = r.send()
    #Response is decoded into str to support json.loads
    result = resp.body.decode(encoding='UTF-8')
    query_result = json.loads(result)
    #When quotes were present in .body, we need double json.loads on string
    #query_result = json.loads(json.loads(result))
    return {'query_result': query_result,
            'logged_in': authenticated_userid(request)}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_alchemy_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
