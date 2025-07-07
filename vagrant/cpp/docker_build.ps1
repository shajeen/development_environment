# Define the Docker build command
$dockerBuildCommand = "docker build . -t cpp-core-latest --no-cache"

# Execute the Docker build command
Invoke-Expression -Command $dockerBuildCommand
