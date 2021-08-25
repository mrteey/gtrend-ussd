
'''
MODEL
--------------
'''
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph

db = SQLAlchemy()

#Model Sample
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    # admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    password = db.Column(db.String)
    def set_password(self, password):
        self.password = gph(password)
        return True
    def is_verified(self, password):
        return cph(self.password, password)
        
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)

class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String)
    stage = db.Column(db.String)
    customer = db.Column(db.String)
    description = db.Column(db.String)
    reference = db.Column(db.String)
    amount = db.Column(db.Integer)
    charges = db.Column(db.Integer)
    transaction_type = db.Column(db.String)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    amount = db.Column(db.Integer)
    charges = db.Column(db.Integer)
    transaction_type = db.Column(db.String)
    created_at = db.Column(db.String)
    reference = db.Column(db.String)