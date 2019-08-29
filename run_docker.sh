#!/usr/bin/env bash
docker build -t curami-web:latest .
docker run -p 5000:5000 curami-web:latest