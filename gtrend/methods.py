from gtrend.model import *
import datetime

def add_transaction(session_id, agent_id, reference, receipt, amount, charges, transaction_type, created_at):
    new_transaction = Transaction(session_id=session_id, agent_id=agent_id, reference=reference, charges=charges, amount=amount, transaction_type=transaction_type, created_at=created_at)
    db.session.add(new_transaction)
    db.session.commit()
    return new_transaction

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

def get_user(phone):
    return User.query.filter_by(phone=phone).first()


def report(date=None):
    # if date:
    pass

def getCurrentDate():
    date = datetime.datetime.now()
    return date.strftime("%Y-%m-%d")

def getReceipt(t):
    # response  = f"END ******Receipt******\n"
    response  = f"END Receipt Number: {t.receipt}\n"
    response  += f"Client: {t.customer}\n"
    response  += f"Amount Paid: {t.amount}\n"
    response  += f"Charges: {t.charges}\n"
    response  += f"Total: {t.charges+t.amount}\n"
    response  += f"Reference: {t.reference}\n"
    response  += f"Date: {getCurrentDate()}\n"
    response  += f"powered by: Global Trend\n"
    return response

def getCharges(amount):
    if amount <= 500:
        return 30
    elif amount <= 1000:
        return 50
    elif amount <= 20000:
        return 100
    else:
        return 200

def getTransaction(reference):
    transaction = Transaction.query.filter(Transaction.reference.ilike(f'%{reference}%')).first()
    return transaction

def getCurrentTimestamp():
    timestamp = datetime.datetime.now().timestamp()
    return int(timestamp)