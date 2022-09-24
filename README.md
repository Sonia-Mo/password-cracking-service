<p align="center">
<img src="https://media.cybernews.com/images/featured/2020/08/password-cracking-techniques-1.jpg" width="500" height="150" />
</p>

# Password Cracking Service

The service receives a file containing MD5 hashes and outputs the cracked password (which is always a phone number 05X-XXXXXXX).

## Installation instructions:

**<u>Run this project:</u>**

Start by cloning the repository:

`git clone https://github.com/Sonia-Mo/password-cracking-service.git`

cd into the project:

`cd password-cracking-service`

Now run the application stack using docker-compose:

`docker-compose up -d --build`

Then navigate to [http://localhost:80/docs](http://localhost:80/docs) to explore the API using the Swagger UI interface.

 **<u>Remove the stack using:</u>**

`docker-compose down -v`
## Technological stack:

* [FastAPI](https://fastapi.tiangolo.com/) - Web framework for building APIs with Python based on standard Python type hints.
* [Docker](https://www.docker.com/) - Containerization technology that enables the creation and use of Linux containers.
* [Ray](https://www.ray.io/) - Open-source unified compute framework which ease the build of scalable, distributed systems in Python in a cloud-agnostic way.

## Folder structure:
    password-cracking-service/
    ├── app/
    │   ├── routers/
    │   │    └── input_processing.py
    │   ├── tests/
    │   │    └── test_app.py
    │   ├── main.py
    │   └── exceptions.py
    ├── Dockerfile
    ├── docker-compose.yaml
    ├── requirements.txt
    ├── README.md
    └── .gitignore

The main logic of the service resided in `input_processing.py` file.
## Implementation process in detail:
As part of the requirements, I was asked that the communication between the master server and the minion servers would be **RESTful**, meaning based on HTTP requests. I understood that this could be implemented by using a clustering orchestration tool. For that purpose, I have created a docker image that would define the environment of each container in the cluster.

For distributing the work between the machines in the cluster I have used `Ray` library which serves for building and scaling distributed applications.

Rays API (RESTful) allows to define tasks that are done by the workers:

> Ray lets you run functions as remote tasks in the cluster. To do this, you decorate your function with`@ray.remote`to declare that you want to run this function remotely. Then, you call that function with`.remote()`instead of calling it normally. This remote call yields a future, a so-called Ray *object reference*, that you can then fetch with`ray.get`.
> 
> [see documentation](https://docs.ray.io/en/latest/ray-core/walkthrough.html#running-a-task)

Ray also takes cares of the **crash handling** for us:

> When a worker is executing a task, if the worker dies unexpectedly, either because the process crashed or because the machine failed, Ray will rerun the task until either the task succeeds or the maximum number of retries is exceeded.
>
> [see documentation](https://docs.ray.io/en/releases-1.11.0/ray-core/fault-tolerance.html#tasks)

Unfortunately, I could not find a free cluster management and cloud deployment tools so currently the service initializes Ray locally only on one machine. Which means that at the moment, the service can handle a small number of hashes as input (for each hash it takes about a minute or two until a result is returned).

### <u>Testing:</u>

In order to test the entire application, I used **`pytest`** and **`httpx`** libraries to create a fictitious client that sends requests to the application.
    
The application was requested with the following files:

  1. A file with only one **correct hash**.

  2. An **empty file**.

  3. A file with the hash that corresponds to a password that is **not a phone number**.

  4. A file that contains bytes which are **not an MD5 hash**.

    
Of the four tests, tests (2) and (4) passed while tests (1) and (3) failed and an unexpected result was obtained. I tested the same cases by running the application itself and in this case the behavior was as it should be.
    What differentiates these cases is that in order to get a correct result in them a proper running of **`Ray`** is required, while in the other two cases the result is obtained before running the library. 
I tried to run a test in order to test Ray's remote function and indeed I realized that during the test run, the function does not return the expected value (while as mentioned above, when running the application itself, the desired value is indeed obtained).

Following that, I realized that in (1) and (3) cases the remote function of Ray returns `None` instead of the desired value. Apparently there is a problem running these types of tests with Ray. Unfortunately, I do not have enough time left to look into this matter in depth.

---
## Optional features and optimisations:
- In case one of the minions finds the password of a certain hash, the minion would send a request back to the master server, and he would in turn send requests to the other minions and instruct them to stop checking the relevant hash. This way, we would have more free resources available for cracking the other hashes.


- Make a **rainbow table** - The service would prepare an hash table as part of the service initialization process. The keys of this table would be all the hashes that correspond to 05X-XXXXXXX and the value of each key would be the matching password. When the service gets a request, it would immediately check if the hashes are present in this table.
    
    This solution improves the running time, but there is a trade-off here with the required memory since now we have to keep a table containing all the hashes for all possible passwords.


- We will note that the calculation for the different hashes is independent, so we can process several hashes at the same time in addition to the parallel processing of the different ranges of phone numbers.
