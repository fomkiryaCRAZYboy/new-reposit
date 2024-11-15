from datetime import datetime
from functools import cache
from kivy.animation import Animation
from kivy.app import App
from kivy.core.text import layout_text
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDFlatButton, MDRectangleFlatIconButton, \
    MDFillRoundFlatIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivy.cache import Cache
from kivymd import icon_definitions
from kivy.lang import Builder
from DB import db_users, db_cars, db_rented_cars

Cache.register('user_info')

class LoginApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AuthorizedScreen(name='authorized'))
        sm.add_widget(UserScreen(name='userscreen'))
        sm.add_widget(AuthorizeAdmin(name='authadmin'))
        sm.add_widget(AuthorizeAdmin01(name='authadmin01'))
        sm.add_widget(AdminScreen(name='adminscreen'))
        sm.add_widget(RentedScreen(name='rentedscreen'))
        sm.add_widget(AuthorizeAdmin02(name='authadmin02'))
        sm.add_widget(AuthorizeAdmin03(name='authadmin03'))
        sm.add_widget(AuthorizeAdmin04(name='authadmin04'))
        return sm

    def login(self, login, password):
        user = db_users.find_one({'username': login})
        Cache.append('user_info', 'username', login)
        if login == '' or password == '':
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Ошибка",
                text="Введите логин и пароль.",
                buttons=[close_button]
            )
            self.error_popup.open()
        elif user is None:
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Ошибка",
                text="Такого пользователя не существует",
                buttons=[close_button]
            )
            self.error_popup.open()
        elif user['password'] != password:
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Ошибка",
                text="Неверный пароль",
                buttons=[close_button]
            )
            self.error_popup.open()
        elif login == 'admin' and password == '001':
            self.root.current = 'adminscreen'
        elif db_rented_cars.find_one({'username': login, 'end_time': ''}):
            self.root.current = 'rentedscreen'
        else:
            self.root.current = 'userscreen'
            self.root.get_screen('userscreen').update_user_info(password)
        return user

    def reg(self, username, password):
        user = db_users.find_one({'username': username})
        if user is None:
            db_users.insert_one({'username': username, 'password': password})
            Cache.append('user_info', 'username', username)
            self.root.current = 'authorized'
        else:
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Ошибка",
                text="Пользователь с таким именем уже зарегистрирован.",
                buttons=[close_button]
            )
            self.error_popup.open()

    def close_popup(self, instance):
        self.error_popup.dismiss()

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_layout()

    def build_layout(self):
        kv_string = '''
BoxLayout:
    orientation: 'vertical'
    padding: 50
    spacing: 10

    MDLabel:
        text: 'Логин:'
        font_size: 25
        bold: True

    MDTextField:
        id: username
        multiline: False
        font_size: 25
        icon_left:"account"

    MDLabel:
        text: 'Пароль:'
        font_size: 25
        bold: True

    MDTextField:
        id: password
        password: True
        multiline: False
        font_size: 25
        icon_left:"lock"

    MDRaisedButton:
        text: 'Войти'
        on_press: app.login(username.text, password.text)
        size_hint: (1, 0.4)
        pos_hint: {'center_x': 0.5}
        bold: True
        icon_left:"account"

    MDRaisedButton:
        text: 'Зарегистроваться'
        on_press: app.reg(username.text, password.text)
        size_hint: (1, 0.4)
        pos_hint: {'center_x': 0.5}
'''
        Builder.load_string(kv_string)
        self.add_widget(Builder.load_string(kv_string))


class UserScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_layout()

    def build_layout(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.user_info_label = MDLabel(text='Вы авторизованы', halign='center', valign='top', theme_text_color='Custom', bold=True)
        layout.add_widget(self.user_info_label)
        button1 = MDRaisedButton(text='Арендовать автомобиль', bold=True, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5})
        button1.bind(on_press=self.get_auth_screen)
        button2 = MDRaisedButton(text='Выйти из аккаунта', bold=True, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5})
        button2.bind(on_press=self.logout)
        layout.add_widget(button1)
        layout.add_widget(button2)
        self.add_widget(layout)

    def update_user_info(self, password):
        self.user_info_label.text = f'Вы авторизованы\nЛогин: {Cache.get("user_info", "username")}\nПароль: {password}'

    def logout(self, instance):
        self.manager.current = 'login'

    def get_auth_screen(self, instance):
        self.manager.current = 'authorized'

class RentedScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)
        self.build_layout()

    def build_layout(self):
        self.layout.clear_widgets()
        rented_car = db_rented_cars.find_one({'username': Cache.get('user_info', 'username'), 'end_time': ''})
        if rented_car is not None:
            self.layout.add_widget(MDLabel(
                text=f'Номер арендованного автомобиля: {rented_car["number"]}\nДата и время начала аренды: {rented_car["start_date"]}, {rented_car["start_time"]}',
                halign='center',
                bold=True,
                theme_text_color='Custom'))
            self.layout.add_widget(MDRaisedButton(text='Завершить аренду',
                                                  pos_hint={'center_x': 0.5},
                                                  size_hint=(0.5, 0.2),
                                                  on_press=lambda x, n=rented_car["number"], username=Cache.get('user_info', 'username'): self.end_rent(n, username)))
        else:
            self.layout.add_widget(MDLabel(
                text='',
                halign='center',
                bold=True,
                theme_text_color='Custom'))


    def end_rent(self, number, username):
        db_rented_cars.update_one(
            {'number': number, 'username': username},
            {'$set':
                 {
                     'end_date': datetime.now().date().strftime('%d.%m.%Y'),
                     'end_time': datetime.now().time().strftime('%H:%M')
                 }
             })
        db_cars.update_one({'number': number}, {'$set': {'not_rented': True}})
        rented_car = db_rented_cars.find_one({'number': number, 'username': username})

        start_time = datetime.strptime(rented_car['start_time'], '%H:%M').time()
        end_time = datetime.strptime(rented_car['end_time'], '%H:%M').time()
        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)
        time_difference = end_datetime - start_datetime
        total_minutes = time_difference.total_seconds() / 60
        car = db_cars.find_one({'number': number})
        rent_cost_per_minute = car['rent_cost']
        total_cost = total_minutes * rent_cost_per_minute

        close_button = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.close_popup
        )
        self.error_popup = MDDialog(
            title="Аренда завершена",
            text=f"Итоговая стоимость аренды: {total_cost} рублей",
            buttons=[close_button]
        )
        self.error_popup.open()
        self.manager.current = 'userscreen'

    def close_popup(self, instance):
        self.error_popup.dismiss()
        self.manager.current = 'userscreen'

    def on_enter(self, *args):
        self.build_layout()

class AuthorizedScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.add_widget(self.scroll_view)
        self.build_layout()
        button1 = MDRaisedButton(text='Выйти из аккаунта', size_hint=(0.1, 0.1),
                                 pos_hint={'x': 0.8, 'y': 0.1}, bold=True)
        button1.bind(on_press=self.logout)
        self.add_widget(button1)

    def build_layout(self):
        if self.layout:
            self.scroll_view.remove_widget(self.layout)
        self.layout = MDGridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        cars = list(db_cars.find({'not_rented': True}))
        for car in cars:
            box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
            box.height = dp(200)
            card = MDCard(
                orientation='vertical',
                size_hint=(1, 1),
                size=(230, 195),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                md_bg_color=(0.9, 0.9, 0.9, 1),
                elevation=10,
                ripple_behavior=True
            )
            card.add_widget(MDLabel(
                text=f"Марка: {car.get('brand')}\nМодель: {car.get('model')}\nНомер: {car.get('number')}\nСтоимость аренды: {car.get('rent_cost')} рублей/мин",
                size_hint_y=None, height=dp(120), halign='left', valign='top'
            ))
            button = MDRaisedButton(text='Арендовать', size_hint=(1, None), height=dp(40), bold=True)
            button.bind(on_press=lambda x, c=car: self.rent_car(c.get('number')))
            card.add_widget(button)
            box.add_widget(card)
            self.layout.add_widget(box)
        self.scroll_view.add_widget(self.layout)

    def on_enter(self, *args):
        self.build_layout()

    def rent_car(self, number):
        db_cars.update_one({'number': number}, {'$set': {'not_rented': False}})
        db_rented_cars.insert_one({"number": number,
                                   'username': Cache.get('user_info', 'username'),
                                   'start_date': datetime.now().date().strftime('%d.%m.%Y'),
                                   'start_time': datetime.now().time().strftime('%H:%M'),
                                   'end_date': '',
                                   'end_time': ''
                                   })
        close_button = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.close_popup
        )
        self.error_popup = MDDialog(
            title="Вы арендовали автомобиль",
            text="",
            buttons=[close_button]
        )
        self.error_popup.open()
        self.manager.current = 'rentedscreen'

    def close_popup(self, instance):
        self.error_popup.dismiss()

    def logout(self, instance):
        self.manager.current = 'login'

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        label = MDLabel(text='Вы авторизовалиь как администратор', halign='center', pos_hint={'center_y': 0.9}, theme_text_color='Custom', bold=True)
        button1 = MDRaisedButton(text='Выйти из аккаунта', bold=True, size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.75})
        button1.bind(on_press=self.logout)
        button2 = MDRaisedButton(text='Добавить автомобиль', bold=True, size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.63})
        button2.bind(on_press=self.get_admin_screen)
        button3 = MDRaisedButton(text='Удалить автомобиль', bold=True, size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.51})
        button3.bind(on_press=self.get_admin_screen01)
        button4 = MDRaisedButton(text='Посмотреть список автомобилей', bold=True, size_hint=(0.7, 0.1),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.39})
        button4.bind(on_press=self.get_admin_screen02)
        button5 = MDRaisedButton(text='Посмотреть список арендованных на данный момент автомобилей', bold=True, size_hint=(0.7, 0.1),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.27})
        button5.bind(on_press=self.get_admin_screen03)
        button6 = MDRaisedButton(text='Посмотреть историю аренды', bold=True, size_hint=(0.7, 0.1),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.15})
        button6.bind(on_press=self.get_admin_screen04)
        self.add_widget(label)
        self.add_widget(button1)
        self.add_widget(button2)
        self.add_widget(button3)
        self.add_widget(button4)
        self.add_widget(button5)
        self.add_widget(button6)

    def logout(self, instance):
        self.manager.current = 'login'

    def get_admin_screen(self, instance):
        self.manager.current = 'authadmin'

    def get_admin_screen01(self, instance):
        self.manager.current = 'authadmin01'

    def get_admin_screen02(self, instance):
        self.manager.current = 'authadmin02'

    def get_admin_screen03(self, instance):
        self.manager.current = 'authadmin03'

    def get_admin_screen04(self, instance):
        self.manager.current = 'authadmin04'

