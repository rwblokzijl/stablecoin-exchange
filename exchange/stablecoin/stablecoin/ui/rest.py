from stablecoin.ui.ui import UI
from stablecoin.stablecoin import StabecoinInteractor

from aiohttp import web

from abc import ABC

class Request(ABC):
    pass

class REST(UI):

    def __init__(self, stabecoin_interactor, test_config=None):
        self.stabecoin_interactor = stabecoin_interactor
        self.app = web.Application()
        self.app.add_routes([
            web.post('/exchange/e2t'       , self.exchange_euro_to_token),
            web.get('/exchange/e2t/rate/{base}' , self.exchange_rate_euro_to_token),
            web.get('/exchange/e2t/payment/{payment_id}' , self.exchange_euro_to_token_status),

            web.post('/exchange/t2e'       , self.exchange_token_to_euro),
            # web.get('/exchange/t2e/{base}' , self.exchange_rate_token_to_euro),
            # web.get('/exchange/t2e/payment/{payment_id}' , self.exchange_euro_to_token_status),
        ])

    "Exchange E->T"
    async def exchange_rate_euro_to_token(self, request):
        base = int(request.match_info.get('base', 100))
        ans  = self.stabecoin_interactor.get_exchange_rate_col_to_tok(base)
        return web.json_response({"eur": base, "token": ans})

    async def exchange_euro_to_token_status(self, request):
        payment_id = request.match_info.get('payment_id')#.encode("ascii")

        payment_data = self.stabecoin_interactor.transaction_status(payment_id)

        return web.json_response(payment_data)

    async def exchange_euro_to_token(self, request):
        data = dict(await request.post())

        collatoral_cent = self.validate_euro_to_token_request_collatoral(data)
        dest_wallet     = self.validate_euro_to_token_destination_address(data)

        payment_data = self.start_creation(collatoral_cent, dest_wallet)

        return web.json_response(payment_data)

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

    def start_creation(self, collatoral_cent, dest_wallet):
        try:
            return self.stabecoin_interactor.initiate_creation(
                    collatoral_amount_cent=collatoral_cent,
                    destination_wallet=dest_wallet
                    )

        except StabecoinInteractor.CommunicationError:
            raise web.HTTPInternalServerError()

    "Exchange T->E"
    async def exchange_rate_token_to_euro(self, request):
        pass

    async def exchange_token_to_euro(self, request):
        data = dict(await request.post())

        token_amount_cent = self.validate_token_to_euro_token_amount(data)
        iban              = self.validate_token_to_euro_iban(data)

        payment_data      = self.start_destruction(token_amount_cent, iban)

        return web.json_response(payment_data)

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

    def start_destruction(self, token_amount_cent, iban):
        try:
            return self.stabecoin_interactor.initiate_destruction(
                    token_amount_cent=token_amount_cent,
                    destination_iban=iban
                    )
        except StabecoinInteractor.CommunicationError:
            raise web.HTTPInternalServerError()

    def start(self):
        web.run_app(self.app, port=8000)

    def __str__(self) -> str:
        return "rest"
