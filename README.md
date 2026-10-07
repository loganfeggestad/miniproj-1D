# CSC4201 Catalog Service

Catalog microservice for the CSC4201 ecommerce mini-project.

The Catalog Service provides information about products available in the ecommerce application. Product information is stored separately from the application code using SQLite.

## Features

* Get all products
* Search products by name or description
* Get an individual product by ID
* SQLite product storage
* Unit tests with pytest
* Docker support
* GitHub Actions CI
* Google Cloud Run deployment

## Project Structure

```text
catalog-service/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   └── test_products.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API

### Get All Products

```http
GET /products
```

Returns all products in the catalog.

Example:

```text
http://localhost:8000/products
```

### Search Products

```http
GET /products?search=<search-term>
```

Searches both the product name and description.

Example:

```text
http://localhost:8000/products?search=mouse
```

Search is case-insensitive.

### Get a Product

```http
GET /products/{product_id}
```

Returns a single product by its ID.

Example:

```text
http://localhost:8000/products/1
```

If the product does not exist, the service returns HTTP `404`.

## Example Product

```json
{
  "product_id": 1,
  "name": "Wireless Mouse",
  "description": "A wireless optical mouse for desktop and laptop computers.",
  "price": 24.99,
  "categories": [
    "electronics",
    "computer-accessories"
  ]
}
```

## Running Locally

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the service:

```powershell
uvicorn app.main:app --reload
```

The service will be available at:

```text
http://localhost:8000
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## Running Tests

Run the unit tests from the project root:

```powershell
python -m pytest
```

The tests cover:

* Returning all products
* Searching by product name
* Searching by product description
* Case-insensitive searching
* Searches with no results
* Retrieving an individual product
* Handling nonexistent products

## Running with Docker

Build and start the service:

```powershell
docker compose up --build
```

The service will be available at:

```text
http://localhost:8000
```

The interactive API documentation will be available at:

```text
http://localhost:8000/docs
```

Stop the Docker container with:

```text
Ctrl+C
```

## Google Cloud Run

The service can be deployed to Google Cloud Run using the Google Cloud CLI.

### Authenticate with Google Cloud

```powershell
gcloud auth login
```

Set the Google Cloud project:

```powershell
gcloud config set project miniproj-1d
```

### Enable Required Services

```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Create the Artifact Registry Repository

```powershell
gcloud artifacts repositories create catalog-repo `
    --repository-format=docker `
    --location=us-central1 `
    --description="CSC4201 Catalog Service"
```

If the repository already exists, this step does not need to be repeated.

Configure Docker authentication:

```powershell
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Build the Docker Image

From the project root:

```powershell
docker build -t us-central1-docker.pkg.dev/miniproj-1d/catalog-repo/catalog-service:latest .
```

### Push the Image

```powershell
docker push us-central1-docker.pkg.dev/miniproj-1d/catalog-repo/catalog-service:latest
```

### Deploy to Cloud Run

```powershell
gcloud run deploy catalog-service `
    --image us-central1-docker.pkg.dev/miniproj-1d/catalog-repo/catalog-service:latest `
    --region us-central1 `
    --allow-unauthenticated
```

After deployment, Google Cloud Run will provide a service URL similar to:

```text
https://catalog-service-xxxxxxxxxx-uc.a.run.app
```

The API can then be accessed using:

```text
https://catalog-service-xxxxxxxxxx-uc.a.run.app/products
```

The interactive API documentation is available at:

```text
https://catalog-service-xxxxxxxxxx-uc.a.run.app/docs
```

### Delete the Cloud Run Service

If the service is no longer needed:

```powershell
gcloud run services delete catalog-service --region us-central1
```

Deleting the Cloud Run service does not delete the Docker image stored in Artifact Registry.

## CI Pipeline

GitHub Actions automatically runs the unit tests when code is pushed to GitHub or when a pull request is created.

The workflow is located at:

```text
.github/workflows/ci.yml
```

The pipeline:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs pytest

## Technology

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* pytest
* Docker
* GitHub Actions
* Google Cloud Run
* Google Artifact Registry
