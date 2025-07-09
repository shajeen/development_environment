# Define the Docker build command
$dockerBuildCommand = "docker build . -t python-core-latest --no-cache"

# Execute the Docker build command
Invoke-Expression -Command $dockerBuildCommand
