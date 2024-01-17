#!/bin/bash

pf flow build \
  --source flows/named_entity_recognition/standard \
  --output docker_output \
  --format docker
