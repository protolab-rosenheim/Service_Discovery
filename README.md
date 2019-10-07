# Service discovery Webservice

## Building and running the Docker Container

    docker build -t servicediscoveryws .
    docker run -d -p 5000:5000 servicediscoveryws
    

## REST ##
* Get all registered devices:
```
servicediscovery.domain.de:5000/api/v1/device
```

* Get all devices which update was 5 or less minutes ago:
```
servicediscovery.domain.de:5000/api/v1/online-devices
```

* Get all devices which update was 10 minutes or less ago:
```
servicediscovery.domain.de:5000/api/v1/online-devices?lastUpdatedMinAgo=10
```