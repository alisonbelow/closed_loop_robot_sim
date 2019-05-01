# Grafana How-Tos

## How to add InfluxDB data source to Grafana

This is automatically done, but you can add a new data source with the following steps:  

1. Log into Grafana with username `admin` and password `admin`  
[grafana 0](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana0.png)

2. Skip next for new password prompt  
[grafana 1](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana1.png)

3. Select Add Data Source  
[grafana 2](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana2.png)

4. Select InfluxDB  
[grafana 3](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana3.png)

5. Fill in following information  
[grafana 4](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana4.png)

6. Click save and test  
[grafana 5](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana5.png)

# How to import Grafana JSON dashboard

1. Click on search/open folder icon  
[grafana 6](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana6.png)  

2. Click Import button  
[grafana 7](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana7.png)

3. Click Browse button and select sensor_data_dashboard.json in relativity directory  
[grafana 8](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana8.png)

4. Click save to save dashboard. Can now open to when running robot sim  
[grafana 9](https://github.com/alisonbelow/closed_loop_robot_sim/docs/grafana9.png)

[Pictures resources](https://grafana.com/docs/features/export_import/)