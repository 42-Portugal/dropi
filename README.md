# Dropi
## A (small) api connector for api.intra.42.fr/v2

### What's done:
- fetch token from api using env variables values (`Token` class)
- basic requests (get, post, patch, delete) (`Api42` class)
- `Api42.get()` gets all page of results unless specified by option
- multithreading
- `ApiRequest` class (inherits from TypedDict) to represent requests
- "mass requests" (relies on a list of ApiRequest class to represent requests) (uses multithreading unless specified by option)

### TODO:
- write/generate doc using Sphinx
- allow to fetch token from creds using `Token.__init__()` params too (add optionnal kwargs)
- better exceptions wrapping (failed requests, expired token, refresh token needs to be tested, etc)
- ideas are welcome x) 
