# Api-Gateway Microservice
GoOutSafe - API gateway microservice

# Usage
___
Spin up application for production by:
 - Setting environment variable `export DEPLOY_MODE=production`
 - `docker-compose up -d`

App will be accessible through api gateway only at `http://localhost:5000/`.

# Development
---
For testing and development purposes app can run by:
  - Setting environment variable `export DEPLOY_MODE=development`
  - `docker-compose up -d`
  - Sourcing development configuration with `. ./set_dev_env.sh`

Containers will now run flask using debug/development mode and will restart upon detecting changes to their respective microservice code.
All services will now be accessible by host machine as well at the address specified by the respective environment variable (e.g. `echo $GOS_REDIS`, `echo $GOS_NOTIFICATION` ..)
