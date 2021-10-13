
'''
Marshmallow
--------------
'''

from gtrend.model import *

from flask_marshmallow import Marshmallow

from gtrend import app

ma = Marshmallow(app)

# Sample Marshmallow Schemas, us this method to make yours

class TransactionSchema(ma.SQLAlchemyAutoSchema):
   class Meta:
       model = Transaction
   include_fk = True #This includes foreignkeys

class TransactionCustomSchema(ma.Schema):
   class Meta:
       fields = ("total", "charges", "transactions")

class UserSchema(ma.SQLAlchemyAutoSchema):
   class Meta:
       model = User
   include_fk = True #This includes foreignkeys
#    books = ma.Nested("BookSchema", many=True)