# E-Wallet

### About
E-Wallet Project is a RESTful API application designed for managing electronic wallets.
It provides users with the ability to:
- Create and manage personal wallets
- Top up wallet balances
- Check current balance
- Withdraw funds
- Perform wallet-to-wallet transfers

The system ensures secure and efficient handling of wallet operations, making it suitable for integration with financial platforms or as a standalone digital wallet solution.

## Configuration
Configuration is stored in `.env`, for examples see `.env.example`

## Installing on a local machine
This project requires python 3.11. Python virtual environment should be installed and activated.
 Dependencies are managed by [poetry](https://python-poetry.org/) with requirements stored in `pyproject.toml`.

Install requirements:

```bash
poetry install
```

### Docker
Then run the following command in the same directory as the `docker-compose.yml` file to start the container.
`docker compose up -d`

### Sending email
To use sending email, you should set up RUN_CELERY=True. Also, run redis by the command

`docker run -d -p 6379:6379 redis`

Testing:
```bash
# run lint
make lint

# run unit tests
make test
```
