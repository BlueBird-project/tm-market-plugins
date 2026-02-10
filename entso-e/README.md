## Docker

#### Build

```
docker-compose -f .\compose\local.yaml --env-file .\resources\.env build entsoe-service
```

#### Import/export docker

```
docker save -o d:/tmp/tm-entsoe-service-app_latest.tar tm-entsoe-service-app:latest

docker load -i d:/tmp/tm-entsoe-service-app_latest.tar
```

## Configuration

#### Market configuration: `entsoe.yaml`

- entsoe_api - `yaml`'s file section
    - subscribed_eic - list of markets to read the data
        - code - region EIC code
        - market_types - list of markets types: `intraday`|`day_ahead`
    - eic_codes - list of EIC codes with country/area names
      Sample:

```yaml
entsoe_api:
  subscribed_eic:
    - code: 10YES-REE------0
      market_types:
        - "intraday"
        - "day_ahead"
  eic_codes:
    10Y1001A1001A82H:
      code: "10Y1001A1001A82H"
      area_names:
        - "BZN|DE-LU"
      country_codes:
        - "Germany"
        - "DE"
    10YES-REE------0:
      code: "10YES-REE------0"
      area_names:
        - "BZN|ES"
      country_codes:
        - "Spain"
        - "ES" 
```

## Running the service

TODO:

### TODO:

- define how much data there should apper daily for each market, add download time to the subscribed market setting

### links:

https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC

https://documenter.getpostman.com/view/7009892/2s93JtP3F6#3b383df0-ada2-49fe-9a50-98b1bb201c6b