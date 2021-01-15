#!/bin/bash
for safety in low med high; do
    for hill in low med high; do
        # theses will take a lot of memory, so best to do one-by-one
        docker build -t bike-mapper-h-${hill}-s-${safety} --build-arg profile=bicycle-h-${hill}-s-${safety}.lua docker
        docker tag bike-mapper-h-${hill}-s-${safety} registry.digitalocean.com/bikesy/bike-mapper-h-${hill}-s-${safety}
        # can background the pushes
        docker push registry.digitalocean.com/bikesy/bike-mapper-h-${hill}-s-${safety} &
    done
done