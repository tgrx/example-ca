# Example: Clean Architecture

My vision of Clean Architecture.


## How to use

### Docker

1. copy `.env.sample` to `.env`
2. run `docker compose up -d`
3. go to [http://localhost:8000](http://localhost:8000)

### Local

As usual, you must set up system libs and Python venv. Let's skip this for now.
Assuming you're already know how to do it and you have your toolchain set.

To run tests, you must:

1. start db container: `task docker-up -- postgres`.
2. check `.env`: `WEBAPP_PRIMARY_DATABASE_URL` must point to `localhost:5432`.
3. check `.env`: `WEBAPP_TEST_URL` must point to `localhost:8000`.
4. apply migratios: `task db-migrate`.
5. start development server: `task run-server-dev`.
6. in another terminal, enjoy your tests: `task f l t`.
