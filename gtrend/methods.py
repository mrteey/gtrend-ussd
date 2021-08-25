from gtrend.model import *

def add_transaction(session_id, agent_id, reference, amount, transaction_type, created_at):
    new_session = Transaction(session_id=session_id, agent_id=agent_id, reference=reference, amount=amount, transaction_type=transaction_type, created_at=created_at)
    db.session.add(new_session)
    db.session.commit()
    return True

def add_session(session_id):
    new_session = Sessions(session_id=session_id, stage='confirmReference')
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