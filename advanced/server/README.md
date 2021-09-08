
# Server

To execute, run the following commands

```
docker network create callcenter
docker build -t callcenter_server .
docker run -i --network callcenter --network-alias serveer -t callcenter_server
```
