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
            web.get('/exchange/e2t/{base}' , self.exchange_rate_euro_to_token),
            web.post('/exchange/t2e'       , self.exchange_token_to_euro),
            # web.get('/exchange/t2e/{base}' , self.exchange_rate_token_to_euro),
        ])

    async def exchange_rate_euro_to_token(self, request):
        base = int(request.match_info.get('base', 100))
        ans  = self.stabecoin_interactor.get_exchange_rate(base)
        return web.json_response({"eur": base, "token": ans})

    async def exchange_euro_to_token(self, request):
        data = dict(await request.post())
        if not "collatoral_cent" in data:
            raise web.HTTPBadRequest(reason="Missing 'collatoral_cent' field.")
        try:
            collatoral_cent = int(data["collatoral_cent"])
        except ValueError:
            raise web.HTTPBadRequest(reason="'collatoral_cent' field must be an integer")
        if not "dest_wallet" in data:
            raise web.HTTPBadRequest(reason="Missing 'dest_wallet' field.")

        dest_wallet     = data["dest_wallet"]

        try:
            ans = self.stabecoin_interactor.start_transaction(
                    collatoral_amount_cent=collatoral_cent,
                    destination_wallet=dest_wallet
                    )
            return web.json_response(ans)

        except StabecoinInteractor.CommunicationError:
            raise web.HTTPInternalServerError()

    async def exchange_token_to_euro(self, request):
        return web.json_response({})

    def start(self):
        web.run_app(self.app)

    def __str__(self) -> str:
        return "rest"
