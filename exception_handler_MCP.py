from mcprotocol import SecureServer
from sentry_sdk import capture_exception

class ExceptionHandlerMCP(SecureServer):
    @endpoint('/v1/error/report')
    def report_error(self, params):
        capture_exception(params['exception'])
        return {"event_id": "generated-event-id"}