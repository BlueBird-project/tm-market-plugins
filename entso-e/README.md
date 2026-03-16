## Configuring the service

Retrieving API TOKEN (
ENTSOE_TOKEN) - [acquire token](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)

## Managing the service

API docs (Swagger):

```
GET: {service_location}/api
```
HealthcheckAPI docs (Swagger):

```
GET: {service_location}/healthcheck/docs
```

Check configured markets:

```
GET: {service_location}/api/market
```

Start job downloading past offers:

```
POST: {service_location}/api/market/country/job/{country_name} 
(set 'override_running_job' arg to True in order to ignore previous state - for instance the previous job didn't finish successfully  ) 
```

Check running job state:

```
POST: {service_location}/api/market/country/job/state
```

Verify data (for 15 minutes day/intraday offer total_isp_span should be 96 or 48 for some of the intraday markets  ) :

```
GET: {service_location}/api/market/verify 
```

## Docker

#### Build

```
docker-compose -f .\compose\local.yaml --env-file .\resources\.env build entsoe-service
```

#### Import/export docker

```
docker save -o d:/tmp/tm-entsoe-service-app_latest.tar bluebird.com/bluebird/tm-entsoe-service:latest

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
- add rest endpoint which start KI post (market data, offer data)
- KI -  "service", "start-command","state-command"

### links:

https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC

https://documenter.getpostman.com/view/7009892/2s93JtP3F6#3b383df0-ada2-49fe-9a50-98b1bb201c6b