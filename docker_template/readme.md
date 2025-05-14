## cpp.workspace

#### build
docker buildx build -f cpp.dockerfile -t cpp.workspace.image . --no-cache

#### create volume
docker volume create cpp.workspace.volume

#### docker run
docker run -it -p 3001:22 -v cpp.workspace.volume:/workspace --name cpp.workspace cpp.workspace.image

#### docker-compose
docker build --no-cache
docker up -d