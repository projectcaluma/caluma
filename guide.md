# Caluma: Guide

## About this guide

Goals:
- get a simple app running
- understand concepts behind caluma
  - build a form
  - design a simple workflow

## Installation

To install Caluma, you'll need to have [Docker]() and [docker-compose]() installed on your system.

Afterwards, create a new directory for your project, copy our [example docker-compose.yml file](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) into it and finally run the following command:

Per default, Caluma is running with production settings. To bypass the security-related configuration steps needed for a prodoction system, create a new file called `docker-compose.override.yml` with the following content:

```yml
version: "3.4"
services:
  caluma:
    environment:
      - ENV=development
```

Afterwards, start the containers by running

```bash
docker-compose up -d
```

You can now access [GraphiQL](https://github.com/graphql/graphiql) at [http://localhost:8000/graphql](http://localhost:8000/graphql). We'll use graphiql to interact with the Caluma service in the coming sections.
