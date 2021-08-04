from gtrend.model import *

def add_session(session_id):
    new_session = Sessions(session_id=session_id, stage='choice')
    db.session.add(new_session)
    db.session.commit()
    return True

def update_session(session_id, stage, **kwargs):
    session = Sessions.query.filter_by(session_id=session_id).first()
    session.stage = stage
    if kwargs:
        Sessions.query.filter_by(session_id=session_id).update(kwargs)
    db.session.commit()
    return True

def get_session(session_id):
    return Sessions.query.filter_by(session_id=session_id).first()

def get_agent(phone):
    return Agent.query.filter_by(phone=phone).first()

def get_user(agent_id):
    return User.query.filter_by(agent_id=agent_id).first()