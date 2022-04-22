import datetime

from PyQt5.QtCore import Qt
from dateutil import parser
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QMessageBox, QPushButton, QCheckBox, \
    QHBoxLayout, QLabel, QComboBox
import sys

from sqlalchemy import and_

from db.tables.tables import Client, TableModel, get_session, Bill, Dish, Worker, Booking, Hall, OrderItem


#   Основной класс приложения
class App(QWidget):
    def __init__(self, db_session):
        self.ui = None
        self.modal = None
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
        self.ui = uic.loadUi('forms/ui.ui')
        self.ui.go_dishes_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(1))
        self.ui.go_clients_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(2))
        self.ui.go_workers_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(3))
        self.ui.go_halls_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(4))
        self.ui.go_tables_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(5))
        self.ui.go_bills_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(6))
        self.ui.go_booking_btn.clicked.connect(lambda: self.ui.window_tabs.setCurrentIndex(7))
        self.ui.reservation_btn.clicked.connect(lambda: self.add_reservation())

        self.ui.add_client_btn.clicked.connect(lambda: self.show_add_client_modal())
        self.ui.edit_client_btn.clicked.connect(lambda: self.show_edit_client_modal())
        self.ui.delete_client_btn.clicked.connect(lambda: self.delete_rows(ex.ui.clients_table, Client))

        self.ui.add_dish_btn.clicked.connect(lambda: self.show_add_dish_modal())
        self.ui.edit_dish_btn.clicked.connect(lambda: self.show_edit_dish_modal())
        self.ui.delete_dish_btn.clicked.connect(lambda: self.delete_rows(ex.ui.dishes_table, Dish))

        self.ui.add_worker_btn.clicked.connect(lambda: self.show_add_worker_modal())
        self.ui.edit_worker_btn.clicked.connect(lambda: self.show_edit_worker_modal())
        self.ui.delete_worker_btn.clicked.connect(lambda: self.delete_rows(ex.ui.workers_table, Worker))

        self.ui.add_worker_btn.clicked.connect(lambda: self.show_add_worker_modal())
        self.ui.edit_worker_btn.clicked.connect(lambda: self.show_edit_worker_modal())
        self.ui.delete_worker_btn.clicked.connect(lambda: self.delete_rows(ex.ui.workers_table, Worker))

        self.ui.add_hall_btn.clicked.connect(lambda: self.show_add_hall_modal())
        self.ui.edit_hall_btn.clicked.connect(lambda: self.show_edit_hall_modal())
        self.ui.delete_hall_btn.clicked.connect(lambda: self.delete_rows(ex.ui.halls_table, Hall))

        self.ui.add_table_btn.clicked.connect(lambda: self.show_add_table_modal())
        self.ui.edit_table_btn.clicked.connect(lambda: self.show_edit_table_modal())
        self.ui.delete_table_btn.clicked.connect(lambda: self.delete_rows(ex.ui.tables_table, TableModel))

        self.ui.add_bill_btn.clicked.connect(lambda: self.show_add_bill_modal())
        self.ui.edit_bill_btn.clicked.connect(lambda: self.show_edit_bill_modal())
        self.ui.delete_bill_btn.clicked.connect(lambda: self.delete_rows(ex.ui.bills_table, Bill))
        self.ui.add_dish_on_bill_btn.clicked.connect(lambda: self.show_add_dish_on_bill_modal())
        self.ui.close_bill_btn.clicked.connect(lambda: self.close_bill())

        self.ui.loading_btn.clicked.connect(lambda: self.show_loading_modal())

        self.ui.show()

    # Метод открытия модального окна добавления клиента
    def show_add_client_modal(self):
        self.modal = uic.loadUi('forms/client_form.ui')
        self.modal.create_client_btn.clicked.connect(lambda: self.create_client())
        self.modal.show()

    # Метод открытия модального окна добавления счета
    def show_add_bill_modal(self):
        self.modal = uic.loadUi('forms/bill_form.ui')
        self.modal.create_bill_btn.clicked.connect(lambda: self.create_bill())
        self.modal.show()

    def show_add_dish_on_bill_modal(self):
        ids = self.get_selected_items(ex.ui.bills_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/add_dish_form.ui')
            bill = self.session.query(Bill).filter_by(id=ids[0]).first()
            if bill.payment_status is True:
                self.alert(text="Нельзя добавить блюдо в оплаченный счет!")
            else:
                self.modal.add_dish_in_bill_btn.clicked.connect(lambda: self.add_dish_on_bill(bill))
                self.modal.show()
        else:
            self.alert(text="Выберите одно блюдо!")

    # Метод открытия модального окна добавления cтола
    def show_add_table_modal(self):
        self.modal = uic.loadUi('forms/table_form.ui')
        self.modal.create_table_btn.clicked.connect(lambda: self.create_table())
        self.modal.show()

    # Метод открытия модального окна добавления блюда
    def show_add_dish_modal(self):
        self.modal = uic.loadUi('forms/dish_form.ui')
        self.modal.create_dish_btn.clicked.connect(lambda: self.create_dish())
        self.modal.show()

    # Метод открытия модального окна добавления блюда
    def show_add_worker_modal(self):
        self.modal = uic.loadUi('forms/worker_form.ui')
        self.modal.create_worker_btn.clicked.connect(lambda: self.create_worker())
        self.modal.show()

    # Метод открытия модального окна добавления зала
    def show_add_hall_modal(self):
        self.modal = uic.loadUi('forms/hall_form.ui')
        self.modal.create_hall_btn.clicked.connect(lambda: self.create_hall())
        self.modal.show()

    # Метод открытия модального окна изменения клиента
    def show_edit_client_modal(self):
        ids = self.get_selected_items(ex.ui.clients_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/client_form.ui')
            client = self.session.query(Client).filter_by(id=ids[0]).first()
            self.modal.client_name_input.setPlainText(client.name)
            self.modal.client_phone_input.setPlainText(client.phone)
            self.modal.create_client_btn.clicked.connect(lambda: self.update_client(client))
            self.modal.show()
        else:
            self.alert(text="Выберите одного клиента!")

    # Метод открытия модального окна изменения счета
    def show_edit_bill_modal(self):
        ids = self.get_selected_items(ex.ui.bills_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/bill_form.ui')
            bill = self.session.query(Bill).filter_by(id=ids[0]).first()
            self.modal.table_bill_input.setPlainText(str(bill.table_id))
            self.modal.client_bill_input.setPlainText(str(bill.client_id))
            self.modal.worker_bill_input.setPlainText(str(bill.worker_id))
            self.modal.create_bill_btn.clicked.connect(lambda: self.update_bill(bill))
            self.modal.show()
        else:
            self.alert(text="Выберите однин счет!")

    def show_loading_modal(self):
        self.modal = uic.loadUi('forms/loading_form.ui')
        full_loading = self.session.query(TableModel).count() * 8
        try:
            date = self.ui.loading_date_input.date().toString('yyyy-MM-dd')
            bookings = self.session.query(Booking)
            print(bookings.first().time.date())
            date_bookings = [booking for booking in bookings if str(booking.time.date()) == date]
            if len(date_bookings) == 0:
                self.alert(text="На эту дату нет бронирований!")
            else:
                loading = 100 / full_loading * len(date_bookings)
                self.modal.booking_count_input.setPlainText(str(len(date_bookings)))
                self.modal.loading_input.setPlainText(str(loading) + "%")
                self.modal.show()
        except:
            self.alert(text="Введите корректные данные!")

    # Метод закрытия счета
    def close_bill(self):
        ids = self.get_selected_items(ex.ui.bills_table)
        if len(ids) == 1:
            bill = self.session.query(Bill).filter_by(id=ids[0]).first()
            if bill.payment_status is True:
                self.alert(text="Этот счет уже закрыт!")
            else:
                bill.payment_status = True
                self.session.commit()
                self.reload_tables()
                self.alert(text="Счет успешно закрыт!")
        else:
            self.alert(text="Выберите однин счет!")

    # Метод открытия модального окна изменения стола
    def show_edit_table_modal(self):
        ids = self.get_selected_items(ex.ui.tables_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/table_form.ui')
            table = self.session.query(TableModel).filter_by(id=ids[0]).first()
            self.modal.table_hall_input.setPlainText(str(table.hall_id))
            self.modal.table_seats_input.setPlainText(str(table.seats_number))
            self.modal.create_table_btn.clicked.connect(lambda: self.update_table(table))
            self.modal.show()
        else:
            self.alert(text="Выберите один стол!")

    def show_edit_dish_modal(self):
        ids = self.get_selected_items(ex.ui.dishes_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/dish_form.ui')
            dish = self.session.query(Dish).filter_by(id=ids[0]).first()
            self.modal.dish_name_input.setPlainText(dish.name)
            self.modal.dish_price_input.setPlainText(str(dish.price))
            self.modal.create_dish_btn.clicked.connect(lambda: self.update_dish(dish))
            self.modal.show()
        else:
            self.alert(text="Выберите одно блюдо!")

    def show_edit_worker_modal(self):
        ids = self.get_selected_items(ex.ui.workers_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/worker_form.ui')
            worker = self.session.query(Worker).filter_by(id=ids[0]).first()
            self.modal.worker_name_input.setPlainText(worker.name)
            self.modal.worker_phone_input.setPlainText(worker.phone)
            self.modal.worker_position_input.setPlainText(worker.position)
            self.modal.worker_salary_input.setPlainText(str(worker.salary))
            self.modal.create_worker_btn.clicked.connect(lambda: self.update_worker(worker))
            self.modal.show()
        else:
            self.alert(text="Выберите одно блюдо!")

    # Метод открытия модального окна изменения зала
    def show_edit_hall_modal(self):
        ids = self.get_selected_items(ex.ui.halls_table)
        if len(ids) == 1:
            self.modal = uic.loadUi('forms/hall_form.ui')
            hall = self.session.query(Hall).filter_by(id=ids[0]).first()
            self.modal.hall_name_input.setPlainText(hall.name)
            self.modal.hall_space_input.setPlainText(str(hall.space))
            self.modal.create_hall_btn.clicked.connect(lambda: self.update_hall(hall))
            self.modal.show()
        else:
            self.alert(text="Выберите однин стол!")

    def create_client(self):
        try:
            client = Client(
                name=self.modal.client_name_input.toPlainText(),
                phone=self.modal.client_phone_input.toPlainText()
            )
            self.session.add(client)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Клиент успешно создан.")
        except:
            self.alert(text="Введите корректные данные!")

    def create_bill(self):
        try:
            bill = Bill(
                table_id=self.modal.table_bill_input.toPlainText(),
                client_id=self.modal.client_bill_input.toPlainText(),
                worker_id=self.modal.worker_bill_input.toPlainText(),
                payment_status=False
            )
            self.session.add(bill)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Счет успешно создан.")
        except:
            self.alert(text="Введите корректные данные!")

    def add_dish_on_bill(self, bill):
        try:
            order_item = OrderItem(
                dish_id=int(self.modal.add_dish_in_bill_input.toPlainText()),
                quantity=int(self.modal.add_quantity_in_bill_input.toPlainText()),
                bill_id=bill.id
            )
            self.session.add(order_item)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Блюдо успешно добавлено в счет.")
        except:
            self.alert(text="Введите корректные данные!")

    def create_table(self):
        try:
            table = TableModel(
                hall_id=int(self.modal.table_hall_input.toPlainText()),
                seats_number=int(self.modal.table_seats_input.toPlainText())
            )
            self.session.add(table)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Стол успешно создан.")
        except:
            self.alert(text="Введите корректные данные!")

    def create_hall(self):
        try:
            hall = Hall(
                name=self.modal.hall_name_input.toPlainText(),
                space=int(self.modal.hall_space_input.toPlainText())
            )
            self.session.add(hall)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Зал успешно создан.")
        except:
            self.alert(text="Введите корректные данные!")

    def create_dish(self):
        try:
            dish = Dish(
                name=self.modal.dish_name_input.toPlainText(),
                price=self.modal.dish_price_input.toPlainText()
            )
            self.session.add(dish)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Блюдо успешно создано.")
        except:
            self.alert(text="Введите корректные данные!")

    def create_worker(self):
        try:
            worker = Worker(
                name=self.modal.worker_name_input.toPlainText(),
                phone=self.modal.worker_phone_input.toPlainText(),
                position=self.modal.worker_position_input.toPlainText(),
                salary=int(self.modal.worker_salary_input.toPlainText())
            )
            self.session.add(worker)
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Сотрудник успешно создан.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_client(self, client):
        try:
            client.name = self.modal.client_name_input.toPlainText()
            client.phone = self.modal.client_phone_input.toPlainText()
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Клиент успешно обновлен.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_bill(self, bill):
        try:
            bill.table_id = self.modal.table_bill_input.toPlainText(),
            bill.client_id = self.modal.client_bill_input.toPlainText(),
            bill.worker_id = self.modal.worker_bill_input.toPlainText(),
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Счет успешно обновлен.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_table(self, table):
        try:
            table.hall_id = int(self.modal.table_hall_input.toPlainText())
            table.seats = int(self.modal.table_seats_input.toPlainText())
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Стол успешно обновлен.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_hall(self, hall):
        try:
            hall.name = self.modal.hall_name_input.toPlainText()
            hall.space = int(self.modal.hall_space_input.toPlainText())
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Зал успешно обновлен.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_dish(self, dish):
        try:
            dish.name = self.modal.dish_name_input.toPlainText()
            dish.price = self.modal.dish_price_input.toPlainText()
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Блюдо успешно обновлено.")
        except:
            self.alert(text="Введите корректные данные!")

    def update_worker(self, worker):
        try:
            worker.name = self.modal.worker_name_input.toPlainText()
            worker.phone = self.modal.worker_phone_input.toPlainText()
            worker.position = self.modal.worker_position_input.toPlainText()
            worker.salary = int(self.modal.worker_salary_input.toPlainText())
            self.session.commit()
            self.reload_tables()
            self.modal.close()
            self.alert(text="Сотрудник успешно обновлен.")
        except:
            self.alert(text="Введите корректные данные!")

    def delete_rows(self, table_name, table):
        ids = self.get_selected_items(table_name)
        if len(ids) > 0:
            msgBox = QMessageBox()
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setText("Вы действительно хотите удалить выбранные обьекты?")
            result = msgBox.exec_()
            if QMessageBox.Yes == result:
                for one_id in ids:
                    obj = self.session.query(table).filter_by(id=one_id).first()
                    self.session.delete(obj)
                self.reload_tables()
                self.session.commit()

    # Метод получения выбранных айтемов в таблице
    def get_selected_items(self, table):
        checked_list = []
        for i in range(table.rowCount()):
            if table.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked():
                checked_list.append(table.item(i, 1).text())
        return checked_list

    # Метод заполнения таблицы клиентов
    def set_clients_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for client_num, client in enumerate(rows):
            self.session.refresh(client)
            client = client.__dict__
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            table.setCellWidget(client_num, 0, widget)
            table.setItem(client_num, 1, QTableWidgetItem(str(client['id'])))
            table.setItem(client_num, 2, QTableWidgetItem(str(client['name'])))
            table.setItem(client_num, 3, QTableWidgetItem(str(client['phone'])))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы залов
    def set_halls_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for hall_num, hall in enumerate(rows):
            self.session.refresh(hall)
            hall = hall.__dict__

            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)

            tables_count = self.session.query(TableModel).filter(TableModel.hall_id == hall['id'])
            seats_count = 0
            free_table_count = 0
            for item in tables_count:
                busy_status = self.session.query(Bill).filter(Bill.payment_status == True,
                                                              Bill.table_id == item.id).first()
                if not busy_status is None:
                    free_table_count += 1
                seats_count += item.seats_number

            table.setCellWidget(hall_num, 0, widget)
            table.setItem(hall_num, 1, QTableWidgetItem(str(hall['id'])))
            table.setItem(hall_num, 2, QTableWidgetItem(str(hall['name'])))
            table.setItem(hall_num, 3, QTableWidgetItem(str(hall['space'])))
            table.setItem(hall_num, 4, QTableWidgetItem(str(tables_count.count())))
            table.setItem(hall_num, 5, QTableWidgetItem(str(free_table_count)))
            table.setItem(hall_num, 6, QTableWidgetItem(str(seats_count)))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы блюд
    def set_dishes_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for dish_num, dish in enumerate(rows):
            self.session.refresh(dish)
            dish = dish.__dict__
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            table.setCellWidget(dish_num, 0, widget)
            table.setItem(dish_num, 1, QTableWidgetItem(str(dish['id'])))
            table.setItem(dish_num, 2, QTableWidgetItem(str(dish['name'])))
            table.setItem(dish_num, 3, QTableWidgetItem(str(dish['price'])))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы работников
    def set_workers_table(self, table, rows: []):
        table.setRowCount(len(rows))
        for worker_num, worker in enumerate(rows):
            self.session.refresh(worker)
            worker = worker.__dict__
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            table.setCellWidget(worker_num, 0, widget)
            table.setItem(worker_num, 1, QTableWidgetItem(str(worker['id'])))
            table.setItem(worker_num, 2, QTableWidgetItem(str(worker['name'])))
            table.setItem(worker_num, 3, QTableWidgetItem(str(worker['phone'])))
            table.setItem(worker_num, 4, QTableWidgetItem(str(worker['position'])))
            table.setItem(worker_num, 5, QTableWidgetItem(str(worker['salary'])))

        table.resizeColumnsToContents()

    # Метод заполнения таблицы столов
    def set_tables_table(self):
        table = self.ui.tables_table
        rows = self.session.query(TableModel).all()

        table.setRowCount(len(rows))
        for table_num, table_model in enumerate(rows):
            self.session.refresh(table_model)
            table_model = table_model.__dict__
            booking = self.session.query(Booking).filter(Booking.table_id == table_model['id'],
                                                         Booking.time > datetime.datetime.now()).first()
            hall = self.session.query(Hall).filter(Hall.id == table_model['hall_id']).first().name
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)

            busy_status = self.session.query(Bill).filter(Bill.payment_status == True,
                                                          Bill.table_id == table_model['id']).first()
            if not busy_status is None:
                busy = "Да"
            else:
                busy = "Нет"

            table.setCellWidget(table_num, 0, widget)
            table.setItem(table_num, 1, QTableWidgetItem(str(table_model['id'])))
            table.setItem(table_num, 2, QTableWidgetItem(str(hall)))
            table.setItem(table_num, 3, QTableWidgetItem(str(table_model['seats_number'])))
            table.setItem(table_num, 4, QTableWidgetItem(busy))
            if booking:
                booking = booking.__dict__
                table.setItem(table_num, 5, QTableWidgetItem(booking['time'].strftime("%d.%m.%Y  %H:%M")))
            else:
                table.setItem(table_num, 5, QTableWidgetItem('Нет'))
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

            order_items = self.session.query(OrderItem).filter_by(bill_id=int(bill['id']))
            box = QComboBox()
            total = 0
            if order_items.count() > 0:
                for item in order_items:
                    dish = self.session.query(Dish).filter_by(id=item.dish_id).first()
                    box.addItem(dish.name + " " + str(item.quantity) + "шт")
                    total += dish.price * item.quantity

            worker = self.session.query(Worker).filter_by(id=bill['worker_id']).first()

            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            layoutH = QHBoxLayout(widget)

            layoutH.addWidget(checkbox)
            table.setCellWidget(bill_num, 0, widget)
            table.setItem(bill_num, 1, QTableWidgetItem(str(bill['id'])))
            table.setItem(bill_num, 2, QTableWidgetItem(str(bill['table_id'])))
            table.setItem(bill_num, 3, QTableWidgetItem(worker.name))

            table.setItem(bill_num, 4, QTableWidgetItem(str(total)))
            table.setItem(bill_num, 5, QTableWidgetItem(str(bill['time'])))
            table.setItem(bill_num, 6, QTableWidgetItem('Оплачен' if bill['payment_status'] == 1 else 'Нет'))
            table.setCellWidget(bill_num, 7, box)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    # Метод перезагрузки таблиц
    def reload_tables(self):
        # bills_list = self.session.query(Bill).all()
        all_clients = session.query(Client).all()
        self.set_clients_table(self.ui.clients_table, all_clients)
        all_dishes = session.query(Dish).all()
        self.set_dishes_table(self.ui.dishes_table, all_dishes)
        all_workers = session.query(Worker).all()
        self.set_workers_table(self.ui.workers_table, all_workers)
        all_halls = session.query(Hall).all()
        self.set_halls_table(self.ui.halls_table, all_halls)
        self.set_tables_table()
        self.set_bills_table()

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
    dishes = session.query(Dish).all()
    bills = session.query(Bill).all()
    workers = session.query(Worker).all()
    halls = session.query(Hall).all()

    app = QApplication(sys.argv)
    ex = App(session)

    ex.set_clients_table(ex.ui.clients_table, clients)
    ex.set_dishes_table(ex.ui.dishes_table, dishes)
    ex.set_workers_table(ex.ui.workers_table, workers)
    ex.set_halls_table(ex.ui.halls_table, halls)

    ex.set_tables_table()
    ex.set_bills_table()

    app.exec_()
