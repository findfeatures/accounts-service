# Accounts Service

The accounts service looks after:
- Users
- Organizations
- Billing
- Authentication

# Installation
(To install a pyenv virtualenv)
```bash
pyenv virtualenv -p python3.6 3.6.8 accounts-service
```

Install the requirements into your virtualenv
```bash
pip install -e ".[dev]"
```

Run Unit Test
```bash
Make test
```

To run the service
```bash
Make run
```
