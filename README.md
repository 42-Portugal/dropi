# Dropi - A (small) api connector for api.intra.42.fr/v2 

## Install ...

`pip install dropi`

## ... and have fun! 

```python3
import dropi
from pprint import pprint

# Create an instance for the api wrapper using environment variables 
# for application's uid, secret and scope
api = dropi.Api42()

# Get all users from lisbon campus
users = dropi.get("users", data={"campus_id": 38})

pprint(users)
```
