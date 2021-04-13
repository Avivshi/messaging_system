from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import UserModel
from models.message import MessageModel


_message_parser = reqparse.RequestParser()
_message_parser.add_argument('receiver',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_message_parser.add_argument('subject',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

_message_parser.add_argument('message',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )


class AllMessages(Resource):
    @jwt_required
    def get(self):
        return {"messages": MessageModel.all_messages(UserModel.find_by_id(get_jwt_identity()).username)}


class InboxMessages(Resource):
    @jwt_required
    def get(self):
        return {"sent_messages": MessageModel.inbox_messages(UserModel.find_by_id(get_jwt_identity()).username)}


class SentMessages(Resource):
    @jwt_required
    def get(self):
        return {"sent_messages": MessageModel.sent_messages(UserModel.find_by_id(get_jwt_identity()).username)}


class ReadMessage(Resource):
    @jwt_required
    def get(self):
        message = MessageModel.read_message(UserModel.find_by_id(get_jwt_identity()).username)
        return message


class UnreadMessages(Resource):
    @jwt_required
    def get(self):
        return {"unread_messages": MessageModel.unread_messages(UserModel.find_by_id(get_jwt_identity()).username)}


class SendMessage(Resource):
    @jwt_required
    def post(self):
        data = _message_parser.parse_args()
        data['sender']= UserModel.find_by_id(get_jwt_identity()).username
        if UserModel.find_by_username(data['receiver']) is None:
            return {"error": f"The user {data['receiver']} does not exist."}
        message = MessageModel(data['sender'], data['receiver'], data['message'], data['subject'])
        message.save_to_db()
        return message.json()


class DeleteReceivedMessage(Resource):
    @jwt_required
    def delete(self, message_id):
        message = MessageModel.find_by_id(message_id)
        if message:
            if message.receiver == UserModel.find_by_id(get_jwt_identity()).username:
                message.delete_from_db()
                return {"info": "Message deleted!"}
        return {"error": "Message cannot be found in your inbox"}


class DeleteSentMessage(Resource):
    @jwt_required
    def delete(self, message_id):
        message = MessageModel.find_by_id(message_id)
        if message:
            if message.sender == UserModel.find_by_id(get_jwt_identity()).username:
                message.delete_from_db()
                return {"info": "Message deleted!"}
        return {"error": "Message cannot be found in your sent messages"}