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
```

  TODO
  =====
  Test with custom and windows images
  Implement rackconnect
  Validate sshkey functionality
  