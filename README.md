# NoDoS DoS protection
In-line, on device DoS protection.

## Requirements
### Windows
* Install Python [from here](<https://www.python.org/downloads/>)
* Install Docker Desktop [from here](<https://docs.docker.com/desktop/setup/install/windows-install/>)

### Linux
* Install `python` from your package manager
* Install `docker` and `docker-compose-plugin` from your package manager (these package name may vary depending on your distribution)

## Running the program
### Getting the code
First clone

The following commands should be executed in the working directory of this project.<br>


### Running the database
To run the database execute the command `docker compose up -d`.<br>
This will run the MySQL instance, accessible via port 3306 on the host.

When modifying anything in the `mysql_init` folder, you need to remove the docker volume associated with the database before you can re run it to execute those scripts.<br>
To do this just execute the command `docker compose down --volumes` and start it again regularly.<br>
WARNING! THIS WILL DELETE ANY DATA INSIDE THE DATABASE!

To access the database on MySql Workbench the required password for port 3306 is `nodos-pass`.


### Running the proxy
#### Creating a virtual environment
If you are doing this from within an IDE look for somewhere to change your python environment.<br>
If it is not immediately obvious what to do ask google how do use a venv in YOUR IDE.<br>
Opt for creating a new one when asked.<br>

If you are doing this at the command line, follow the following instructions.<br>
##### Windows (use powershell)
* First create the virtual environment by executing the command `python -m venv .venv`
* Activate the virtual environment `.\.venv\Scripts\Activate.ps1`

##### Linux
* First create the virtual environment by executing the command `python3 -m venv .venv`
* Activate the virtual environment `source ./.venv/bin/activate`

#### Executing the program
Once in a virtual environment you first need to install all of the python dependencies.<br>
To do this execute the command `pip install -r requirements.txt`.

Then to run the admin panel (which spawns the proxies) in one terminal execute the command `python src/main.py`.<br>

Out of the box, the proxy will not have any server to forward data to/from.<br>
An easy way to run a server to test with is with the `python -m http.server [PORT]` command.

Once the program is running view <http://localhost:8080/docs> to view the swagger documentation.<br>
