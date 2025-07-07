# Define the Docker build command
$dockerBuildCommand = "docker build . -t ubuntu-core --no-cache"

# Execute the Docker build command
Invoke-Expression -Command $dockerBuildCommand
