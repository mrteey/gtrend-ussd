
'''
api
--------------
'''
from flask import Blueprint, request, render_template, redirect, url_for
import requests

from gtrend import app
from gtrend.methods import add_session, update_session, get_session, get_user, add_transaction, getCurrentDate, getReceipt, getTransaction, getCharges, getCurrentTimestamp
from gtrend.marshmallow import TransactionSchema, UserSchema

api = Blueprint('api', __name__, url_prefix='/api')


api_base = app.config.get('API')
bearer = app.config.get('BEARER')
terminalId = app.config.get('TERMINALID')
endpoints = {'lookup':'/lookup', 'notification':'/notification'}

@api.route('auth', methods=['POST'])
def auth():
    phone = request.json.get('phone')
    pin = request.json.get('pin')
    user = get_user(phone)
    if user and user.is_verified(pin):
        schema = UserSchema()
        return schema.jsonify(user)
    return {'message':'invalid credentials', 'status':'failed'}

@api.route("/dispatch", methods=["POST"])
def dispatch():
    serviceCode = request.form.get('serviceCode')
    phoneNumber = request.form.get('phoneNumber')
    sessionId = request.form.get('sessionId')
    networkCode = request.form.get('networkCode')
    text = request.form.get('text')
    agent = get_user(phoneNumber)
    session = get_session(sessionId)
    if agent:
        if session:
            return globals()[session.stage](text, sessionId, phoneNumber)
        return start(sessionId=sessionId, phone=phoneNumber, name=agent.name)
    return 'END You are not authorized to use this service'

@api.route('confirm-reference', methods=['POST'])
def confirm():
    reference = request.json.get('reference')
    return getInvoice(reference)

@api.route('make-payment', methods=['POST'])
def make_payment():
    data = request.json
    agent = get_user(data.get('phone'))
    if agent and agent.is_verified(data.get('pin')):
        payment = pay(agent.name, data.get('reference'), data.get('amount'), data.get('customer'), data.get('description'))
        receipt = payment.get('billerReference')
        if receipt:
            transaction = add_transaction(None, agent.id, data.get('reference'), receipt, data.get('description'), data.get('customer'), data.get('amount'), data.get('charges'), data.get('transaction_type'), getCurrentDate())
        return payment
    return {'message':'invalid credentials', 'status':'failed'}

@api.route('generate-receipt', methods=['POST'])
def generate_receipt():
    reference = request.json.get('reference')
    schema = TransactionSchema()
    transaction = getTransaction(reference)
    return schema.jsonify(transaction)
                
def start(sessionId, phone, name):
    add_session(sessionId)
    response  = f"CON Welcome {name}\nPlease enter a transaction reference\n"
    return response

def getInvoice(reference):
    invoice = requests.get(api_base+endpoints.get('lookup'), headers={'Authorization':'bearer'f' {bearer}', 'TerminalId':terminalId}, params={"reference":reference, "type":"invoice"})
    invoice = invoice.json()
    return invoice

def confirmReference(_reference, sessionId, phone):
    _reference = _reference.split('*')[-1]
    _reference = _reference.strip().replace('IN', '')
    invoice = getInvoice(_reference)
    total = invoice.get("totalAmount")
    amount = invoice.get("outStandingAmount")
    customer = invoice.get('businessName')
    description=invoice.get('description')
    reference=invoice.get('reference')
    status = invoice.get("status")
    if status == 'false':
        transaction = getTransaction(_reference)
        if transaction:
            response = getReceipt(transaction)
        else:
            response  = f"CON Invalid reference, try again!"
    elif amount and amount > 0:
        response  = f"CON Client: {customer}\nAmount: {amount}\nCharges: {getCharges(amount)}\nPick an option to continue:\n"
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

def pay(agent, reference, amount, customer, description):
    data = {
            "AgentId":"GlobalTrend",
            "AgentName":agent,
            "reference": reference.replace('IN', ''),
            "Amount": amount,
            "Currency": "NGN",
            "type": 'invoice',
            "TransactionReference": getCurrentTimestamp(),
            "RetrievalReferenceNumber": f"IN{reference.replace('IN', '')}",
            "MaskedPAN": "MaskedPAN",
            "CardScheme": "CardScheme",
            "CustomerName": customer,
            "StatusCode": "200",
            "StatusDescription": description,
            "STAN": "STAN",
            "CardExpiry": "CardExpiry",
            "PaymentDate": getCurrentDate()
            }
    payment = requests.post(api_base+endpoints.get('notification'), headers={'Authorization':'bearer'f' {bearer}', 'TerminalId':terminalId}, json=data)
    return payment.json()

def makePayment(pin, sessionId, phone):
    session = get_session(sessionId)
    pin = pin.split('*')[-1]
    agent = get_user(phone=phone)
    if agent.is_verified(pin):
        payment = pay(agent.name, session.reference, session.customer, session.description)
        receipt = payment.get('billerReference')
        if receipt:
            transaction = add_transaction(session.id, agent.id, session.reference, receipt, session.description, session.customer, session.amount, session.charges, session.transaction_type, getCurrentDate())
            update_session(sessionId, "completed")
            response = getReceipt(transaction)
        else:
            response  = f"END Sorry we could not complete your transaction!"
    else:
        response  = f"CON Invalid pin, try again!"
    return response
