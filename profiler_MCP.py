from mcprotocol import SecureServer
import cProfile

class ProfilerMCP(SecureServer):
    @endpoint('/v1/profile/start')
    def start_profile(self, params):
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        return {"status": "started"}