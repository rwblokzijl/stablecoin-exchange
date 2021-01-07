from stablecoin.ui.ui import UI
from stablecoin.stablecoin import StablecoinInteractor
from stablecoin.transaction import Transaction

from aiohttp import web

from abc import ABC
from copy import copy

from ipv8.attestation.trustchain.block import TrustChainBlock, ValidationResult
from ipv8.attestation.trustchain.listener import BlockListener
from ipv8.REST.rest_manager import RESTManager, cors_middleware
from ipv8.keyvault.crypto import ECCrypto
from ipv8.peer import Peer

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec

from ipv8.REST.base_endpoint import BaseEndpoint, Response

from binascii import hexlify, unhexlify

INITIAL_BALANCE = 100


class APIEndpoint(BaseEndpoint):

    def __init__(self):
        super(APIEndpoint, self).__init__()
        self.trustchain = None

    def initialize(self, session):
        super(APIEndpoint, self).initialize(session)#.blockchain.ipv8)
        self.stablecoin_interactor = session
        # self.trustchain = session.get_overlay(MyTrustChainCommunity)

    def setup_routes(self):
        self.app.add_routes([

            #"Creation"
            # Step 1 -> returns info to connect to gateway over ipv8
            web.post( '/exchange/e2t/initiate',         self.REST_CREATE_initiate),
            # Step 2 -> user connects through ipv8 to register its node and address
            # Step 3 -> returns the payment link to the user
            web.post( '/exchange/e2t/start_payment',    self.REST_CREATE_start_payment),
            # Step 4 -> triggers_payout
            web.post( '/exchange/e2t/finish_payment',   self.REST_CREATE_finish_payment),

            #"Destruction"
            # Step 1 -> returns: wallet_address and payment id to send money to with trustchain ipv8
            web.post( '/exchange/t2e/initiate',         self.REST_DESTROY_initiate),
            # Step 2 -> user connects through ipv8 and sends the funds providing the payment id

            #"Other"
            #"exchange rates"
            web.get(  '/exchange/e2t/rate',    self.exchange_rate_euro_to_token),
            web.get(  '/exchange/t2e/rate',    self.exchange_rate_token_to_euro),
            #"get payment status"
            web.get(  '/exchange/status',     self.exchange_status),

            #"FOR TESTING"
            web.post( '/exchange/complete', self.complete_payment), #tested
        ])

    def get_status_dict(self, t):
        transaction = self.clean_transaction_status(copy(t.data)) #copy

        return {
            "status":                   transaction['status'],
            "status_text":              transaction['status_text'],
            "created":                  transaction['created_on'],
            "payment_amount":           transaction['amount'],
            "payout_amount":            transaction['payout_amount'],
            "payment_currency":         transaction['payment_currency'],
            "payout_currency":          transaction['payout_currency'],
            "payment_id":               transaction['payment_id'],

            "gateway_connection_data":  transaction.get('gateway_connection_data', None),

            "payment_connection_data":  transaction.get('payment_connection_data', None),
            "payment_started_on":       transaction.get('payment_started_on', None),

            "payment_transaction_data": transaction.get('payment_transaction_data', None),
            "payment_confirmed_on":     transaction.get('payment_confirmed_on', None),

            "payout_connection_data":   transaction.get('payout_connection_data', None),
            "payout_transaction_data":  transaction.get('payout_transaction_data', None),
            "payout_done_on":           transaction.get('payout_done_on', None),
            }


    "Creation"
    # Step 1 -> returns info to connect to gateway over ipv8
    async def REST_CREATE_initiate(self, request):
        data = dict(await request.json())

        collatoral_cent   = self.validate_euro_to_token_request_collatoral(data)

        t = self.stablecoin_interactor.CREATE_initiate(collatoral_cent)

        response = self.get_status_dict(t)

        return web.json_response(response)

    # Step 2 -> user connects through ipv8 to register its node and address
    # Over trustchain

    # Step 3 -> returns the payment link to the user
    async def REST_CREATE_start_payment(self, request):

        data = dict(await request.json())

        if "payment_id" not in data:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")
        payment_id = data["payment_id"]

        transaction = self.stablecoin_interactor.CREATE_start_payment(payment_id)

        if not transaction:
            raise web.HTTPNotFound(reason="Transaction not found")

        response = self.get_status_dict(transaction)

        return web.json_response(response)

    # Step 4 -> triggers_payout
    async def REST_CREATE_finish_payment(self, request):
        data = dict(await request.json())

        if "payment_id" not in data:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")
        payment_id = data["payment_id"]

        transaction = self.stablecoin_interactor.CREATE_finish_payment(payment_id)

        if not transaction:
            raise web.HTTPNotFound(reason="Transaction not found")

        response = self.get_status_dict(transaction)

        return web.json_response(response)

    "Destruction"
    # Step 1 -> returns: wallet_address and payment id to send money to with trustchain ipv8
    async def REST_DESTROY_initiate(self, request):
        data = dict(await request.json())

        amount  = self.validate_token_to_euro_token_amount(data)
        iban    = self.validate_token_to_euro_iban(data)

        transaction = self.stablecoin_interactor.DESTROY_initiate(amount, iban)

        response = self.get_status_dict(transaction)

        return web.json_response(response)

    # Step 2 -> user connects through ipv8 and sends the funds providing the payment id
    # Over trustchain


    " Test functions "
    async def complete_payment(self, request):
        data = dict(await request.json())
        if "payment_id" not in data:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")
        if "counterparty" not in data:
            raise web.HTTPBadRequest(reason="Missing 'counterparty'")
        status = self.stablecoin_interactor.complete_payment(data["payment_id"], data["counterparty"])

        if not status:
            raise web.HTTPNotFound(reason="Transaction not found")

        if status:
            return web.json_response()
        else:
            raise web.HTTPBadRequest(reason="Coundn't complete the transaction")

    "Exchange E->T"
    # Get exchange rate
    async def exchange_rate_euro_to_token(self, request):
        base = request.query.get("base", 100)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stablecoin_interactor.get_exchange_rate_col_to_tok(base)
        return web.json_response({"eur": base, "token": ans})

    # Start Creation transaction
    async def exchange_euro_to_token(self, request):
        data = dict(await request.json())

        collatoral_cent   = self.validate_euro_to_token_request_collatoral(data)
        dest_wallet       = self.validate_euro_to_token_destination_address(data)
        temp_counterparty = data.get("counterparty", None)

        payment_data = self.start_creation(collatoral_cent, dest_wallet, temp_counterparty)

        return web.json_response(payment_data)

    # Get info on existing transaction
    async def exchange_status(self, request):
        if "payment_id" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")

        payment_id = request.query["payment_id"]

        transaction = self.stablecoin_interactor.get_transaction(payment_id)

        if not transaction:
            raise web.HTTPNotFound(reason="Transaction not found")

        response = self.get_status_dict(transaction)

        for item, value in response.items():
            if type(value) is bytes:
                print(item,  ": ",  type(value), value)

        return web.json_response(response)

    # Helpers
    def validate_euro_to_token_request_collatoral(self, request_data):
        if not "collatoral_cent" in request_data:
            raise web.HTTPBadRequest(reason="Missing 'collatoral_cent' field.")
        try:
            return int(request_data["collatoral_cent"])
        except ValueError:
            raise web.HTTPBadRequest(reason="'collatoral_cent' field must be an integer")

    def validate_euro_to_token_destination_address(self, request_data):
        if not "dest_wallet" in request_data:
            raise web.HTTPBadRequest(reason="Missing 'dest_wallet' field.")
        return request_data["dest_wallet"]

    def clean_transaction_status(self, transaction_data):
        if "status" in transaction_data:
            transaction_data["status_text"] = self.clean_status(transaction_data["status"])
            transaction_data["status"]      = transaction_data["status"].value
        return transaction_data

    def clean_status(self, status):
        if status == Transaction.Status.CREATED:
            return "Transaction created"
        elif status == Transaction.Status.PAYMENT_READY:
            return "Ready for payment"
        elif status == Transaction.Status.PAYMENT_PENDING:
            return "Waiting for payment"
        elif status == Transaction.Status.PAYMENT_DONE:
            return "Payment Done"
        elif status == Transaction.Status.PAYOUT_DONE:
            return "Payout Done"
        else:
            return "Invalid Status"

    def start_creation(self, collatoral_cent, dest_wallet, temp_counterparty=None):
        try:
            data = self.stablecoin_interactor.initiate_creation(
                    collatoral_amount_cent=collatoral_cent,
                    destination_wallet=dest_wallet,
                    temp_counterparty=temp_counterparty
                    )
            data = self.clean_transaction_status(data)
            return data

        except StablecoinInteractor.CommunicationError:
            raise web.HTTPInternalServerError()

    "Exchange T->E"
    # Get exchange rate
    async def exchange_rate_token_to_euro(self, request):
        base = request.query.get("base", 100)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stablecoin_interactor.get_exchange_rate_tok_to_col(base)
        return web.json_response({"token": base, "eur": ans})

    # Start Destruction transaction
    async def exchange_token_to_euro(self, request):
        data = dict(await request.json())

        token_amount_cent = self.validate_token_to_euro_token_amount(data)
        iban              = self.validate_token_to_euro_iban(data)
        temp_counterparty = data.get("counterparty", None)

        payment_data      = self.start_destruction(token_amount_cent, iban, temp_counterparty)

        return web.json_response(payment_data)

    # Helpers
    def validate_token_to_euro_token_amount(self, request_data):
        if not "token_amount_cent" in request_data:
            raise web.HTTPBadRequest(reason="Missing 'token_amount_cent' field.")
        try:
            return int(request_data["token_amount_cent"])
        except ValueError:
            raise web.HTTPBadRequest(reason="'token_amount_cent' field must be an integer")

    def validate_token_to_euro_iban(self, request_data):
        if not "destination_iban" in request_data:
            raise web.HTTPBadRequest(reason="Missing 'destination_iban' field.")
        return request_data["destination_iban"]

    def start_destruction(self, token_amount_cent, iban, temp_counterparty=None):
        try:
            data =  self.stablecoin_interactor.initiate_destruction(
                    token_amount_cent=token_amount_cent,
                    destination_iban=iban,
                    temp_counterparty=temp_counterparty
                    )
            data = self.clean_transaction_status(data)
            return data
        except StablecoinInteractor.CommunicationError:
            raise web.HTTPInternalServerError()

    async def get_iban_transactions(self, request):
        if "iban" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'iban'")
        iban = request.query["iban"]
        transactions = self.stablecoin_interactor.get_iban_transactions(iban)
        transactions2 = [self.clean_transaction_status(t.get_data()) for t in transactions]
        return web.json_response(transactions2)

    async def get_wallet_transactions(self, request):
        if "wallet" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'wallet'")
        wallet = request.query["wallet"]
        transactions = self.stablecoin_interactor.get_wallet_transactions(wallet)
        transactions2 = [self.clean_transaction_status(t.get_data()) for t in transactions]
        return web.json_response(transactions2)

    async def get_wallet_balance(self, request):
        if "wallet" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'wallet'")
        wallet = request.query["wallet"]

        balance = self.stablecoin_interactor.get_wallet_balance(wallet)

        return web.json_response({
            "wallet": wallet,
            "balance":balance
            })

    # def start(self):
    #     web.run_app(self.app, port=8000)

