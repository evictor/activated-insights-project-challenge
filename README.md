# Activated Insights Project Challenge

### Guidelines

This project is designed to assess your ability to look critically at a coding problem from a standpoint of optimization and architectural design, and covers some of the flows that exist in the platform you would work on at Activated Insights.

Your project will be evaluated on:

- Completeness. Your code should fulfill the requirements as if they will be run on production.
- Efficiency of file ingestion and API (considering CPU/memory constraints)
- Organization
- Code Clarity

You will not be evaluated on:

- Writing tests
- Frontend or Data Visualization

There's no need to build any features beyond the listed requirements, we
will discuss future optimizations and error handling in the project debrief.

### Requirements

- Write a management command to ingest the file `coding_challenge_data.xlsx`. The file contains 20k rows of survey participant data.
- Add a task queue service to docker-compose (we use Celery).
- Process the file asynchronously using the task queue and store the data in a django database (the default SQLite is fine). You can assume that the data in the file is valid.
- Add graphql endpoint(s) to retrieve the data. You should be able to give us a graphql query to run in the graphiql explorer such that we can see
  - The total number of participants ingested.
  - A list of the unique departments, with the survey code and birth year for the first 10 participants in each department.

If you have any questions about the requirements, feel free to email us.

### Project Setup

Run the backend with docker-compose:

```
cd backend
docker-compose up --build
```

View the graphql explorer at
http://localhost:8000/graphql
