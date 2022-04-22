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
    hall_id = Column(Integer, ForeignKey('hall.id'))
    seats_number = Column(Integer)

    def __init__(self, hall_id, seats_number):
        """"""
        self.hall_id = hall_id
        self.seats_number = seats_number


class OrderItem(Base):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer, ForeignKey('bill.id'))
    dish_id = Column(Integer, ForeignKey('dish.id'))
    quantity = Column(Integer)

    def __init__(self, bill_id, dish_id, quantity):
        """"""
        self.bill_id = bill_id
        self.dish_id = dish_id
        self.quantity = quantity


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
    time = Column(DateTime(timezone=True), default=func.now())
    payment_status = Column(Boolean)

    def __init__(self, table_id, worker_id, client_id, payment_status):
        """"""
        self.table_id = table_id
        self.worker_id = worker_id
        self.client_id = client_id
        self.payment_status = payment_status


class Hall(Base):
    __tablename__ = 'hall'

    id = Column(Integer, primary_key=True, autoincrement=True)
    space = Column(Integer)
    name = Column(String)

    def __init__(self, name, space):
        """"""
        self.name = name
        self.space = space


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Integer)
    name = Column(String)

    def __init__(self, price, name):
        """"""
        self.price = price
        self.name = name


# Метод создания сессии
def get_session():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session