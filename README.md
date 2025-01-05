### Grafana Provisioning
#### InfluxDB Data Source
I automated the Grafana InfluxDB data source. It is using the Flux query language. I'm not a big fan of that query language but the original project was using it so I just went along with it.

#### Dashboards
I have the dashboard from [this image](img/speed_and_temp_dashboard.png) in source control and it will automatically be created and linked to the data source above.

### Docker Service Management
```bash
docker compose build  # build images
docker compose up     # start containers (use -d to detatch from the terminal)
docker compose down   # stop containers (you can just control-c if still attached)
```

### Included Grafana Dashboard
<img src="img/speed_and_temp_dashboard.png" width="500px">

### Credits
This repository is a fork of https://github.com/akarazeev/temp-monitor