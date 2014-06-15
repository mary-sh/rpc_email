# -*- coding: utf-8 -*-
import urllib
import urllib2
from django.core.validators import validate_email

class Validator(object):
    '''
    Валидация email-адреса, типа события.
    Также общие (для всех типов событий) проверки деталей события и клиента
    '''

    def __init__(self, email, event_type, event_details, customer_details):
        self.email = email
        self.event_type = event_type
        self.event_details = event_details
        self.customer_details = customer_details

    def validate_email(self):
        validate_email(self.email)
        return self.email

    def validate_event_type(self):
        if self.event_type in ('trigger', 'transaction', 'order',
                               'subscription', 'registration', 'test'):
            return self.event_type
        raise ValueError

    def validate_event_details(self):
        if not isinstance(self.event_details, dict):
            raise ValueError
        # TODO: дописать проверку информации события для всех типов событий
        # TODO: для этого нужна конкретизация задания
        return self.event_details

    def validate_customer_details(self):
        if not isinstance(self.customer_details, dict):
            raise ValueError
        # TODO: дописать проверку информации клиента для всех типов событий
        # TODO: для этого нужна конкретизация задания
        return self.customer_details

    def validate(self):
        return {
            'email': self.validate_email(),
            'event_type': self.validate_event_type(),
            'event_details': self.validate_event_details(),
            'customer_details': self.validate_customer_details()
            }

class Event(object):

    email_template = '' # шаблон письма,
                        # должен быть переопределён в наследующих классах


    def __init__(self, **kwargs):
        self.raw_event_details = kwargs.get('event_details')
        self.raw_customer_details = kwargs.get('customer_details')

    def validate_event_details(self):
        '''
        Валидация деталей события в зависимости от его типа.
        Должна быть переопределена в классе-потомке
        '''
        raise NotImplementedError

    def validate_customer_details(self):
        '''
        Валидация деталей клиента в зависимости от его типа.
        Должна быть переопределена в классе-потомке
        '''
        raise NotImplementedError

    def parse_event_details(self):
        '''
        Приведение информации о событии в вид, соответствующий шаблону письма.
        Метод должен быть переопределен в классе-потомке
        '''
        raise NotImplementedError

    def parse_customer_details(self):
        '''
        Приведение информации о клиенте в вид, соответствующий шаблону письма.
        Метод должен быть переопределен в классе-потомке
        '''
        raise NotImplementedError

    @property
    def details(self):
        details = self.parse_event_details()
        details.update(self.parse_customer_details())
        return details

    @property
    def email_text(self):
        return self.email_template % self.details

class TestEvent(Event):
    '''
    Тестовое событие, для примера
    '''

    email_template = "Hello, dear %(username)s!"

    def validate_event_details(self):
        pass

    def validate_customer_details(self):
        if (not 'username' in self.raw_customer_details
            or not self.raw_customer_details['username']):
            raise ValueError

    def parse_event_details(self):
        return {}

    def parse_customer_details(self):
        return {'username': self.raw_customer_details['username']}

class TriggerEvent(Event):
    pass

class TransactionEvent(Event):
    pass

class OrderEvent(Event):
    pass

class SubscriptionEvent(Event):
    pass

class RegistrationEvent(Event):
    pass

class EventParser(object):
    '''
    Выдаёт в зависимости от типа события экземпляр соответствующего класса
    '''

    @staticmethod
    def get(**kwargs):
        event_type = kwargs.get('event_type')
        if event_type == 'trigger':
            return TriggerEvent(**kwargs)
        if event_type == 'transaction':
            return TransactionEvent(**kwargs)
        if event_type == 'order':
            return OrderEvent(**kwargs)
        if event_type == 'subscription':
            return SubscriptionEvent(**kwargs)
        if event_type == 'registration':
            return RegistrationEvent(**kwargs)
        if event_type == 'test':
            return TestEvent(**kwargs)

class EmailSender(object):
    '''
    Отправка письма
    '''

    def __init__(self, email, email_text):
        self.email = email
        self.email_text = email_text

    def do(self):
        data = {
            'email': self.email,
            'email_text': self.email_text
        }
        print data
        urllib2.urlopen('http://example.com', urllib.urlencode(data))

def send_email(email, event_type, event_details, customer_details):
    '''
    АPI-метод для автоматической отправки писем
    '''

    data = Validator(email, event_type, event_details,
                     customer_details).validate()
    event = EventParser.get(**data)
    EmailSender(data['email'], event.email_text).do()

if __name__ == '__main__':
    send_email('mary.shornikova@gmail.com',
               'test', None, {'username': 'Maria'})

