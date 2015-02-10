# TwemSentinel

Python [twemproxy](https://github.com/twitter/twemproxy) agent for the master-change event and nutcracker config/restart

Simply, it will update TwemProxy and restart it when [redis
sentinel](http://redis.io/topics/sentinel) push notify for master-change (+switch-master).

```python
import twemsentinel
t = twemsentinel.Twemsentinel()
t.start()
```

You can use [config.yml](config.yml) for configration about sentinel(ip:port) , twemproxy config file, nutcracker restart command and log file


```yml
sentinel_ip: "127.0.0.1"
sentinel_port: "26379"
twemproxy_config_file: "nutcracker.yml"
nutcracker_restart_command: "supervisorctl restart nutcracker" # or /etc/init.d/twemproxy restart
log_file: "twemsentinel.log"

```
