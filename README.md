# Patient Encounter System

A simple FastAPI app for managing patient appointments with doctors.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to see the API documentation.

## Running tests

```bash
# Unit tests (95% coverage)
pytest tests/unit/ -v --cov=src

# Integration tests (need server running first)
pytest tests/test_*.py -v -s
```

## Tech stack

- FastAPI for the API
- SQLAlchemy for database stuff
- Pydantic for validation
- pytest for testing
- MySQL in production, SQLite for tests

## Key features

**Appointment conflict detection** - checks if doctor is already booked  
**Timezone-aware datetimes** - everything uses UTC  
**Database constraints** - can't delete doctors/patients with existing appointments  
**Validation** - appointment duration must be 15-180 minutes

## API Endpoints

```
POST   /patients              Create patient
GET    /patients/{id}         Get patient by ID

POST   /doctors               Create doctor
GET    /doctors/{id}          Get doctor by ID
PUT    /doctors/{id}          Update doctor

POST   /appointments          Schedule appointment
GET    /appointments          List appointments by date
```

## Development

Code quality checks:
```bash
ruff check src tests       # Linting
black --check src tests    # Formatting
bandit -r src tests        # Security
```

CI/CD runs automatically on push via GitHub Actions.
