import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, DateTime, Boolean, String, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker, relationship
import environ

# Инициализация переменной среды
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env('.env')

engine = create_engine(f'mysql://{env("MYSQL_DB_LOGIN")}:{env("MYSQL_DB_PASS")}@localhost/course', echo=True)

Base = declarative_base(engine)


# Классы моделей
class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)

    def __init__(self, name, phone):
        """"""
        self.name = name
        self.phone = phone


class TableModel(Base):
    __tablename__ = 'table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall = Column(String)
    seats_number = Column(Integer)
    busy_status = Column(Boolean)

    def __init__(self, hall, seats_number, busy_status):
        """"""
        self.hall = hall
        self.seats_number = seats_number
        self.busy_status = busy_status


class Worker(Base):
    __tablename__ = 'worker'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    position = Column(String)
    salary = Column(Integer)

    def __init__(self, name, phone, position, salary):
        """"""
        self.name = name
        self.phone = phone
        self.position = position
        self.salary = salary


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime)
    table_id = Column(Integer, ForeignKey('table.id'))
    client_id = Column(Integer, ForeignKey('table.id'))
    # booking = relationship("TableModel", back_populates="booking")

    def __init__(self, time, table_id, client_id):
        """"""
        self.time = time
        self.table_id = table_id
        self.client_id = client_id


class Bill(Base):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("table.id"))
    worker_id = Column(Integer, ForeignKey("worker.id"))
    client_id = Column(Integer, ForeignKey("client.id"))
    total = Column(Integer)
    time = Column(DateTime(timezone=True), default=func.now())
    payment_status = Column(Boolean)

    def __init__(self, table_id, worker_id, client_id, total, payment_status):
        """"""
        self.table_id = table_id
        self.worker_id = worker_id
        self.client_id = client_id
        self.total = total
        self.payment_status = payment_status


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Integer)
    bill_id = Column(Integer, ForeignKey("bill.id"))
    name = Column(String)

    def __init__(self, price, bill_id, name):
        """"""
        self.price = price
        self.bill_id = bill_id
        self.name = name


# Метод создания сессии
def get_session():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session