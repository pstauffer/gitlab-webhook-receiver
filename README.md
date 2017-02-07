# gitlab-webhook-receiver
Simple gitlab webhook receiver.

## Source
The idea and base of the script is from this [github repo](https://github.com/schickling/docker-hook).

## Configuration

### Gitlab Secret Token
The script requires, that the gitlab secret token is set! You can define the value in the [configuration file](#example-config).

### Gitlab Project Homepage
The structure of the [configuration file](#example-config) requires the homepage of the gitlab project as key.

### Command
Define, which command should be run after the hook was received.

### Example config
```
# file: config.yaml
---
# myrepo
https://git.example.ch/exmaple/myrepo:
  command: uname
  gitlab_token: mysecret-myrepo
# test-repo
https://git.example.ch/exmaple/test-repo:
  command: uname
  gitlab_token: mysecret-test-repo
```

## Script Arguments

### Port
Define the listen port for the webserver. Default: **8666**

### Addr
Define the listen address for the webserver. Default: **0.0.0.0**

### Cfg
Define the path to your configuration file. Default: **config.yaml**



## Run Script

```
python gitlab-webhook-receiver.py --port 8080 --cfg /etc/hook.yaml
```


### Help
```
usage: gitlab-webhook-receiver.py [-h] [--addr ADDR] [--port PORT] [--cfg CFG]

Gitlab Webhook Receiver

optional arguments:
  -h, --help   show this help message and exit
  --addr ADDR  address where it listens (default: 0.0.0.0)
  --port PORT  port where it listens (default: 8666)
  --cfg CFG    path to the config file (default: config.yaml)
```