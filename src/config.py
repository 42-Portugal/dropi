import os

token_url = "https://api.intra.42.fr/oauth/token"
endpoint = "https://api.intra.42.fr/v2"
params = {
    "client_id": os.getenv("UID42"),
    "client_secret": os.getenv("SECRET42"),
    "grant_type": "client_credentials",
    "scope": "public projects tig forum profile elearning"
}

max_poolsize = 30
