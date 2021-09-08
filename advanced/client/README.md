
# Client

To execute, run the following commands

```
docker build -t callcenter_client .
docker run -i --network callcenter --network-alias client -t callcenter_client
```
