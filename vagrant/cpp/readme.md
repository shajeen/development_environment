## Run script to build image
powershell -ExecutionPolicy Bypass -File .\docker_build.ps1

## manual build imagge
docker build --no-cache -t cpp-core-latest . 

## port
1002

## users
- root
- vagrant