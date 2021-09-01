import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.database import (
    Cryptocurrency,
    History,
    Session,
    User,
    Userstatus,
    create_session,
)
from app.local_info import Info


class CustomError(Exception):
    def __init__(self, message: Any) -> None:
        super().__init__()
        self.message = message


def add_new_user(name: str) -> str:
    with create_session() as session:
        exists_in_database = session.query(User).filter(User.login == name).first()
        if exists_in_database:
            raise CustomError(Info.user_exists)
        user = User(login=name, money=Info.default_user_money)
        session.add(user)

        is_user_in_database = session.query(User).filter(User.login == name).first()

        if is_user_in_database:
            return Info.register_success.format(name, is_user_in_database.id)
        raise CustomError(Info.failed)


def get_money_info(user_id: int) -> str:
    with create_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomError(Info.failed)
        return str(user.money) + '\n'


def count_of_crypto(currency_name: str) -> str:
    with create_session() as session:
        answer = (
            session.query(Cryptocurrency)
            .filter(Cryptocurrency.name == currency_name)
            .first()
        )
        return str(answer.price)


def user_currency_status(user_id: int) -> str:
    with create_session() as session:
        answer = ''
        for currency in session.query(Userstatus).filter(Userstatus.user_id == user_id):
            answer += (
                str(currency.cryptocurrency) + ' ' + str(currency.count_currency) + '\n'
            )
        if answer != '':
            return answer
        return Info.no_currency


def get_user(session: Session, user_id: int) -> User:
    return session.query(User).filter(User.id == user_id).first()


def get_currency(session: Session, currency_name: str) -> Cryptocurrency:
    return (
        session.query(Cryptocurrency)
        .filter(Cryptocurrency.name == currency_name)
        .first()
    )


def get_user_status(session: Session, user_id: int, currency_name: str) -> Userstatus:
    return (
        session.query(Userstatus)
        .filter(
            Userstatus.user_id == user_id,
            Userstatus.cryptocurrency == currency_name,
        )
        .first()
    )


# pylint: disable=too-many-arguments
def add_to_history(
    session: Session,
    user_id: int,
    operation_type: str,
    currency_name: str,
    count: str,
    price: str,
) -> None:
    session.add(
        History(
            user_id=user_id,
            operation_type=operation_type,
            currency_type=currency_name,
            count_currency=count,
            currency_rate=price,
            datetime=datetime.now(),
        )
    )


def exchange_currency(
    user_id: int, currency_name: str, count: str, operation_type: str
) -> str:
    with create_session() as session:
        user = get_user(session, user_id)
        answer = get_currency(session, currency_name)
        user_status = get_user_status(session, user_id, currency_name)

        if user is None or answer is None:
            raise CustomError(Info.failed)
        if operation_type == 'buy':
            if Decimal(user.money) < Decimal(answer.price) * Decimal(count):
                raise CustomError(Info.not_enough_money)
            user.money = str(
                Decimal(user.money) - Decimal(answer.price) * Decimal(count)
            )

            if user_status is None:
                status = Userstatus(
                    user_id=user_id,
                    cryptocurrency=currency_name,
                    count_currency=count,
                )
                session.add(status)
                add_to_history(
                    session, user_id, operation_type, currency_name, count, answer.price
                )
                return Info.successful_operation.format(currency_name, count)

            user_status.count_currency = str(
                Decimal(user_status.count_currency) + Decimal(count)
            )
        else:
            if user_status is None:
                raise CustomError(Info.failed)
            if Decimal(user_status.count_currency) < Decimal(count):
                raise CustomError(Info.not_enough_cryptocurrency)
            user.money = str(
                Decimal(user.money) + Decimal(answer.price) * Decimal(count)
            )
            user_status.count_currency = str(
                Decimal(user_status.count_currency) - Decimal(count)
            )
            if Decimal(user_status.count_currency) == Decimal(0):
                session.query(Userstatus).filter(
                    Userstatus.user_id == user_id,
                    Userstatus.cryptocurrency == currency_name,
                ).delete()

        add_to_history(
            session, user_id, operation_type, currency_name, count, answer.price
        )

        return Info.successful_operation.format(
            currency_name, str(user_status.count_currency)
        )


def get_user_history(user_id: int) -> Any:
    with create_session() as session:
        article_info = {}
        index = 1
        for obj in session.query(History).filter(History.user_id == user_id):
            article_info[index] = {
                'operation_type': obj.operation_type,
                'currency_type': obj.currency_type,
                'count_currency': str(obj.count_currency),
                'currency_rate': str(obj.currency_rate),
                'datetime': str(obj.datetime),
            }
            index += 1

        myJSON = json.dumps(article_info)
        return myJSON


def add_new_currency(name: str, price: str) -> str:
    with create_session() as session:
        session.add(Cryptocurrency(name=name, price=price))
        return Info.successful_added_new_currency.format(name)


def get_all_currencies() -> str:
    with create_session() as session:
        answer = ''
        for obj in session.query(Cryptocurrency):
            answer += obj.name
            answer += '\n'
        return answer
