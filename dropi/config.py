import os
from enum import IntEnum

token_url = "https://api.intra.42.fr/oauth/token"
"""The endpoint to request an acces token to 42 intra's api."""

endpoint = "https://api.intra.42.fr/v2"
"""The base endpoint to 42 intra's api."""

params = {
    "grant_type": "client_credentials",
    "client_id": os.getenv("UID42"),
    "client_secret": os.getenv("SECRET42"),
    "scope": os.getenv("SCOPE42")
}
"""The paramaters to be provided to request token.

    :meta hide-value:
"""

max_poolsize = 3
"""The maximum poolsize for concurrent request, defaults to ``3``.

    In order to garantee that intra doesn't trigger a 429 "Too Many Requests",
    this variable should be set to one lower than the actual max requests per
    second of the token being used.

    To update it, just set it to the new value.

    .. code-block:: python
        :linenos:

        import dropi
        config.dropi.max_poolsize = 42
        # Do stuff
"""

class LogLvl(IntEnum):
    """:class:`~.Api42` logging level.

        Priority is ordered by numeric value.
    """
    Debug = -10
    Info = 10
    Error = 20
    Fatal = 30
    NoLog = 10000

log_lvl = LogLvl.Error
