## Run script to build image
powershell -ExecutionPolicy Bypass -File .\docker_build.ps1

## manual build imagge
docker build --no-cache -t ubuntu-cuda-vnc . 

## port
3000 - ssh
6000 - vnc

## users
- root
- vagrant