# Dropi
## A (small) api connector for api.intra.42.fr/v2

### What's done:
- fetch token from api using env variables values (`ApiToken` class)
- basic requests (get, post, patch, delete) (`Api42` class)
- `Api42.get()` gets all page of results unless specified by option
- multithreading
- `ApiRequest` class (inherits from TypedDict) to represent requests
- "mass requests" (relies on a list of ApiRequest objects to represent requests) (uses multithreading unless specified by option)

### TODO:
- ~~write/generate doc using Sphinx~~ (basic settings done, needs more config and prettier output)
- ~~allow to fetch token from creds using `ApiToken.__init__()` params too (add optionnal kwargs)~~
- better exceptions wrapping (failed requests, expired token, refresh token needs to be tested, etc)
- a bit more logs (and more granular control of logs)
- use params to build url
- **DRY:** *_get _post _patch* and *_delete* are just basically doing the same thing, we could use requests.request instead
- ideas are welcome x) 

### To use/test it:
- `pip install git+ssh://git@github.com/42-Lisboa/dropi`
- `source .env` after filling it with your api credentials
- `import dropi` in your script
-  ~~`t = dropi.ApiToken()` to create your api token~~ (automatically done by dropi.Api42() now)
- `api = dropi.Api42(t)` to create your api connector instance
- `response = api.get("campus/38/users")` to get all users from lisbon campus for example (don't forget to strip away the api.intra.42.fr/v2 part from the url)
- `enjoy` :) 

### Doc:
 - you will need sphinx installed (or python-sphinx on fedora)
 - just run `build_doc.sh` and visit the link at the end of the script output :)
