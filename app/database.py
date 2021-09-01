from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionClass
from sqlalchemy.util.compat import contextmanager

engine = sa.create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = 'users_base'
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String(20), unique=True)
    money = sa.Column(sa.String)


class Cryptocurrency(Base):  # type: ignore
    __tablename__ = 'cryptocurrency'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(20), unique=True)
    price = sa.Column(sa.String)


class Userstatus(Base):  # type: ignore
    __tablename__ = 'userstatus'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    cryptocurrency = sa.Column(
        sa.String(20), sa.ForeignKey(Cryptocurrency.id), nullable=False, index=True
    )
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'cryptocurrency', name='_user_currency_uc'),
    )
    count_currency = sa.Column(sa.String)


class History(Base):  # type: ignore
    __tablename__ = 'history'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    operation_type = sa.Column(sa.String(5))
    currency_type = sa.Column(sa.String(20))
    count_currency = sa.Column(sa.String)
    currency_rate = sa.Column(sa.String)
    datetime = sa.Column(sa.DATETIME)


Base.metadata.create_all(engine)


@contextmanager
def create_session(**kwargs: Any) -> SessionClass:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()
