import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.processor_stripe_bank_account_token_create_request import ProcessorStripeBankAccountTokenCreateRequest
import datetime
import requests
import json


class plaid_connect(object):
    PLAID_CLIENT_ID = '622c9ce4f80bde0013a73bcb'
    PLAID_SECRET = '5b5c360f616105921c5e429720b7eb'

    def __init__(self):
        self.PUBLIC_TOKEN = None
        self.ACCESS_TOKEN = None
        # self.INSTITUTION = INSTITUTION_ID
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': plaid_connect.PLAID_CLIENT_ID,
                'secret': plaid_connect.PLAID_SECRET,
            }
        )

        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        # self.get_public_token_access()
        # self.get_access_token()

    def get_public_token_access(self, initial_products='', institution_id=''):
        institution_id = 'ins_3'
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[Products('transactions'), Products('auth')]
        )
        pt_response = self.client.sandbox_public_token_create(pt_request)
        public_token = pt_response['public_token']
        self.PUBLIC_TOKEN = public_token

    def get_access_token(self):
        exchange_request = ItemPublicTokenExchangeRequest(public_token=self.PUBLIC_TOKEN)
        exchange_token_response = self.client.item_public_token_exchange(exchange_request)
        access_token = exchange_token_response['access_token']
        self.ACCESS_TOKEN = access_token

    def auth(self):
        request = AuthGetRequest(access_token=self.ACCESS_TOKEN)
        response = self.client.auth_get(request)
        numbers = response['numbers']
        return numbers

    def get_transaction(self):
        url = 'https://sandbox.plaid.com/transactions/get'

        # if not self.ACCESS_TOKEN:
        self.get_public_token_access()
        self.get_access_token()

        data = {
            "client_id": plaid_connect.PLAID_CLIENT_ID,
            "secret": plaid_connect.PLAID_SECRET,
            "access_token": self.ACCESS_TOKEN,
            "start_date": "2021-01-01",
            "end_date": "2021-12-10"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=data, headers=headers)
        transactions = []
        print(response.json())
        if response.status_code == 200:
            transactions = response.json()['transactions']
        return transactions

        # request = TransactionsGetRequest(
        #     access_token=self.ACCESS_TOKEN,
        #     start_date=datetime.date(2021, 1, 1),
        #     end_date=datetime.date(2021, 12, 10),
        #     # options=TransactionsGetRequestOptions()
        #     # options=TransactionsGetRequestOptions()
        # )
        # response = self.client.transactions_get(request)
        # transactions = response['transactions']
        # return transactions

    def get_accounts(self):
        request = AccountsGetRequest(access_token=self.ACCESS_TOKEN)
        response = self.client.accounts_get(request)
        accounts = response['accounts']
        return accounts

    def get_institutions(self, count=100, offset=0):
        request = InstitutionsGetRequest(
            country_codes=[CountryCode('US')],
            count=count,
            offset=offset
        )
        response = self.client.institutions_get(request)
        institutions = response['institutions']
        return institutions
