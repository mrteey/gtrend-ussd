
'''
api
--------------
'''
from flask import Blueprint, request, render_template, redirect, url_for
import requests, datetime

from gtrend.methods import add_session, update_session, get_session, get_agent, get_user

api = Blueprint('api', __name__, url_prefix='/api')


api_base = "https://ecashiers.healthinabox.ng/api/pay"
bearer = """lQOsBFth1NYBCACMUr78x3Zun0xdI3640sUjW/j36KOulTmsD25efkGiVNRztxMfmFjtllf+ZV0/eNbqxD9cdCJg/SJB3JFKB4eHecDl+sqL1POisuggxAcTq/5WywwT5P5h/fEDryJoy78APKUIy6IbrzAups5Uz8ZH04vVt+AEU7g7A/YrdeEZotICZbF7KiCQNbGGUEk8fXJ7kms8adl5ZxbwEZEkhyy2rx9bh1cFZB8nhezN+KLJrXKCjG7xQsyBzYy7QHifdwY2UH9VlbHF1CNk0U6j8S4G/P0w09Buxe1wFAy3v/p0zVo5wu7Gb7PgXpPu98lfUQAcWiGLFOs8WBC+4sNGBMB1ABEBAAH/AwMCJGpT+Fdo+npgS0sZFhAzSp4Ej9RrsPw7tUm94JScfBs49pg4eqzhUyt5vcU7yDPIi+kRnDYO6lWyLksH++as/3EUcAGC/4/CYoIOem90T/Il3k4Qkqqah+JVlp/Ut9HiW1tgXqxGMkvEDbp+9hJK83KXOs8ImLV3Eca/WbSiiWPcGpUCUPdGs2CfJWrSrzxa6iHmC4kM/PHauctuXPqzX2UKcnQ+8CLlUNFyk4k/tK/1LdigFrsB8jr1T+pVQ4d2BrQ18ZyBUZgw9QZjIWJlldvSh3p9Q2yK0g7vkcHVHW4XDL8iy54ko3lYDLoHJDB8PGmDH6XxLKjl+eRdi8iNsVLrYpMGhFvZYQM6q1Pai5ihbU2T4CsmqEKFfc7yQc4H9w65p4ImrVmD4O/0SwpCPG+JCot73FfdLbytlRMmYFclRVeN+3mTbj3+wXGeXgZm5S7rlwyzoR28i+EUzPGW//NY4SaaOeoZ4KCwdtxBa/mmvmY1Ze+igY37FKdj1J4HodwcXLWQpgbpXwRDyrY9X19U3Cg7wOjumQXInetz15WXhcxm891bPvYAQ3RKHHtlM5Cw6oFPHjf0SfjwPGCbyvfqFcupw206R6B0hOTFBncwqsFuiN2Q//KADNVTDbG1ZTAjbw6T6dgHvcyvGjA1ZUIlC09he4Oaq1IpfC1D8vLjTPCa1FXAKOKMzP6kPuyAVH4KkMZ/Dh6O1mADSJEjOAuTvR15yqn0PwIHJ2QVsZR9+IriKZxsIxZdyioP8Pabg7mwwSj3bMGRVE+z4E3XKYAkjwBcDOJ/GJfX5k/AiUxGFdg6hAkyDyty6W7NsmjEaOU6EuWdSRiaVytnmRUwNFHtDtbQ0V8bg90x0aMBTldloXkTTHHXaKyYjrQUZXplbWUubWFya0BnbWFpbC5jb22JARwEEAECAAYFAlth1NYACgkQFcVxLxSLZ9S86Qf/aK5X9Kg7UlpjZGL1SXLiHla7BV/JEP1r/TYhKuhUxGmU4PxqBOTokIKQdxzVKdoxdWv3QXvUBGRdM/TpeymE7DT3JYMBvw1O/XhWZFV5r+O5qTFWMmAAfq/8HlEcDtr46hZBPNGNRRTu8qN+jxiWqXbnLumSGwROQDznl+F4g7s4Vz4piuubyygllJgugHXk5bDUdEZlRmUDecDwAbL79Nzc7wmbugPL0iLU+Us8suGWP/iV87xrIoygFXQn2EhYNULqxfM8FXtpLWyRKHyDJxkNNktHkoRr1CGBJWLJo75P7HQUvIB5I7fJ6igihMmHtL6NCSfiyG5L4v09WTG6zQ===8P/6"""
terminalId = "MM_TEST"
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
    response  = f"CON Welcome {name}\nWhat do you want yo do? \n"
    response += "1. Make Payment \n"
    response += "2. Confirm Deposit"
    return response
    

def choice(text, sessionId, phone):
    if text == '1':
        return getReference(text, sessionId, phone)
    elif text == '2':
        return getTeller(text, sessionId, phone)
    else:
        return choice(text, sessionId)

def getReference(text, sessionId, phone):
    response  = "CON Please enter transaction reference"
    update_session(sessionId, 'confirmReference')
    return response

def getTeller(text, sessionId, phone):
    response  = "CON Please enter teller number"
    update_session(sessionId, 'confirmTeller')
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
        response  = f"CON Client: {customer}\nAmount: {amount}\nDescription:{description}\nEnter your pin to continue"
        update_session(sessionId, 'makePayment', customer=customer, description=description, reference=reference, amount=amount)
    else:
        response  = f"END This reference has already been paid"
    return response

def makePayment(pin, sessionId, phone):
    session = get_session(sessionId)
    pin = pin.split('*')[-1]
    agent = get_agent(phone=phone)
    user = get_user(agent.id)
    if user.is_verified(pin):
        data = {
            "AgentId":agent.id,
            "AgentName":agent.name,
            "reference": session.reference,
            "Amount": session.amount,
            "Currency": "NGN",
            "type": "Finalpay",
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
        print(payment)
        update_session(sessionId, "completed")
        response  = f"END Amount paid successfully!"
    else:
        response  = f"CON Invalid pin, try again!"
    return response

def confirmTeller(teller, sessionId, phone):
    teller = teller.split('*')[-1]
    update_session(sessionId, "completed")
    return "END Deposit confirmed successfully!"

def get_current_date():
    date = datetime.datetime.now()
    return date.strftime("%Y-%m-%d")

def makeTransfer(amount, bank, account):
    return True