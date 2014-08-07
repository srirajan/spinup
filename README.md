spinup
======
Simple server spinup example using Pyrax and a yaml definition file
 - Define server type
 - Define count
 - Define simple test criteria
 - Delete if failed
 - Generate statistics

Arguments:
--help     : This help
--username : Rackspace Cloud username.This also can be read from the environment variable OS_USERNAME 
--apikey   : Rackspace Cloud API key. This also can be read from the environment variable OS_PASSWORD 
--region   : Rackspace Cloud region(ord,iad,lon,syd,hkg). This also can be read from the environment variable OS_REGION 
--template : YAML template (use --templatehelp for more details)
--templatehelp : Print detailed template help

YAML template file explained :-

```
--- 
log_file: Log file for operations
log_level: Log level

creds:
  username: Rackspace Cloud username. This also can be read from the environment variable OS_USERNAME or passed via the command line using --username
  api_key: Rackspace Cloud api key. This also can be read from the environment variable OS_PASSWORD or passed via the command line using --apikey
  region: Rackspace Cloud region(ord,iad,lon,syd,hkg). This also can be read from the environment variable OS_REGION or passed via the command line using --region

server:
  image_id: Rackspace cloud server image ID
  flavor_id: Rackspace cloud flavor ID
  sshkey_name: SSH key if server type is Linux
  tests: Define the tests that need to be performed for determining the sucess of the server build
    ports: Comma separated list of ports. These ports will be scanned to make sure they are listening
    url: A URL that can be used to check heath status. e.g. /health.php
    url_sha:  A SHA checksum for the URL
  build_timeout: Number of seconds to wait before treating the server as failed. If the server is not active by then, it will be deleted.
  total_timeout: A grand total timeout after which the scripts aborts.
  check_interval: Intervals to check server status during the build process. If you set this too low, you may hit API limits 
  desired_count: Number of servers desired
  error_prediction_pct: An estimation of how many servers will fail the build. This is used to calculate the number of servers to start with. The values are rounded to the nearest integer
  delete_failed: Delete servers that we consider failed. This includes the servers that took longer than build_timeout
  delete_success: Delete servers in any case. Used for testing and playing.
  rackconnect: Are these servers rackconnected. 
  stats_file: A file to which CSV results will be written
  ```

  TODO
  =====
  Implement failure detection in code
  Implement cleanup on total timeout
  Fix stats header issue
  Test with custom and windows images
  Implement rackconnect
  Validate sshkey functionality
  