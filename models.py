from base import engine, session

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from aiogram.types import Message
from datetime import datetime, timedelta
from prettytable import PrettyTable

Base = declarative_base()


class UserMessages(Base):
    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", foreign_keys=[user_id])
    role = Column(String)
    message = Column(String)
    datetime = Column(DateTime, default=datetime.now().date)

    def __init__(self, user, role, message_text):
        self.user = user
        self.role = role
        self.message = message_text

    @staticmethod
    def create(user, role, message_text):
        user_message = UserMessages(user, role, message_text)
        session.add(user_message)
        session.commit()

        user_messages = session.query(UserMessages).filter_by(user_id=user.id).count()
        if user_messages > 7:
            session.query(UserMessages).filter_by(user_id=user.id).order_by(UserMessages.datetime).first().delete()

        return user_message

    def delete(self):
        session.delete(self)
        session.commit()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    name = Column(String)
    username = Column(String)
    language_code = Column(String)
    datetime = Column(DateTime, default=datetime.now().date)

    def __init__(self, chat_id, name, username, language_code):
        self.chat_id = chat_id
        self.name = name
        self.username = username
        self.language_code = language_code

    @staticmethod
    def create(chat_id: int, name: str, username: str, language_code: str):
        user = User(chat_id, name, username, language_code)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def get_by_chat_id(chat_id: int):
        return session.query(User).filter_by(chat_id=chat_id).first()

    @staticmethod
    def get_or_create(message: Message):
        chat_id = message.chat.id
        name = message.from_user.full_name
        username = message.from_user.username
        language_code = message.from_user.language_code

        user = User.get_by_chat_id(chat_id)
        if user is None:
            user = User.create(chat_id, name, username, language_code)
        return user

    def add_message(self, message: str, role: str):
        UserMessages.create(self, role, message)
        return True

    def get_messages(self):
        res = []
        messages = session.query(UserMessages).filter_by(user_id=self.id).order_by(UserMessages.datetime.desc()).all()
        for message in messages:
            res.append({"role": "user", "content": message.message[:250]})
        return res


class Statistic(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    requests = Column(Integer)
    requests_true = Column(Integer)

    def __init__(self, date):
        self.date = date
        self.requests = 0
        self.requests_true = 0

    @staticmethod
    def get_stat_by_week():
        res = "Всього користвувачів: "
        res += str(session.query(User).count())
        res += "\n---Статистика за неділю---\n"
        th = ["D", "U", "Req", "True"]

        table = PrettyTable(th)
        date = datetime.now().date() - timedelta(days=7)
        stats = session.query(Statistic).filter(func.DATE(Statistic.date) > date).all()

        stats.reverse()

        for stat in stats:
            users = session.query(User).filter(func.DATE(User.datetime) == func.DATE(stat.date)).count()
            table.add_row([stat.date.strftime('%m.%d'), users, stat.requests, stat.requests_true])

        return table

    @staticmethod
    def get_or_create():
        date = datetime.now().date()
        stat = session.query(Statistic).filter(func.DATE(Statistic.date) == date).first()
        if stat is None:
            stat = Statistic(date)
            session.add(stat)
            session.commit()
        return stat

    @staticmethod
    def add_request():
        stat = Statistic.get_or_create()
        stat.requests += 1
        session.commit()

    @staticmethod
    def add_request_true():
        stat = Statistic.get_or_create()
        stat.requests_true += 1
        session.commit()


Base.metadata.create_all(engine)
