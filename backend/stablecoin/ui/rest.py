from ui.ui import UI
from stablecoin import StablecoinInteractor
from transaction import Transaction

from aiohttp import web

from abc import ABC
from copy import copy

from pyipv8.ipv8.REST.rest_manager  import RESTManager, cors_middleware
from pyipv8.ipv8.REST.base_endpoint import BaseEndpoint

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec

from binascii import hexlify, unhexlify

INITIAL_BALANCE = 100


class APIEndpoint(BaseEndpoint):

    def __init__(self):
        super(APIEndpoint, self).__init__()
        self.trustchain = None

    def initialize(self, session):
        super(APIEndpoint, self).initialize(session)#.blockchain.ipv8)
        self.stablecoin_interactor = session
        self.app.router._frozen = False
        self.app.add_routes(
                self.parse_post_routes(
                    self.stablecoin_interactor.get_additional_post_routes()))
        self.app.router._frozen = True
        # self.trustchain = session.get_overlay(MyTrustChainCommunity)

    def parse_post_routes(self, route_dict):
        def new_callback(callback):
            async def fun(request):
                return web.json_response(callback(await request.json()))
            return fun
        return [ web.post(url, new_callback(callback))
                for url, callback in route_dict.items()]


    def setup_routes(self):
        self.app.add_routes([

            # web.post( '/exchange/e2t/tikkie_callback',  self.tikkie_callback),

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
        ])

    # async def tikkie_callback(self, request):
    #     print(await request.json())
    #     return web.json_response({})

    def get_status_dict(self, t):
        ans = t.serialise()
        ans.update({ "gateway_name": self.stablecoin_interactor.name })
        return ans

    "Creation"
    # Step 1 -> returns info to connect to gateway over ipv8
    async def REST_CREATE_initiate(self, request):
        data = dict(await request.json())

        collatoral_cent = self.validate_euro_to_token_request_collatoral(data)

        t = self.stablecoin_interactor.CREATE_initiate(collatoral_cent)

        response = self.get_status_dict(t)

        return web.json_response(response)

    # Step 2 -> user connects through ipv8 to register its node and address
    # Over trustchain

    # Step 3 -> returns the payment link to the user
    async def REST_CREATE_start_payment(self, request):

        data = dict(await request.json())

        payment_id = self.validate_payment_id(data)
        transaction = self.stablecoin_interactor.CREATE_start_payment(payment_id)

        if not transaction:
            raise web.HTTPBadRequest(reason="Wrong state")

        response = self.get_status_dict(transaction)

        return web.json_response(response)

    # Step 4 -> triggers_payout
    async def REST_CREATE_finish_payment(self, request):
        data = dict(await request.json())

        payment_id = self.validate_payment_id(data)
        transaction = self.stablecoin_interactor.CREATE_finish_payment(payment_id)

        if not transaction:
            raise web.HTTPBadRequest(reason="Wrong state")


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

    "Exchange E->T"
    # Get exchange rate
    async def exchange_rate_euro_to_token(self, request):
        base = request.query.get("base", None)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stablecoin_interactor.get_exchange_rate_col_to_tok(base)
        return web.json_response({"eur": base, "token": ans})

    # Get info on existing transaction
    async def exchange_status(self, request):
        payment_id = self.validate_payment_id(request.query)
        transaction = self.stablecoin_interactor.get_transaction(payment_id)

        response = self.get_status_dict(transaction)

        return web.json_response(response)

    # Helpers

    def validate_payment_id(self, request_data):
        if "payment_id" not in request_data:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")

        payment_id = request_data["payment_id"]

        transaction = self.stablecoin_interactor.get_transaction(payment_id)
        if not transaction:
            raise web.HTTPNotFound(reason="Transaction not found")

        return payment_id

    def validate_euro_to_token_request_collatoral(self, request_data):
        if not "collatoral_cent" in request_data:
            raise web.HTTPBadRequest(reason="Missing 'collatoral_cent' field.")
        try:
            return int(request_data["collatoral_cent"])
        except ValueError:
            raise web.HTTPBadRequest(reason="'collatoral_cent' field must be an integer")

    "Exchange T->E"
    # Get exchange rate
    async def exchange_rate_token_to_euro(self, request):
        base = request.query.get("base", None)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stablecoin_interactor.get_exchange_rate_tok_to_col(base)
        return web.json_response({"token": base, "eur": ans})

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

    async def start(self, ip='0.0.0.0', port=8000):
        """
        Starts the HTTP API with the listen port as specified in the session configuration.
        """

        print("STARTING REST")

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
        self.site = web.TCPSite(runner, ip, port)
        await self.site.start()

