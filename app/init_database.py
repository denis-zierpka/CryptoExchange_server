from datetime import datetime
from decimal import Decimal
from random import randint
from time import sleep

from app.database import Cryptocurrency, create_session
from app.local_info import Info, time_of_last_operation


def init_database() -> None:
    with create_session() as session:
        answer = session.query(Cryptocurrency).first()
        if answer is None:
            currency1 = Cryptocurrency(name='Bitcoin', price=Info.Bitcoin_price)
            currency2 = Cryptocurrency(name='Ethereum', price=Info.Ethereum_price)
            currency3 = Cryptocurrency(name='Litecoin', price=Info.Litecoin_price)
            currency4 = Cryptocurrency(name='Cardano', price=Info.Cardano_price)
            currency5 = Cryptocurrency(name='Dogecoin', price=Info.Dogecoin_price)
            session.add_all([currency1, currency2, currency3, currency4, currency5])


def update_rate() -> None:
    while True:
        with create_session() as session:
            for cryptocurrency in session.query(Cryptocurrency):
                r = randint(-10, 10)
                cryptocurrency.price = str(
                    Decimal(cryptocurrency.price)
                    + Decimal(cryptocurrency.price) * Decimal(r) / 100
                )
        time_of_last_operation.time = datetime.now()
        sleep(Info.cryptocurrency_update_time)
