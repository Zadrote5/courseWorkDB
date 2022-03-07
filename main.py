import datetime
from dateutil import parser
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QMessageBox
import sys

from sqlalchemy import and_

from db.tables.tables import Client, TableModel, get_session, Bill, Dish, Worker, Booking


#   Основной класс приложения
class App(QWidget):
    def __init__(self, db_session):
        self.current_bill = None
        self.start()
        self.session = db_session

    # Метод отображения всплывающего окна
    def alert(self, title='Ресторан', text='Ошибка'):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec_()

    # Метод запуска приложения
    def start(self):
        self.ui = uic.loadUi('ui.ui')
        self.ui.create_bill_btn.clicked.connect(lambda: self.add_bill())
        self.ui.search_bill_btn.clicked.connect(lambda: self.search_bill())
        self.ui.reservation_btn.clicked.connect(lambda: self.add_reservation())
        self.ui.push_dish.clicked.connect(lambda: self.add_dish())
        self.ui.close_bill_btn.clicked.connect(lambda: self.close_bill())
        self.ui.show()

    # Метод заполнения таблицы клиентов
    def set_clients_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for client_num, client in enumerate(rows):
            self.session.refresh(client)
            client = client.__dict__

            table.setItem(client_num, 0, QTableWidgetItem(str(client['id'])))
            table.setItem(client_num, 1, QTableWidgetItem(str(client['name'])))
            table.setItem(client_num, 2, QTableWidgetItem(str(client['phone'])))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы работников
    def set_workers_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for worker_num, worker in enumerate(rows):
            self.session.refresh(worker)
            worker = worker.__dict__

            table.setItem(worker_num, 0, QTableWidgetItem(str(worker['id'])))
            table.setItem(worker_num, 1, QTableWidgetItem(str(worker['name'])))
            table.setItem(worker_num, 2, QTableWidgetItem(str(worker['phone'])))
            table.setItem(worker_num, 3, QTableWidgetItem(str(worker['position'])))
            table.setItem(worker_num, 4, QTableWidgetItem(str(worker['salary'])))

    # Метод заполнения таблицы столов
    def set_tables_table(self):
        table = self.ui.tables_table
        rows = self.session.query(TableModel).all()

        table.setRowCount(len(rows))
        for table_num, table_model in enumerate(rows):
            self.session.refresh(table_model)
            table_model = table_model.__dict__
            booking = self.session.query(Booking).filter(Booking.table_id == table_model['id'], Booking.time > datetime.datetime.now()).first()
            table.setItem(table_num, 0, QTableWidgetItem(str(table_model['id'])))
            table.setItem(table_num, 1, QTableWidgetItem(str(table_model['hall'])))
            table.setItem(table_num, 2, QTableWidgetItem(str(table_model['seats_number'])))
            table.setItem(table_num, 3, QTableWidgetItem('Да' if table_model['busy_status'] == 1 else 'Нет'))
            if booking:
                booking = booking.__dict__
                table.setItem(table_num, 4, QTableWidgetItem(str(booking['time'])))
            else:
                table.setItem(table_num, 4, QTableWidgetItem('Нет'))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы счетов
    def set_bills_table(self):
        table = self.ui.bills_table
        rows = self.session.query(Bill).all()
        table.setRowCount(0)
        table.setRowCount(len(rows))
        for bill_num, bill in enumerate(rows):
            self.session.refresh(bill)
            bill = bill.__dict__

            table.setItem(bill_num, 0, QTableWidgetItem(str(bill['id'])))
            table.setItem(bill_num, 1, QTableWidgetItem(str(bill['table_id'])))
            table.setItem(bill_num, 2, QTableWidgetItem(str(bill['worker_id'])))
            table.setItem(bill_num, 3, QTableWidgetItem(str(bill['total'])))
            table.setItem(bill_num, 4, QTableWidgetItem(str(bill['time'])))
            table.setItem(bill_num, 5, QTableWidgetItem('Оплачен' if bill['payment_status'] == 1 else 'Нет'))

        table.resizeColumnsToContents()

    # Метод создания счета
    def add_bill(self):
        try:
            bill = Bill(
                table_id=int(self.ui.table_check_input.toPlainText()),
                worker_id=int(self.ui.worker_check_input.toPlainText()),
                client_id=int(self.ui.client_check_input.toPlainText()),
                total=0,
                payment_status=0,
            )
            session.query(TableModel).get(bill.table_id).busy_status = 1
            self.session.add(bill)
            self.session.commit()
            self.reload_tables()
        except:
            self.alert(text="Заполните данные!")

    # Метод поиска счета
    def search_bill(self):
        try:
            bill = session.query(Bill).get(int(self.ui.bill_search_field.toPlainText()))
            self.current_bill = bill
            self.ui.sum_bill_input.setPlainText(str(bill.total))
        except:
            self.alert(text="Счета с таким номером не существует!")

    # Метод добавления блюда в счет
    def add_dish(self):
        try:
            if self.current_bill.payment_status == 1:
                return self.alert(text="Счет уже закрыт!")
            dish = Dish(
                price=int(self.ui.dish_price_input.toPlainText()),
                name=self.ui.dish_name_input.toPlainText(),
                bill_id=self.current_bill.id,
            )
            self.session.add(dish)
            self.current_bill.total += dish.price
            self.session.commit()
            self.reload_tables()
            self.ui.sum_bill_input.setPlainText(str(self.current_bill.total))
            self.alert(text=f'Блюдо {dish.name} успешно добавлено в счет №{dish.id}')
        except:
            self.alert(text="Неккоректные данные!")

    # Метод перезагрузки таблиц
    def reload_tables(self):
        bills_list = self.session.query(Bill).all()
        self.set_tables_table()
        self.set_bills_table()

    # Метод закрытия счета
    def close_bill(self):
        try:
            if self.current_bill.payment_status == 1:
                return self.alert(text="Счет уже закрыт!")
            self.current_bill.payment_status = 1
            session.query(TableModel).get(self.current_bill.table_id).busy_status = 0
            self.session.commit()
            self.reload_tables()
            self.alert(text="Счет успешно закрыт")
        except:
            self.alert(text="Введите номер счета!")

    # Метод добавления брони
    def add_reservation(self):
        try:
            reservation = Booking(
                time=parser.parse(str(self.ui.time_reservation_input.dateTime().toString('dd-MM-yyyy hh:mm'))),
                table_id=int(self.ui.table_reservation_input.toPlainText()),
                client_id=int(self.ui.client_reservation_input.toPlainText()),
            )
            self.session.add(reservation)
            self.session.commit()
            self.reload_tables()
            self.alert(text="Стол успешно забронирован.")
        except:
            self.alert(text="Введите корректные данные!")


# Запуск программы
if __name__ == '__main__':
    session = get_session()
    clients = session.query(Client).all()

    bills = session.query(Bill).all()
    workers = session.query(Worker).all()

    app = QApplication(sys.argv)
    ex = App(session)

    ex.set_clients_table(ex.ui.clients_table, clients)
    ex.set_tables_table()
    ex.set_bills_table()
    ex.set_workers_table(ex.ui.workers_table, workers)
    app.exec_()
