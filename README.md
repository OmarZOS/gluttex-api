
## Document storage server
## Table of Contents

- Table of Contents
  - Description
  - Folder hierarchy
  - Deploying
    - Docker
    - Development
  - Progress

### Description


### Folder hierarchy

        ├── core
        |  # base component for the server
        ├── features
        |  # each set of features is implemented in a folder
        └── storage
            ├── storage_service
            | # an abstraction for storage engines
            └── wrappers
            | # the implementation to handle 3rd party storage.

### Deploying

#### Docker

You can use docker-compose to build and deploy the containers:

    sudo docker compose up -d



#### Development
Connect to the container 

    sudo docker exec -it gluttex-db mysql -u root gluttex -p

Create a user that can access from anywhere:

    CREATE USER 'dev_user'@'%' IDENTIFIED BY 'dev_password';
    GRANT ALL PRIVILEGES ON *.* TO 'dev_user'@'%';
    FLUSH PRIVILEGES;
    exit;

To generate the `models.py` file, you can execute the following instruction:

    sudo docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' gluttex-db

    sqlacodegen --outfile=server/core/models.py   mysql+pymysql://dev_user:dev_password@[$MYSQL_HOST]/gluttex



### Progress
    
- Serving feature. ![x](https://us-central1-progress-markdown.cloudfunctions.net/progress/90)
  - Product.
    - Ordering Products.
    - Polling to monitor `quantity` changes.
  - Category.
  - Supplier.
  - App user.
- Auth server. ![x](https://us-central1-progress-markdown.cloudfunctions.net/progress/60)
  - App user creation.
  - Logging in feature.
  - Changing password.
  - ssl certificate (locally generated).
- [x] 3rd Party storage solutions. ![](https://us-central1-progress-markdown.cloudfunctions.net/progress/70)
  - [x] SQL based storage.
  - [x] SQLITE based authentication.
- [x] Containerisation. ![](https://us-central1-progress-markdown.cloudfunctions.net/progress/90)
  - [x] Automation of deployment. (docker-compose)
  - [x] Smaller footprint.



<!-- >## NOTES: -->
>  
> 