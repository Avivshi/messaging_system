from db import db
import datetime
from sqlalchemy import or_


class MessageModel(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String())
    receiver = db.Column(db.String())
    message = db.Column(db.String())
    subject = db.Column(db.String())
    creation_date = db.Column(db.String())
    is_read = db.Column(db.Boolean())

    def __init__(self, sender, receiver, message, subject):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.subject = subject
        self.creation_date = f"{datetime.datetime.now()}"
        self.is_read = False

    def json(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'creation_date': self.creation_date,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
        }

    @classmethod
    def read_message(cls, username):
        msg = cls.query.filter_by(is_read=False, receiver=username).first()
        if msg:
            msg.is_read = True
            db.session.commit()
            return msg.json()
        return {"message": "There are no unread messages"}

    @classmethod
    def all_messages(cls, username):
        messages = [message.json() for message in cls.query.filter(or_(MessageModel.sender==username, MessageModel.receiver==username)).all()]
        return messages if messages else {"messages": "No messages"}

    @classmethod
    def inbox_messages(cls, username):
        inbox = [message.json() for message in cls.query.filter_by(receiver=username).all()]
        return inbox if inbox else {"inbox": "Your inbox is empty"}

    @classmethod
    def sent_messages(cls, username):
        sent = [message.json() for message in cls.query.filter_by(sender=username).all()]
        return sent if sent else {"sent": "You have not yet sent any messages"}

    @classmethod
    def unread_messages(cls, username):
        unread = [message.json() for message in cls.query.filter_by(is_read=False, receiver=username).all()]
        return unread if unread else {"message": "There are no unread messages"}
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
