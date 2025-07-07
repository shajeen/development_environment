## Run script to build image
powershell -ExecutionPolicy Bypass -File .\docker_build.ps1

## manual build imagge
docker build --no-cache -t ubuntu-core . 

## port
1000

## users
- root
- vagrant