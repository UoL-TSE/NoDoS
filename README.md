# NoDoS DoS protection
In-line, on device DoS protection.

## Requirements
# Windows
    - Install python            [From here](<https://www.python.org/downloads/>)
    - Install Docker Desktop    [From here](<https://docs.docker.com/desktop/setup/install/windows-install/>)

# Linux
    - Install python from your package manager
    - Install docker and docker-compose-plugin from your package manager

## Running the program
These commands should be executed in the working directory of this project.
For example

# Running the proxy
To run the proxy execute the command `python3 src/main.py`

As is the proxy will not have any server to forward data to/from.
An easy way to run a server to test with is with the `python -m http.server` command

# Running the database
To run the database execute the command `docker compose up -d`
This will run the MySQL instance, accessible via port 3306 on the host
