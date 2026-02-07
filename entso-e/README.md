## Build docker
```

docker-compose -f .\compose\local.yaml --env-file .\resources\.env build entsoe-service

docker save -o d:/tmp/tm-entsoe-service-app_latest.tar tm-entsoe-service-app:latest

docker load -i d:/tmp/tm-entsoe-service-app_latest.tar
```
## Configuration

describe configuration

## Running the service

TODO:



### links:
https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC

https://documenter.getpostman.com/view/7009892/2s93JtP3F6#3b383df0-ada2-49fe-9a50-98b1bb201c6b