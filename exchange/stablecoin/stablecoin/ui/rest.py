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

            #"actual exchange (creation/destruction)"
            web.post( '/exchange/e2t',         self.exchange_euro_to_token), #tested
            web.post( '/exchange/t2e',         self.exchange_token_to_euro), #tested
            #"exchange rates"
            web.get(  '/exchange/e2t/rate',    self.exchange_rate_euro_to_token), #tested
            web.get(  '/exchange/t2e/rate',    self.exchange_rate_token_to_euro), #tested
            #"get payment status"
            web.get(  '/exchange/payment',     self.exchange_status), #tested
            #"get transactions for wallet/iban"
            web.get(  '/transactions/iban',    self.get_iban_transactions),
            web.get(  '/transactions/wallet',  self.get_wallet_transactions),
            web.get(  '/transactions/balance', self.get_wallet_balance), #tested

            #"FOR TESTING"
            web.post( '/exchange/complete', self.complete_payment), #tested
        ])

    async def complete_payment(self, request):
        data = dict(await request.post())
        # print(data["payment_id"])
        if "payment_id" not in data:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")
        if "counterparty" not in data:
            raise web.HTTPBadRequest(reason="Missing 'counterparty'")
        status = self.stabecoin_interactor.complete_payment(data["payment_id"], data["counterparty"])
        if status:
            return web.json_response()
        else:
            raise web.HTTPBadRequest(reason="Coundn't complete the transaction")

    "Exchange E->T"
    async def exchange_rate_euro_to_token(self, request):
        base = request.query.get("base", 100)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stabecoin_interactor.get_exchange_rate_col_to_tok(base)
        return web.json_response({"eur": base, "token": ans})

    async def exchange_status(self, request):
        # payment_id = request.match_info.get('payment_id')#.encode("ascii")
        if "payment_id" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'payment_id'")

        payment_id = request.query["payment_id"]

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
        base = request.query.get("base", 100)
        try:
            base = int(base)
        except:
            raise web.HTTPBadRequest(reason="'base' should be an integer amount of cents")
        ans  = self.stabecoin_interactor.get_exchange_rate_tok_to_col(base)
        return web.json_response({"token": base, "eur": ans})

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

    async def get_iban_transactions(self, request):
        if "iban" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'iban'")
        iban = request.query["iban"]

    async def get_wallet_transactions(self, request):
        if "wallet" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'wallet'")
        wallet = request.query["wallet"]

    async def get_wallet_balance(self, request):
        if "wallet" not in request.query:
            raise web.HTTPBadRequest(reason="Missing 'wallet'")
        wallet = request.query["wallet"]

        balance = self.stabecoin_interactor.get_wallet_balance(wallet)

        return web.json_response({
            "wallet": wallet,
            "balance":balance
            })

    def start(self):
        web.run_app(self.app, port=8000)

    def __str__(self) -> str:
        return "rest"
