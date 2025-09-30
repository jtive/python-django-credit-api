# Django Personal Info API

A Django REST API for managing personal information including persons, addresses, and credit cards. This is a Python/Django port of the original .NET PersonalInfoApi.

## Features

- **Person Management**: Create, read, update, and delete person records
- **Address Management**: Manage addresses associated with persons
- **Credit Card Management**: Handle credit card information with masking
- **Data Masking**: Automatic masking of sensitive information in API responses
- **Rate Limiting**: Built-in rate limiting for write operations
- **Health Checks**: Health and readiness endpoints for monitoring
- **PostgreSQL Support**: Full PostgreSQL database integration
- **Docker Support**: Containerized deployment ready

## API Endpoints

### Persons
- `GET /api/person/` - List all persons
- `POST /api/person/` - Create a new person
- `GET /api/person/{id}/` - Get person by ID
- `PUT /api/person/{id}/` - Update person
- `DELETE /api/person/{id}/` - Delete person

### Addresses
- `GET /api/address/person/{person_id}/` - List addresses for a person
- `POST /api/address/person/{person_id}/` - Create address for a person
- `GET /api/address/{id}/` - Get address by ID (masked)
- `GET /api/address/{id}/unmasked/` - Get address by ID (unmasked)
- `PUT /api/address/{id}/` - Update address
- `DELETE /api/address/{id}/` - Delete address

### Credit Cards
- `GET /api/creditcard/person/{person_id}/` - List credit cards for a person
- `POST /api/creditcard/person/{person_id}/` - Create credit card for a person
- `GET /api/creditcard/{id}/` - Get credit card by ID
- `PUT /api/creditcard/{id}/` - Update credit card
- `DELETE /api/creditcard/{id}/` - Delete credit card

### Health Checks
- `GET /api/health/` - Health check with database connectivity
- `GET /api/health/ready/` - Readiness check

## Data Masking

The API automatically masks sensitive information in responses:

- **SSN**: Shows as `***-**-1234` (last 4 digits)
- **Address**: Shows first 2 characters, rest masked
- **City**: Shows first character, rest masked
- **State**: Completely masked
- **Zip Code**: Shows last 2 digits, rest masked
- **Country**: Completely masked
- **Credit Card**: Shows as `****1234` (last 4 digits)

## Rate Limiting

- **Write Operations**: Limited to 1000 requests per day per IP
- **Read Operations**: No rate limiting
- **Reset Time**: Daily at midnight UTC

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Docker (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-credit-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Docker Development

1. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

## Deployment

### AWS App Runner via GitHub Actions

This project is configured for automatic deployment to AWS App Runner using GitHub Actions.

#### Required GitHub Secrets

Set the following secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_ACCOUNT_ID`: AWS account ID (12-digit number)
- `DJANGO_SECRET_KEY`: Django secret key for production
- `DB_HOST`: PostgreSQL host
- `DB_NAME`: Database name
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_PORT`: Database port (default: 5432)

#### Deployment Process

1. **Push to main branch**: The workflow automatically triggers on push to main
2. **ECR Repository**: Creates `personal-info-django-api` repository
3. **Docker Build**: Builds and pushes Docker image to ECR
4. **App Runner Service**: Creates or updates App Runner service
5. **Health Check**: Verifies deployment success

#### Manual Deployment

If you prefer manual deployment:

1. **Build and push to ECR**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
   
   # Build and push
   docker build -t personal-info-django-api .
   docker tag personal-info-django-api:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/personal-info-django-api:latest
   docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/personal-info-django-api:latest
   ```

2. **Create App Runner service** using the AWS Console or CLI

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DB_HOST` | Database host | Required |
| `DB_NAME` | Database name | `personalinfo` |
| `DB_USERNAME` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | Required |
| `DB_PORT` | Database port | `5432` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per day | `1000` |
| `RATE_LIMIT_WINDOW_HOURS` | Rate limit window | `24` |

### CORS Configuration

The API is configured to allow requests from:
- Local development servers (localhost:3000, localhost:5000, etc.)
- AWS App Runner domains (*.awsapprunner.com)
- Custom domains as needed

## Database Schema

### Person
- `id`: UUID primary key
- `first_name`: String (max 100 chars)
- `last_name`: String (max 100 chars)
- `birth_date`: Date
- `ssn`: String (max 11 chars, optional)
- `created_at`: DateTime
- `updated_at`: DateTime

### Address
- `id`: UUID primary key
- `person_id`: Foreign key to Person
- `address_type`: String (Home, Work, Mailing)
- `street_address`: String (max 200 chars)
- `city`: String (max 100 chars)
- `state`: String (2 chars)
- `zip_code`: String (max 10 chars)
- `country`: String (2 chars, default: US)
- `is_primary`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

### CreditCard
- `id`: UUID primary key
- `person_id`: Foreign key to Person
- `card_type`: String (Visa, MasterCard, etc.)
- `last_four_digits`: String (4 chars)
- `expiration_month`: Integer (1-12)
- `expiration_year`: Integer (2024-2030)
- `is_active`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

## Development

### Type Checking
This project uses mypy for static type checking. To run type checking:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run type checking
mypy --config-file mypy-basic.ini api/
```

### Code Quality
The project includes several development tools:

- **mypy**: Static type checking
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **pytest**: Testing framework

## Testing

### Run Tests
```bash
python manage.py test
```

### API Testing
Use the health check endpoint to verify the API is working:
```bash
curl https://your-app-url/api/health/
```

## Monitoring

### Health Checks
- **Health**: `/api/health/` - Returns service status and database connectivity
- **Readiness**: `/api/health/ready/` - Returns service readiness status

### Logging
The application logs to stdout with structured logging for easy monitoring in cloud environments.

## Security

- **Data Masking**: Sensitive data is automatically masked in API responses
- **Rate Limiting**: Prevents abuse with configurable rate limits
- **CORS**: Configured for specific allowed origins
- **Environment Variables**: Sensitive configuration via environment variables
- **Non-root Container**: Runs as non-root user in Docker

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
