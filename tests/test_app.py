import json
from datetime import datetime
from time import sleep

from app import app
from app.app import flask_app
from app.database import Cryptocurrency, User, create_session
from app.local_info import Info


def test_init_database():
    with flask_app.test_request_context('/', method='POST'):
        app.start_work()
    with create_session() as session:
        cnt = 0
        result = []
        for obj in session.query(Cryptocurrency):
            cnt += 1
            print(str(obj.name))
            result.append(str(obj.name))

    assert cnt == 5
    for i in ['Bitcoin', 'Ethereum', 'Litecoin', 'Cardano', 'Dogecoin']:
        assert i in result


def test_homepage(client):
    save = client.get('/')
    assert save.data.decode('utf-8') == Info.welcome_message


def test_registration(client):
    save = client.post('/register/Test')
    assert save.data.decode('utf-8') == Info.register_success.format('Test', 1)
    save_second = client.post('/register/Test')
    assert save_second.data.decode('utf-8') == Info.user_exists


def test_money_check(client):
    with create_session() as session:
        session.add(User(id=1, login='Test', money=1000))
    save = client.get('/1/money')
    assert save.data.decode('utf-8') == Info.default_user_money + '\n'


def test_info_currency(client):
    with flask_app.test_request_context('/', method='POST'):
        app.start_work()
    save = client.get('/info/Bitcoin')
    assert save.data.decode('utf-8') != Info.user_not_in_system


def test_empty_list_user_status(client):
    with create_session() as session:
        session.add(User(id=1, login='Test', money=1000))
    save = client.get('/1/list')
    assert save.data.decode('utf-8') == Info.no_currency


def test_buy_and_sell_currency(client):
    with create_session() as session:
        session.add(Cryptocurrency(name='Bitcoin', price=200))
        session.add(User(id=1, login='Test', money=1000))

    save = client.post(
        '/1/buy/Bitcoin/1.0/' + datetime.strftime(datetime.now(), '%d.%m.%Y.%H:%M:%S')
    )
    if save.data.decode('utf-8') == Info.rate_changed_during_operation:
        sleep(1)
        save = client.post(
            '/1/buy/Bitcoin/1.0/'
            + datetime.strftime(datetime.now(), '%d.%m.%Y.%H:%M:%S')
        )
        assert save.data.decode('utf-8') == Info.successful_operation.format(
            'Bitcoin', '1.0'
        )
    assert save.data.decode('utf-8') == Info.successful_operation.format(
        'Bitcoin', '1.0'
    )

    save = client.post(
        '/1/buy/Bitcoin/1.0/' + datetime.strftime(datetime.now(), '%d.%m.%Y.%H:%M:%S')
    )
    assert save.data.decode('utf-8') == Info.successful_operation.format(
        'Bitcoin', '2.0'
    )

    save_list = client.get('/1/list')
    assert save_list.data.decode('utf-8') == 'Bitcoin 2.0\n'

    save_sell = client.post(
        '/1/sell/Bitcoin/1.0/' + datetime.strftime(datetime.now(), '%d.%m.%Y.%H:%M:%S')
    )
    if save_sell.data.decode('utf-8') == Info.rate_changed_during_operation:
        sleep(1)
        save_sell = client.post(
            '/1/sell/Bitcoin/1.0/'
            + datetime.strftime(datetime.now(), '%d.%m.%Y.%H:%M:%S')
        )
        assert save_sell.data.decode('utf-8') == Info.successful_operation.format(
            'Bitcoin', '1.0'
        )
    assert save_sell.data.decode('utf-8') == Info.successful_operation.format(
        'Bitcoin', '1.0'
    )

    save_history = client.get('/1/history')
    data = json.loads(save_history.data.decode('utf-8'))
    assert len(data) == 3


def test_sell_not_existing_currency(client):
    with create_session() as session:
        session.add(Cryptocurrency(name='Bitcoin', price=200))
        session.add(User(id=1, login='Test', money=1000))

    save = client.post('/1/sell/Bitcoin/1.0/time')
    assert save.data.decode('utf-8') == Info.failed


def test_adding_new_currency(client):
    save = client.post('/newcurrency/Testcurrency/10')
    assert save.data.decode('utf-8') == Info.successful_added_new_currency.format(
        'Testcurrency'
    )
    save_help = client.get('/help')
    assert save_help.data.decode('utf-8').count('Testcurrency') > 0
