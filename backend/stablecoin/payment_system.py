from abc import ABC, abstractmethod

import logging

class PaymentSystem(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    "Set the stablecoin instance"
    def set_callback_instance(self, stablecoin_instance):
        self.stablecoin = stablecoin_instance

    def get_post_callback_routes(self):
        """ return: {url : callback_function, ...} """
        pass

    "Helpers"
    @abstractmethod
    def __str__(self):
        pass

    "Payment end"

    "Step 0: Creation"
    @abstractmethod
    def create_payment_request(self, amount):
        "Returns payment identifier string if succesful"

    "Payout End"

    "Step 3: Validate the request is payed"
    @abstractmethod
    def attempt_payment_done(self):
        pass

    "Step 4: Start the payout"
    @abstractmethod
    def initiate_payment(self, account, amount):
        "Returns true if succesful"
        pass


