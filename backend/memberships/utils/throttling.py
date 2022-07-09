from rest_framework.throttling import SimpleRateThrottle


class EnhancedThrottle(SimpleRateThrottle):
    """
    Enhanced DRF throttle to support flexible rates and action validation.
    """

    def __init__(self, scope, action=None):
        self.scope = scope
        self.action = action
        super().__init__()

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split("/")
        num_requests = int(num)
        durations = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if period[0] in durations:
            duration = durations[period[0]]
        else:
            # parse 1/30s, 100/30m etc. shamelessly brittle.
            duration = int(period[:-1]) * durations[period[-1]]
        return (num_requests, duration)

    def allow_request(self, request, view):
        if self.action and self.action != view.action:
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class Throttle:
    """
    Enhanced DRF throttle to support flexible rates and action validation.
    """

    def __init__(self, scope, action=None):
        self.scope = scope
        self.action = action
    
    def __call__(self, *args, **kwargs):
        return EnhancedThrottle(self.scope, self.action)
