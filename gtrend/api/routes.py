
'''
api
--------------
'''
from flask import Blueprint, request, render_template, redirect, url_for
import requests, datetime

from gtrend.methods import add_session, update_session, get_session, get_agent, get_user, add_transaction
from gtrend import app

api = Blueprint('api', __name__, url_prefix='/api')


api_base = app.config.get('API')
bearer = app.config.get('BEARER')
terminalId = app.config.get('TERMINALID')
endpoints = {'lookup':'/lookup', 'notification':'/notification'}

@api.route("/dispatch", methods=["POST"])
def dispatch():
    serviceCode = request.form.get('serviceCode')
    phoneNumber = request.form.get('phoneNumber')
    sessionId = request.form.get('sessionId')
    networkCode = request.form.get('networkCode')
    text = request.form.get('text')
    agent = get_agent(phoneNumber)
    session = get_session(sessionId)
    if agent:
        if session:
            return globals()[session.stage](text, sessionId, phoneNumber)
        return start(sessionId=sessionId, phone=phoneNumber, name=agent.name)
    return 'END You are not authorized to use this service'
                
def start(sessionId, phone, name):
    add_session(sessionId)
    response  = f"CON Welcome {name}\nPlease enter a transaction reference\n"
    return response
    
def confirmReference(reference, sessionId, phone):
    reference = reference.split('*')[-1]
    reference = reference.strip().replace('IN', '')
    invoice = requests.get(api_base+endpoints.get('lookup'), headers={'Authorization':'bearer'f' {bearer}', 'TerminalId':terminalId}, params={"reference":reference, "type":"invoice"})
    invoice = invoice.json()
    total = invoice.get("totalAmount")
    amount = invoice.get("outStandingAmount")
    customer = invoice.get('businessName')
    description=invoice.get('description')
    reference=invoice.get('reference')
    status = invoice.get("status")
    if status == 'false':
        response  = f"CON Invalid reference, try again!"
    elif amount and amount > 0:
        response  = f"CON Client: {customer}\nAmount: {amount}\nDescription:{description}\nCharges: {getCharges(amount)}\nPick an option to continue:\n"
        response += "1. Purchase\n"
        response += "2. Deposit\n"
        response += "3. Final Pay\n"
        update_session(sessionId, 'choice', customer=customer, description=description, reference=reference, amount=amount, charges=getCharges(amount))
    else:
        response  = f"END This reference has already been paid"
    return response

def choice(text, sessionId, phone):
    if text.split('*')[-1] == '1':
        update_session(sessionId, 'makePayment', transaction_type='purchase')
        return finalpay(None, sessionId, phone)
    elif text.split('*')[-1] == '2':
        update_session(sessionId, 'makePayment', transaction_type='deposit')
        return deposit(text, sessionId, phone)
    elif text.split('*')[-1] == '3':
        update_session(sessionId, 'makePayment', transaction_type='finalpay')
        return finalpay(None, sessionId, phone)
    else:
        return choice(text, sessionId, phone)

def finalpay(amount=None, sessionId=None, phone=None):
    if amount:
        update_session(sessionId, 'makePayment', amount=int(amount.split('*')[-1]))
    update_session(sessionId, 'makePayment')
    session = get_session(sessionId)
    response  = f"CON Please enter your pin to pay {session.amount}:"
    return response

def deposit(text, sessionId, phone):
    session = get_session(sessionId)
    response  = f"CON Original Amount: {session.amount}\nPlease enter amount to pay:"
    update_session(sessionId, 'finalpay')
    return response

def makePayment(pin, sessionId, phone):
    session = get_session(sessionId)
    pin = pin.split('*')[-1]
    agent = get_agent(phone=phone)
    user = get_user(agent.id)
    if user.is_verified(pin):
        data = {
            "AgentId":f"{agent.id}",
            "AgentName":agent.name,
            "reference": session.reference.replace('IN', ''),
            "Amount": session.amount,
            "Currency": "NGN",
            "type": 'invoice',
            "TransactionReference": session.reference,
            "RetrievalReferenceNumber": f"IN{session.reference}",
            "MaskedPAN": "MaskedPAN",
            "CardScheme": "CardScheme",
            "CustomerName": session.customer,
            "StatusCode": "200",
            "StatusDescription": session.description,
            "STAN": "STAN",
            "CardExpiry": "CardExpiry",
            "PaymentDate": get_current_date()
            }
        payment = requests.post(api_base+endpoints.get('notification'), headers={'Authorization':'bearer'f' {bearer}', 'TerminalId':terminalId}, json=data)
        payment = payment.json()
        if payment.get('billerReference'):
            add_transaction(session.id, agent.id, session.reference, session.amount, session.charges, session.transaction_type, get_current_date())
            update_session(sessionId, "completed")
            response  = f"END ******Receipt******\n"
            response  += f"Client: {session.customer}\n"
            response  += f"Amount Paid: {session.amount}\n"
            response  += f"Charges: {session.charges}\n"
            response  += f"Total: {session.charges+session.amount}\n"
            response  += f"Reference: {session.reference}\n"
            response  += f"Date: {get_current_date()}\n"
            response  += f"powered by: Global Trend\n"
        else:
            response  = f"END Sorry we could not complete your transaction!"
    else:
        response  = f"CON Invalid pin, try again!"
    return response

def report(date=None):
    # if date:
    pass

def get_current_date():
    date = datetime.datetime.now()
    return date.strftime("%Y-%m-%d")

def getCharges(amount):
    if amount <= 500:
        return 30
    elif amount <= 1000:
        return 50
    elif amount <= 20000:
        return 100
    else:
        return 200