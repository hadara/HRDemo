from wtforms import Form, BooleanField, StringField, IntegerField, SelectField, \
    HiddenField, validators, FormField, DateField, PasswordField
from wtforms.widgets import PasswordInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import ValidationError
from .models import Employee, Department, DBSession, Group, Job, Location, Region, Country

def Jobs():
    return DBSession.query(Job).all()

def Locations():
    return DBSession.query(Location).all()

def Countries():
        return DBSession.query(Country).all()

def Regions():
    return DBSession.query(Region).all()

def Employees():
    return DBSession.query(Employee).all()

def Departments():
    return DBSession.query(Department).all()

def Groups():
    return DBSession.query(Group).all()


#For CSRF security override with Pyramid session get_csrf_token
class BaseForm(SessionSecureForm):
    def generate_csrf_token(self, session):
        """Get the session's CSRF token."""
        return session.get_csrf_token()

    def validate_csrf_token(form, field):
        """Validate the CSRF token."""
        if field.data != field.current_token:
            raise ValidationError('Invalid CSRF token; the form probably expired.  Try again.')


class LoginForm(BaseForm):
    came_from = HiddenField(u'Came_from')
    login = StringField(u'Login')
    password = PasswordField(u'Password')


class EmployeeForm(BaseForm):
    employee_id = HiddenField()
    first_name = StringField(u'First Name', [validators.Length(min=4, max=64), validators.InputRequired(message=(u'Input First Name'))])
    last_name = StringField(u'Last Name', [validators.Length(min=4, max=64), validators.InputRequired(message=(u'Input Last Name'))])
    email = StringField(u'E-mail', [validators.Email(), validators.InputRequired(message=(u'Input E-mail'))])
    phone_number = StringField(u'Phone Number', [validators.Length(min=4, max=20), validators.InputRequired(message=(u'Input Phone Number'))])
    salary = IntegerField(u'Salary', [validators.InputRequired(message=(u'Input Salary'))])
    hire_date = DateField(u'Hire Date', [validators.InputRequired(message=(u'Select Hire Date'))], format='%d-%m-%Y')
    end_date = DateField(u'End Date', [validators.Optional()], format='%d-%m-%Y')
    job = QuerySelectField(u'Job', [validators.DataRequired()], query_factory=Jobs, allow_blank=True)
    department = QuerySelectField('Department', [validators.DataRequired()], query_factory=Departments, allow_blank=True)
    manager = QuerySelectField('Manager', query_factory=Employees, allow_blank=True)


class DepartmentForm(BaseForm):
    department_name = StringField(u'Department Name', [validators.Length(min=3, max=60),
                                         validators.InputRequired(message=(u'Input Department Name'))])
    location = QuerySelectField(u'Location', query_factory=Locations, allow_blank=True)
    manager = QuerySelectField(u'Manager', query_factory=Employees, allow_blank=True)


class JobForm(BaseForm):
    job_title= StringField(u'Job Title', [validators.Length(min=3, max=30),
                                         validators.InputRequired(message=(u'Input required'))])
    min_salary = IntegerField(u'Min Salary', [validators.InputRequired(message=(u'Input required'))])
    max_salary = IntegerField(u'Max Salary', [validators.InputRequired(message=(u'Input required'))])


class LocationForm(BaseForm):
    street_address = StringField(u'Street Address', [validators.Length(min=3, max=40),
                                         validators.InputRequired(message=(u'Input required'))])
    postal_code = StringField(u'Postal Code', [validators.Length(min=3, max=10),
                                         validators.InputRequired(message=(u'Input required'))])
    city = StringField(u'City', [validators.Length(min=3, max=30),
                                         validators.InputRequired(message=(u'Input required'))])
    state_province = StringField(u'State/Province', [validators.Length(min=3, max=30),
                                         validators.InputRequired(message=(u'Input required'))])
    country = QuerySelectField(u'Country', query_factory=Countries, allow_blank=True)


class CountryForm(BaseForm):
    country_id = StringField(u'Country Label', [validators.Length(min=2, max=2),
                                         validators.InputRequired(message=(u'Input required'))])
    country_name = StringField(u'Country Name', [validators.Length(min=3, max=40),
                                         validators.InputRequired(message=(u'Input required'))])
    region = QuerySelectField(u'Region', query_factory=Regions, allow_blank=True)


class RegionForm(BaseForm):
    region_name = StringField(u'Region Name', [validators.Length(min=3, max=25),
                                         validators.InputRequired(message=(u'Input required'))])


#Security module forms
class GroupForm(BaseForm):
    groupname = StringField(u'Group Name', [validators.Length(min=3, max=30),
                                         validators.InputRequired(message=(u'Input required'))])


class UserForm(BaseForm):
    username = StringField(u'Username', [validators.Length(min=3, max=30),
                                         validators.InputRequired(message=(u'Input First Name'))])
    pwd = PasswordField(u'Password', [validators.InputRequired(message=(u'Password required'))],
                        widget=PasswordInput(hide_value=False))
    groups = QuerySelectMultipleField(u'Groups', query_factory=Groups, allow_blank=True)
