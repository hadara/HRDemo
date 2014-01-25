from sqlalchemy import Column, Index, Integer, String, ForeignKey, Text, Table, Date, DateTime, func

from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker

from sqlalchemy.ext.declarative import declarative_base


from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()




class Region(Base):
    __tablename__ = 'hr_regions'
    region_id = Column(Integer, primary_key = True)
    region_name = Column(String(25))
    def __repr__(self):
        return '<Region %r>' % (self.region_name)
    def __str__(self):
        return self.region_name


class Country(Base):
    __tablename__ = 'hr_countries'
    country_id = Column(String(3), primary_key = True)
    country_name = Column(String(40))
    region_id = Column(Integer, ForeignKey('hr_regions.region_id'))
    region = relationship('Region', backref='hr_countries')
    def __repr__(self):
        return '<Country %r>' % (self.country_name)
    def __str__(self):
        return self.country_name


class Location(Base):
    __tablename__ = 'hr_locations'
    location_id = Column(Integer, primary_key = True)
    street_address = Column(String(40))
    postal_code = Column(String(10))
    city = Column(String(30))
    state_province = Column(String(30))
    country_id = Column(String(2), ForeignKey('hr_countries.country_id'))
    country = relationship('Country')
    #departments = relationship('Department')
    def __repr__(self):
        return '<Location %r>' % (self.street_address + ', ' + self.city)
    def __str__(self):
        return self.city + ', ' + self.street_address




class Employee(Base):
    __tablename__ = 'hr_employees'
    employee_id = Column(Integer, primary_key = True)
    first_name = Column(String(20), nullable = False)
    last_name = Column(String(25), nullable = False)
    email = Column(String(40))
    phone_number = Column(String(20))
    hire_date = Column(Date, nullable = False)
    end_date = Column(Date, nullable = True)
    salary = Column(Integer(8,2))

    job_id = Column(Integer, ForeignKey('hr_jobs.job_id'))
    job = relationship('Job', backref='hr_employees')

    department_id = Column(Integer, ForeignKey('hr_departments.department_id'))
    department = relationship("Department", backref="hr_employees", foreign_keys=[department_id])

    #Self relationship
    manager_id = Column(Integer, ForeignKey('hr_employees.employee_id'))
    manager = relationship('Employee', remote_side=[employee_id], post_update=True)

    def __repr__(self):
        return '<Employee %r>' % (self.last_name)
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    def name(self):
        return self.first_name + ' ' + self.last_name

class Department(Base):
    __tablename__ = 'hr_departments'
    department_id = Column(Integer, primary_key = True)
    department_name = Column(String(60), nullable = False)

    manager_id = Column(Integer, ForeignKey('hr_employees.employee_id', use_alter=True,
                                            name="fk_department_manager"))
    manager = relationship('Employee', backref='hr_departments',
                                      primaryjoin=manager_id==Employee.employee_id, post_update=True)
    employees = relationship('Employee', primaryjoin=department_id==Employee.department_id)


    location_id = Column(Integer, ForeignKey('hr_locations.location_id'))
    location = relationship('Location', backref='hr_departments')

    def __repr__(self):
        return '<Department %r>' % (self.department_name)
    def __str__(self):
        return self.department_name

class Job(Base):
    __tablename__ = 'hr_jobs'
    job_id = Column(Integer, primary_key = True)
    job_title = Column(String(30))
    min_salary = Column(Integer(8))
    max_salary = Column(Integer(8))
    employees = relationship(Employee)
    def __repr__(self):
        return '<Job %r>' % (self.job_title)
    def __str__(self):
        return self.job_title


class Job_History(Base):
    __tablename__ = 'hr_job_history'
    employee_id = Column(Integer, ForeignKey('hr_employees.employee_id'), primary_key = True)
    start_date = Column(Date)
    end_date = Column(Date)
    job_id = Column(Integer, ForeignKey('hr_jobs.job_id'), primary_key = True)
    department_id = Column(Integer, ForeignKey('hr_departments.department_id'), primary_key = True)
    job = relationship('Job')
    department = relationship('Department')


#Security models
class User(Base):
    __tablename__ = 'sec_user'
    id = Column(Integer, primary_key = True)
    username = Column(String(30))
    pwd = Column(String(100), nullable=False)
    #Many-to-many
    groups = relationship('Group', secondary='sec_user_groups', backref='sec_user')
    def __repr__(self):
        return '<User %r>' % (self.username)
    def __str__(self):
        return self.username

Index('sec_user_idx', User.username, unique=True)


class Group(Base):
    __tablename__ = 'sec_group'
    id = Column(Integer, primary_key = True)
    groupname = Column(String(60))
    users = relationship('User', secondary='sec_user_groups')
    def __repr__(self):
        return '<Group %r>' % (self.groupname)
    def __str__(self):
        return self.groupname


user_groups = Table('sec_user_groups', Base.metadata,
    Column('user', Integer, ForeignKey('sec_user.id'), primary_key=True),
    Column('group', Integer, ForeignKey('sec_group.id'), primary_key=True))


def Summary():
    return DBSession.query(Region.region_name, Country.country_name, Location.city, Department.department_name,
                                  func.count(Employee.employee_id)).\
                            filter(Region.region_id==Country.region_id).\
                            filter(Country.country_id==Location.country_id).\
                            filter(Location.location_id==Department.location_id).\
                            filter(Department.department_id==Employee.department_id).\
                    group_by(Region.region_name, Country.country_name, Location.city, Department.department_name).\
                    order_by(Region.region_name, Country.country_name, Location.city, Department.department_name).all()



#Pagination page row count
ITEMS_PER_PAGE = 5

# u=DBSession.query(User).filter(User.groups.any(groupname='Editor')).all()
# g=DBSession.query(Group).filter(Group.users.any(username='margus')).all()