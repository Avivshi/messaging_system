import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from db import db
from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, TokenRefresh, UserLogout
from resources.message import AllMessages, InboxMessages, SentMessages, ReadMessage, UnreadMessages, SendMessage, DeleteReceivedMessage, DeleteSentMessage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)

"""
JWT related configuration. The following functions includes:
1) add claims to each jwt
2) customize the token expired error message 
"""
app.config['JWT_SECRET_KEY'] = 'SECRET_KEY'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401

# JWT configuration ends


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

api.add_resource(AllMessages, "/messages")
api.add_resource(InboxMessages, "/messages/inbox")
api.add_resource(SentMessages, "/messages/sent")
api.add_resource(UnreadMessages, "/messages/inbox/unread")
api.add_resource(ReadMessage, "/messages/inbox/read")
api.add_resource(SendMessage, "/messages/send")
api.add_resource(DeleteReceivedMessage, "/messages/inbox/<int:message_id>")
api.add_resource(DeleteSentMessage, "/messages/sent/<int:message_id>")


if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
