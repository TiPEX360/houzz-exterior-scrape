#!/bin/bash
imagemagick mogrify -path ./converted/ -resize 1024x768\^ -gravity Center -extent 1024x768 ./scraped/*