FROM osrm/osrm-backend:latest

RUN mkdir /data
RUN ls
RUN pwd
ADD ./profiles/bicycle.lua bicycle.lua
RUN ls
# RUN cat /opt/bicycle.lua
