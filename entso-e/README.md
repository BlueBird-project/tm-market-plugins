## Configuring the service

Retrieving API TOKEN (
ENTSOE_TOKEN) - [acquire token](https://www.amsleser.no/blog/post/21-obtaining-api-token-from-entso-e)

## REST API

### Description

API docs (Swagger):

```
GET: {service_location}/api
```

HealthcheckAPI docs (Swagger):

```
GET: {service_location}/healthcheck/docs
```

Check configured markets :

```
GET: {service_location}/api/market
```

Start job downloading past offers (To populate the entso-e service with market offer data):

```
POST: {service_location}/api/market/country/job/{country_name} 
# set 'override_running_job' arg to True in order to ignore previous state - for instance when the previous job didn't finish successfully   
# The country_name can be obtained from {endpoint}/api/market.  
```
The maximum time span is **180 days**.


Check running job state:

```
POST: {service_location}/api/market/country/job/state
```

Verify data (for 15 minutes day/intraday offer total_isp_span should be 96 or 48 for some of the intraday markets  ) :

```
GET: {service_location}/api/market/verify 
```



 

### Samples

Get markets

```shell

curl -X 'GET'   'http://localhost:11001/api/market'   -H 'accept: application/json'

```

Get data for a market with an id  '1' (all timestamps are UNIX timestamp in milliseconds ):
```shell

curl -X 'GET'   'http://localhost:11001/api/market/1/offer?ts_from=1776075237000&ts_to=1788674437000'   -H 'accept: application/json'

````

Start data acquisition  job  for given country (gets data for all configured markets related with that country here 'Poland' ) for a given period  ( Maximum time range is 180 days).
```shell 
curl -X 'POST'   'http://localhost:11001/api/market/country/job/Poland?ts_from=1776075237000&ts_to=1788674437000&override_running_job=false'   -H 'accept: application/json'   -d ''
```

Check the state of running job.  If entsoe_job_progress is '100.0' - job should be finished and all data should be collected
```shell 

curl -X 'GET'  'http://localhost:11001/api/market/country/job/state' -H 'accept: application/json'

#Sample response:

{
"entsoe_job_state": "started",
"entsoe_job_country": "Poland",
"entsoe_job_progress": "2.06"  # Progress percentage
}

```




## Docker

#### Build

```
docker-compose -f .\compose\local.yaml --env-file .\resources\.env build entsoe-service
```

build and export image:

```shell
 .\compose\export_image.ps1 .\resources\.env         
```

#### Import/export docker

```
#TODO: save with aprpropriate tag  (env variable)
docker save -o d:/tmp/tm-entsoe-service-latest-0.5.3.tar bluebird.com/bluebird/tm-entsoe-service:latest bluebird.com/bluebird/tm-entsoe-service:0.5.3 

docker load -i d:/tmp/tm-entsoe-service-latest-0.5.3.tar
```

## Configuration

#### Market configuration: `entsoe.yaml`

- entsoe_api - `yaml`'s file section
    - subscribed_eic - list of markets to read the data
        - code - region EIC code
        - market_types - list of markets types: `intraday`|`day_ahead`
    - eic_codes - list of EIC codes with country/area names. Additional area codes can be
      found [here](https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC)

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