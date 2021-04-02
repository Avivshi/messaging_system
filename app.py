from flask import Flask, request
from flask_restful import Api, Resource
from datetime import date

app = Flask(__name__)
api = Api(app)


messages = []


class MessagesInbox(Resource):
    def get(self, owner):
        owner_messages = [msg for msg in messages if msg['receiver'] == owner]
        return {'messages': owner_messages}, 200 if owner_messages else 404


class ReadMessage(Resource):
    def get(self, owner):
        for message in messages:
            if message['receiver'] == owner and message['is_read'] is False:
                message['is_read'] = True
                return message
        return {'info': "You read all messages"}


class UnreadMessages(Resource):
    def get(self, owner):
        owner_unread_messages = [msg for msg in messages if msg['receiver'] == owner and msg['is_read'] is False]
        return {'messages': owner_unread_messages}, 200 if owner_unread_messages else 404


class DeleteAsReceiver(Resource):
    def delete(self, owner, subject):
        global messages
        messages = [msg for msg in messages if msg['subject'] != subject and msg['receiver'] != owner]
        return {'info': "message deleted"}


class MessagesSent(Resource):
    def get(self, owner):
        owner_messages = [msg for msg in messages if msg['sender'] == owner]
        return {'messages': owner_messages}, 200 if owner_messages else 404

    def post(self, owner):
        data = request.get_json()
        message = {
            'sender': owner,
            'receiver': data['receiver'],
            "message": data['message'],
            "subject": data['subject'],
            "creation_date": date.today().strftime("%B %d, %Y"),
            "is_read": False
        }
        messages.append(message)
        return message, 201


class DeleteAsSender(Resource):
    def delete(self, owner, subject):
        global messages
        messages = [msg for msg in messages if msg['subject'] != subject and msg['sender'] != owner]
        return {'info': "message deleted"}


api.add_resource(MessagesInbox, '/messages/<string:owner>/inbox')
api.add_resource(ReadMessage, '/messages/<string:owner>/inbox/read')
api.add_resource(UnreadMessages, '/messages/<string:owner>/inbox/unreadMessages')
api.add_resource(DeleteAsReceiver, '/messages/<string:owner>/inbox/<string:subject>')

api.add_resource(MessagesSent, '/messages/<string:owner>/sent')
api.add_resource(DeleteAsSender, '/messages/<string:owner>/sent/<string:subject>')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