class RootEndpoint(BaseEndpoint):
    """
    The root endpoint of the HTTP API is the root resource in the request tree.
    It will dispatch requests regarding torrents, channels, settings etc to the right child endpoint.
    """

    def setup_routes(self):
        endpoints = {'/api': APIEndpoint,
                # '/gui': GUIEndpoint,
                }
        for path, ep_cls in endpoints.items():
            self.add_endpoint(path, ep_cls())

class MyRESTManager(RESTManager):

    def __str__(self) -> str:
        return "rest"

    async def start(self, port=8085):
        """
        Starts the HTTP API with the listen port as specified in the session configuration.
        """

        root_endpoint = RootEndpoint(middlewares=[cors_middleware])
        root_endpoint.initialize(self.session)
        setup_aiohttp_apispec(
                app=root_endpoint.app,
                title="IPv8 REST API documentation",
                version="v1.9",
                url="/docs/swagger.json",
                swagger_path="/docs",
                )

        from apispec.core import VALID_METHODS_OPENAPI_V2
        if 'head' in VALID_METHODS_OPENAPI_V2:
            VALID_METHODS_OPENAPI_V2.remove('head')

        runner = web.AppRunner(root_endpoint.app, access_log=None)
        await runner.setup()
        # If localhost is used as hostname, it will randomly either use 127.0.0.1 or ::1
        self.site = web.TCPSite(runner, '127.0.0.1', port)
        await self.site.start()

