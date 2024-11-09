import subprocess

def run_command(command):
    """Helper function to execute a shell command."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
    else:
        print(result.stdout)

# Stop all running containers (ignores errors if there are no running containers)
run_command("docker stop $(docker ps -q) || true")

# Remove all stopped containers (ignores errors if there are no stopped containers)
run_command("docker rm $(docker ps -aq) || true")

# Build the Docker image with the tag 'ebus_backend'
run_command("docker build . -t ebus_backend")

# Run the Docker container, mapping port 8000 on the host to port 8000 in the container
run_command("docker run -d -p 8000:8000 ebus_backend")
