from ipv8.messaging.lazy_payload           import VariablePayload, vp_compile

@vp_compile
class GatewayConnectMessage(VariablePayload):
    msg_id      = 1  # Gateway Connect message
    format_list = ["Q", "varlenI"]
    names       = ["global_time", "payment_id"]