class AuthorizeAdmin(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_layout()

    def build_layout(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.number_input = MDTextField(hint_text='Номер', size_hint=(1, None), height=50)
        self.model_input = MDTextField(hint_text='Модель', size_hint=(1, None), height=50)
        self.brand_input = MDTextField(hint_text='Марка', size_hint=(1, None), height=50)
        self.rent_cost_input = MDTextField(hint_text='Стоимость аренды', size_hint=(1, None), height=50)
        button = MDRaisedButton(text='Добавить автомобиль', size_hint=(1, None), size=(200, 50))
        button.bind(on_press=self.add_car)
        button1 = MDRectangleFlatButton(text='Назад', size_hint=(1, None), pos_hint={'x': 0, 'y': 0.8}, size=(100, 100))
        button1.bind(on_press=self.get_back)
        layout.add_widget(MDLabel(text='Номер автомобиля:', size_hint=(1, None), height=50, font_size=30, bold=True))
        layout.add_widget(self.number_input)
        layout.add_widget(MDLabel(text='Модель автомобиля:', size_hint=(1, None), height=50, font_size=30, bold=True))
        layout.add_widget(self.model_input)
        layout.add_widget(MDLabel(text='Марка автомобиля:', size_hint=(1, None), height=50, font_size=30, bold=True))
        layout.add_widget(self.brand_input)
        layout.add_widget(MDLabel(text='Цена аренды автомобиля за минуту:', size_hint=(1, None), height=50, font_size=30, bold=True))
        layout.add_widget(self.rent_cost_input)
        layout.add_widget(button)
        layout.add_widget(button1)
        self.add_widget(layout)

    def get_back(self, instance):
        self.manager.current = 'adminscreen'

    def add_car(self, instance):
        number = self.number_input.text
        model = self.model_input.text
        brand = self.brand_input.text
        rent_cost = self.rent_cost_input.text
        if not number:
            self.show_error_popup('Номер автомобиля не может быть пустым')
            return
        if not model:
            self.show_error_popup('Модель автомобиля не может быть пустой')
            return
        if not brand:
            self.show_error_popup('Марка автомобиля не может быть пустой')
            return
        if not rent_cost:
            self.show_error_popup('Стоимость аренды автомобиля не может быть пустой')
            return
        if not rent_cost.isdigit():
            self.show_error_popup('Стоимость аренды автомобиля должна быть числом')
            return
        car = db_cars.find_one({'number': number})
        if car is None:
            db_cars.insert_one({'number': number, 'model': model, 'brand': brand, 'rent_cost': int(rent_cost), 'not_rented': True})
            self.number_input.text = ''
            self.model_input.text = ''
            self.brand_input.text = ''
            self.rent_cost_input.text = ''
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Вы добавили автомобиль",
                text="",
                buttons=[close_button]
            )
            self.error_popup.open()
        else:
            self.show_error_popup('Автомобиль с таким номером уже существует')

    def show_error_popup(self, message):
        close_button = MDFlatButton(
            text='Закрыть',
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.close_popup
        )
        self.error_popup = MDDialog(
            title="Ошибка",
            text=message,
            buttons=[close_button]
        )
        self.error_popup.open()

    def close_popup(self, instance):
        self.error_popup.dismiss()

class AuthorizeAdmin01(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_layout()

    def build_layout(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.number_input = MDTextField(hint_text='Номер', size_hint=(1, None), height=50)
        button = MDRaisedButton(text='Удалить автомобиль', size_hint=(1, None))
        button.bind(on_press=self.del_car)
        button1 = MDRectangleFlatButton(text='Назад', size_hint=(1, None))
        button1.bind(on_press=self.get_back)
        layout.add_widget(MDLabel(text='Номер автомобиля, который Вы хотите удалить:', bold=True, size_hint=(1, None), height=50, font_size=30))
        layout.add_widget(self.number_input)
        layout.add_widget(button)
        layout.add_widget(button1)
        self.add_widget(layout)

    def del_car(self, instance):
        number = self.number_input.text
        if not number:
            self.show_error_popup2('Номер автомобиля не может быть пустым')
            return
        car = db_cars.find_one({'number': number})
        if car is None:
            self.show_error_popup('Автомобиля с таким номером нет в базе данных')
        else:
            db_cars.delete_one({'number': number})
            self.number_input.text = ''
            close_button = MDFlatButton(
                text="Закрыть",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup
            )
            self.error_popup = MDDialog(
                title="Вы удалили автомобиль",
                text="",
                buttons=[close_button]
            )
            self.error_popup.open()

    def show_error_popup(self, message):
        close_button = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.close_popup
        )
        self.error_popup = MDDialog(
            title="Ошибка",
            text="Такого автомобиля нет в базе данных",
            buttons=[close_button]
        )
        self.error_popup.open()

    def show_error_popup2(self, message):
        close_button = MDFlatButton(
            text="Закрыть",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.close_popup
        )
        self.error_popup = MDDialog(
            title="Ошибка",
            text="Поле не должно быть пустым",
            buttons=[close_button]
        )
        self.error_popup.open()

    def close_popup(self, instance):
        self.error_popup.dismiss()

    def get_back(self, instance):
        self.manager.current = 'adminscreen'

class AuthorizeAdmin02(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.add_widget(self.scroll_view)
        self.build_layout()

    def build_layout(self):
        if self.layout:
            self.scroll_view.remove_widget(self.layout)
        self.layout = MDGridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        cars = list(db_cars.find({'not_rented': True}))
        for car in cars:
            box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
            box.height = dp(130)
            card = MDCard(
                orientation='vertical',
                size_hint=(1, 0.8),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                md_bg_color=(0.9, 0.9, 0.9, 1),
                elevation=10,
                ripple_behavior=True
            )
            card.add_widget(MDLabel(
                text=f" Марка: {car.get('brand')}\n Модель: {car.get('model')}\n Номер: {car.get('number')}\n Стоимость аренды: {car.get('rent_cost')} рублей/мин",
                size_hint_y=None, height=dp(120), halign='left', valign='top'
            ))
            box.add_widget(card)
            self.layout.add_widget(box)
        button = MDRaisedButton(text='Назад', size_hint=(0.1, 0.1),
                                pos_hint={'x': 0.8, 'y': 0.8})
        button.bind(on_press=self.get_back)
        self.layout.add_widget(button)
        self.scroll_view.add_widget(self.layout)

    def on_enter(self, *args):
        self.build_layout()

    def get_back(self, instance):
        self.manager.current = 'adminscreen'

class AuthorizeAdmin03(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.add_widget(self.scroll_view)
        self.build_layout()

    def build_layout(self):
        if self.layout:
            self.scroll_view.remove_widget(self.layout)
        self.layout = MDGridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        cars = list(db_cars.find({'not_rented': False}))
        for car in cars:
            rented_car = db_rented_cars.find_one({'number': car['number'], 'end_time': ''})
            if rented_car:
                box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
                box.height = dp(130)
                card = MDCard(
                    orientation='vertical',
                    size_hint=(1, 0.8),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    md_bg_color=(0.9, 0.9, 0.9, 1),
                    elevation=10,
                    ripple_behavior=True
                )
                card.add_widget(MDLabel(
                    text=f" Номер арендованной машины: {car.get('number')}\n Имя пользователя: {rented_car.get('username')}\n Дата и вермя начала аренды: {rented_car.get('start_date')} {rented_car.get('start_time')}",
                    size_hint_y=None, height=dp(120), halign='left', valign='top'
                ))
                box.add_widget(card)
                self.layout.add_widget(box)
        button = MDRaisedButton(text='Назад', size_hint=(0.1, 0.1),
                                pos_hint={'x': 0.8, 'y': 0.8})
        button.bind(on_press=self.get_back)
        self.layout.add_widget(button)
        self.scroll_view.add_widget(self.layout)

    def on_enter(self, *args):
        self.build_layout()

    def get_back(self, instance):
        self.manager.current = 'adminscreen'

class AuthorizeAdmin04(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.add_widget(self.scroll_view)
        self.build_layout()

    def build_layout(self):
        if self.layout:
            self.scroll_view.remove_widget(self.layout)
        self.layout = MDGridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        cars = list(db_rented_cars.find({'end_time': {'$ne': ''}, 'end_date': {'$ne': ''}}))
        for car in cars:
            rented_car = db_rented_cars.find_one({'number': car['number'], 'end_time': {'$ne': ''}, 'end_date': {'$ne': ''}})
            if rented_car:
                box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
                box.height = dp(230)
                card = MDCard(
                    orientation='vertical',
                    size_hint=(1, 0.8),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    md_bg_color=(0.9, 0.9, 0.9, 1),
                    elevation=10,
                    ripple_behavior=True
                )
                card.add_widget(MDLabel(
                    text=f" Номер арендованной машины: {car.get('number')}\n Имя пользователя: {rented_car.get('username')}\n Дата и время начала аренды: {rented_car.get('start_date')} {rented_car.get('start_time')}\n Дата и время окончания аренды: {rented_car.get('end_date')} {rented_car.get('end_time')}",
                    size_hint_y=None, height=dp(230), halign='left', valign='top'
                ))
                box.add_widget(card)
                self.layout.add_widget(box)
        button = MDRaisedButton(text='Назад', size_hint=(0.1, 0.1),
                                pos_hint={'x': 0.8, 'y': 0.8})
        button.bind(on_press=self.get_back)
        self.layout.add_widget(button)
        self.scroll_view.add_widget(self.layout)

    def on_enter(self, *args):
        self.build_layout()

    def get_back(self, instance):
        self.manager.current = 'adminscreen'

if __name__ == '__main__':
    LoginApp().run()