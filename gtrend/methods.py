from gtrend.model import *
import datetime
from sqlalchemy import func, or_, and_

def add_transaction(session_id, agent_id, reference, receipt, description, customer, amount, charges, transaction_type, treference, tid, created_at):
    new_transaction = Transaction(session_id=session_id, agent_id=agent_id, receipt=receipt, description=description, customer=customer, reference=reference, charges=charges, amount=amount, transaction_type=transaction_type, treference=treference, tid=tid, created_at=created_at)
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

def get_user(phone=None, id=None):
    if phone:
        return User.query.filter(User.phone.ilike(f'%{phone[1:]}%')).first()
    return User.query.filter(User.id==id).first()


def report(date=None):
    # if date:
    pass

def getCurrentDate(with_time=False):
    date = datetime.datetime.now()
    if with_time:
        return date.strftime("%Y-%m-%d - %H:%M")
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
    elif amount <= 10000:
        return 100
    elif amount <= 20000:
        return 150
    elif amount <= 200000:
        return 200
    else:
        return 300

def getTransaction(reference):
    # reference can either be invoice reference or receipt number
    transaction = Transaction.query.filter(or_(Transaction.reference.ilike(f'%{reference}%'), Transaction.receipt.ilike(f'%{reference}%'))).first()
    return transaction

def getCurrentTimestamp():
    timestamp = datetime.datetime.now().timestamp()
    return int(timestamp)

def valid_number(number, country_code='+234'):
    number = str(number.replace(' ', ''))
    if number and number[1:].isdigit():
        if number.startswith('0') and len(number) == 11:
            #e.g. 07012345678 returns +2347012345678
            return country_code+number[1:]
        elif not number.startswith('0') and len(number) == 10:
            #e.g. 7012345678 returns +2347012345678
            return country_code+number
        elif number.startswith('234') and len(number) == 13:
            #e.g. 2347012345678 returns +2347012345678
            return country_code+number[3:]
        elif number.startswith(country_code) and len(number) == 14:
            #e.g. +2347012345678 returns +2347012345678
            return number
    return None

def getReport(agent_id=0, date_from=0, date_to=0):
    _report = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0).label('total'), db.func.coalesce(db.func.sum(Transaction.charges), 0).label('charges'), db.func.count(Transaction.id).label('transactions')).filter(Transaction.created_at >= date_from, Transaction.created_at <= date_to)
    report = Transaction.query.filter(Transaction.created_at >= date_from, Transaction.created_at <= date_to)
    if agent_id:
        _report = _report.filter(Transaction.agent_id==agent_id)
        report = report.filter(Transaction.agent_id==agent_id)
    _report = _report.first()
    report = report.all()
    return _report, report

def getAgents():
    agents = User.query.filter_by(is_agent=True).all()
    return agents

def addAgent(name='', phone='', password=''):
    if valid_number(number=phone):
        try:
            agent = User(name=name, phone=phone, is_agent=True)
            db.session.add(agent)
            agent.set_password(password)
            db.session.commit()
            return agent
        except:
            db.session.rollback()