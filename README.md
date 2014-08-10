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
log_file: Log file for operations
log_level: Log level

creds:
  username: Rackspace Cloud username. This also can be read from the
  environment variable OS_USERNAME or passed via the command line using
  --username.

  api_key: Rackspace Cloud api key. This also can be read from the
  environment variable OS_PASSWORD or passed via the command line using
  --apikey.

  region: Rackspace Cloud region(ord,iad,lon,syd,hkg). This also can be
  read from the environment variable OS_REGION or passed via the command
  line using --region.

server:
  image_id: Rackspace cloud server image ID.

  flavor_id: Rackspace cloud flavor ID.

  sshkey_name: SSH key if server type is Linux.

  tests: Define the tests that need to be performed for determining the
  sucess of the server build.

  ports: Comma separated list of ports. These ports will be scanned to make
  sure they are listening.

  url: A URL that can be used to check heath status. e.g. /health.php

  url_sha1:  A SHA checksum for the URL.

  retries: Number of times to try the tests.

  build_timeout: Number of seconds to wait before treating the server as
  failed. If the server is not active by then, it will be deleted.

  total_timeout: A grand total timeout after which the scripts aborts.

  check_interval: Intervals to check server status during the build process.
  If you set this too low, you may hit API limits.

  desired_count: Number of servers desired

  error_prediction_pct: An estimation of how many servers will fail the build.
  This is used to calculate the number of servers to start with. The values
  are rounded to the nearest integer.

  delete_failed: Delete servers that we consider failed. This includes the
  servers that took longer than build_timeout.

  delete_success: Delete servers in any case. Used for testing and playing.

  rackconnect: Are these servers rackconnected.

  stats_file: A file to which CSV results will be written.

```

TODO
======
 * Test with custom and windows images
 * Implement rackconnect
 * Validate sshkey functionality


EXAMPLES
======

```
python spinup.py  --template test01.yml 
Starting spinup : Username: rtsdemo03 , Region: LON
Desired count reached 10
+---------------+-----------------+--------------+------------+----------------+----------------+--------------------------------------+
| name          |    end-status   | build-status | build-time |   flavor-id    |   primary-ip   |              server-id               |
+---------------+-----------------+--------------+------------+----------------+----------------+--------------------------------------+
| yse8-bl24esa3 | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.52.47  | d892f64f-6022-4abc-83c3-38e5e1d6c017 |
| yse8-mxh88hqr | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.90  | a6bcfa15-799a-4a9e-a303-d1138d3cc31a |
| yse8-m7p8xhnl | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.91  | 08a23c34-da75-4ffa-838e-8e5b77560b9e |
| yse8-gagb1eb8 | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.92  | b9b6ee3b-62e8-4d86-9a5c-81d0beaf91fd |
| yse8-sxa5ob4a | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.186 | c587caf9-2801-4a47-90b4-d5683fd891df |
| yse8-7ziytyl6 | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.117 | 29f14284-8a3c-4681-a729-d0b849b04751 |
| yse8-mfdnfcif | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.187 | 22ee878d-fd14-44c0-b10c-9fca3a3844de |
| yse8-5ouagw9k |     DELETED     |    BUILD     |     20     | performance1-2 |    0.0.0.0     | 27e29a80-af6a-4090-bc3b-f4bbc260a322 |
| yse8-ibpgmsyr |     DELETED     |    BUILD     |     20     | performance1-2 |    0.0.0.0     | 0325f6b4-5440-45af-a7e9-91610896b424 |
| yse8-ikpdzdfj | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.190 | 4df201b9-78e8-4e5d-afd4-76284e7501ce |
| yse8-a1v1z6y1 |     DELETED     |    BUILD     |     20     | performance1-2 |    0.0.0.0     | bc490d82-313a-43c9-8c6c-92cc2d75a950 |
| yse8-5nt29k7g | DELETED_SUCCESS |    ACTIVE    |     20     | performance1-2 | 134.213.60.192 | 07c28adc-fcfc-4eb2-82af-c82e7deb87ea |
| yse8-8owjh9nd | DELETED_SUCCESS |    ACTIVE    |     10     | performance1-2 | 134.213.60.193 | 42f56e1e-2c8c-4545-ab27-c78a0c2568eb |
+---------------+-----------------+--------------+------------+----------------+----------------+--------------------------------------+
```
  