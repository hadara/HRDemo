from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from .security import groupfinder, RootFactory

from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings = dict(settings)
    #Jinja domeen
    settings.setdefault('jinja2.i18n.domain', 'empproj')

    #Session factory (CSRF)
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')


    #SqlAlchemy:
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    #Security
    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    #RootFactory from security module
    config = Configurator(settings=settings, root_factory=RootFactory, session_factory = my_session_factory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    #Jinja:
    #config.add_translation_dirs('locale/')
    config.include('pyramid_jinja2')

    #Static
    config.add_static_view('static', 'static', cache_max_age=3600)

    #Routes
    config.add_route('home', '/')
    #Security views
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    #Departments
    config.add_route('department_view', '/departments')
    config.add_route('department_view:page', '/departments/page/{page:\d+}')
    config.add_route('department_add', '/departments/add')
    config.add_route('department_edit', '/departments/{dep_id:\d+}/edit')
    #config.add_route('department_delete', '/departments/{dep_id}/delete')
    #Employees
    config.add_route('employee_view', '/employees')
    config.add_route('employee_view:page', '/employees/page/{page:\d+}')
    config.add_route('employee_add', '/employees/add')
    config.add_route('employee_edit', '/employees/{emp_id:\d+}/edit')
    #Region
    config.add_route('region_view', '/regions')
    config.add_route('region_view:page', '/regions/page/{page:\d+}')
    config.add_route('region_add', '/regions/add')
    config.add_route('region_edit', '/regions/{reg_id:\d+}/edit')
    #Country
    config.add_route('country_view', '/countries')
    config.add_route('country_view:page', '/countries/page/{page:\d+}')
    config.add_route('country_add', '/countries/add')
    config.add_route('country_edit', '/countries/{con_id}/edit')
    #Location
    config.add_route('location_view', '/locations')
    config.add_route('location_view:page', '/locations/page/{page:\d+}')
    config.add_route('location_add', '/locations/add')
    config.add_route('location_edit', '/locations/{loc_id:\d+}/edit')
    #Job
    config.add_route('job_view', '/jobs')
    config.add_route('job_view:page', '/jobs/page/{page:\d+}')
    config.add_route('job_add', '/jobs/add')
    config.add_route('job_edit', '/jobs/{job_id:\d+}/edit')
    #Security_user
    config.add_route('user_view', '/sec/users')
    config.add_route('user_view:page', '/sec/users/page/{page:\d+}')
    config.add_route('user_add', '/sec/users/add')
    config.add_route('user_edit', '/sec/users/{usr_id:\d+}/edit')
    #Reports
    config.add_route('summary_view', '/reports/summary')
    config.add_route('summary_rep', '/reports/summary/report')


    #Security_group
    config.add_route('group_view', '/sec/groups')
    config.add_route('group_view:page', '/sec/groups/page/{page:\d+}')
    config.add_route('group_add', '/sec/groups/add')
    config.add_route('group_edit', '/sec/groups/{gro_id:\d+}/edit')


    config.scan()

    return config.make_wsgi_app()
