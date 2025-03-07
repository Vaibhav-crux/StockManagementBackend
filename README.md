# Stock Portfolio Management API

## **Overview**
The **Stock Portfolio Management** project is designed with a **Service-Oriented Architecture (SOA)** approach with **async RESTful API**, ensuring modularity, scalability, and maintainability. Built using modern technologies such as **Python**, **FastAPI**, **Docker**, **PostgreSQL**, **Redis**, and **WebSocket**, this application provides a robust platform for managing stock portfolios, tracking investments, and performing real-time analysis.

### **API Access**

For API testing, import the provided **Insomnia** file:  
📂 **File Name:** `stock_market_analysis_v1`

### **Key Highlights**
1. **Service-Oriented Architecture (SOA)**:
   - The application is divided into independent services (e.g., user management, portfolio tracking, quality checks) that communicate via well-defined APIs.
   - This modular design allows for easy scaling, maintenance, and integration with other systems.

2. **Real-Time Updates**:
   - Utilizes **WebSocket** to provide real-time updates on stock prices and portfolio changes.
   - Enables users to monitor their investments and make informed decisions without manual refreshes.

3. **Data Management**:
   - **PostgreSQL** is used as the primary database for storing structured data such as user information, orders, and portfolio details.
   - **Redis** is employed for caching frequently accessed data (e.g., purchased orders) and managing WebSocket connections, ensuring high performance and low latency.

4. **Security and Authentication**:
   - Implements **JWT (JSON Web Tokens)** for secure user authentication and authorization.
   - Ensures that only authenticated users can access sensitive endpoints and perform actions like placing orders or viewing portfolios.

5. **Performance Optimization**:
   - Uses **GZIP compression** to reduce the size of API responses, improving load times and reducing bandwidth usage.
   - Implements **rate limiting** and **timeout handling** to prevent abuse and ensure the application remains responsive under high traffic.

6. **Quality Assurance**:
   - Performs automated **quality checks** on purchased orders to flag potential issues such as invalid prices, quantities, or timestamps.
   - Provides actionable insights to users, helping them maintain accurate and reliable portfolio data.

7. **Scalability and Deployment**:
   - The application is containerized using **Docker**, making it easy to deploy and scale across different environments (e.g., development, staging, production).
   - **Docker Compose** is used to manage multi-container setups, including the application, database, and Redis.

8. **User-Friendly API**:
   - The API follows RESTful principles and provides clear, consistent endpoints for managing users, orders, portfolios, and more.
   - Includes comprehensive documentation (e.g., Swagger UI) for easy integration and testing.

---

### **Technologies Used**
- **Backend**: Python, FastAPI
- **Database**: PostgreSQL
- **Caching**: Redis
- **Real-Time Communication**: WebSocket
- **Containerization**: Docker, Docker Compose
- **Authentication**: JWT (JSON Web Tokens)
- **Middleware**: CORS, GZIP compression, rate limiting, timeout handling, logging, error handling


### Key Features
- **User authentication** with JWT tokens
- **Real-time ticker updates** via WebSocket
- **Cache implementation** with Redis
- **PostgreSQL Database** implementation
- **Portfolio tracking** with profit/loss calculations
- **Quality checks** to flag potential issues in orders

### **Environment Variables & GitHub Actions**  
If there are any additions or changes in the `.env` files:  
1. **Update the GitHub Actions workflow**: Modify `.github/workflows/deploy.yml`.  
2. **Update GitHub Secrets**: Go to `Actions → Secrets` in the GitHub repository and update the necessary environment variables.  


## Table of Contents
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Tickers](#tickers)
  - [Orders](#orders)
  - [Portfolio](#portfolio)
  - [Quality Checks](#quality-checks)
  - [WebSocket](#websocket)
- [Services Folder](#services-folder)
  - [Portfolio Service](#portfolio-service)
  - [Purchased Orders Service](#purchased-orders-service)
  - [Quality Check Service](#quality-check-service)
  - [Tick Service](#tick-service)
  - [User Service](#user-service)
- [Middleware Folder](#middleware-folder)
  - [CORS](#cors)
  - [Error Handler](#error-handler)
  - [GZIP Compression](#gzip-compression)
  - [JWT Authentication](#jwt-authentication)
  - [Logger](#logger)
  - [Rate Limiting](#rate-limiting)
  - [Timeout](#timeout)

## Project Structure
```
stock-portfolio-api/  # Code Block Start
│
├── .gitignore                 # Git ignore configuration file  # Vertical Bar, Branch, Inline Comment
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image configuration
├── read.txt                   # Additional readme information
├── requirements.txt           # Python dependencies
│
├── .github/
│   ├── workflows/             # Version 1 of the API
│   │   ├── deploy.yml
│
├── app/                       # Main application directory
│   ├── main.py                # Entry point for the application
│   ├── server.py              # Server setup
│   ├── init.py            # Package initialization
│   │
│   ├── api/                   # API routes and handlers
│   │   ├── v1/                # Version 1 of the API
│   │   │   ├── portfolio_router.py        # Portfolio API routes
│   │   │   ├── purchased_orders_router.py # Purchased Orders API routes
│   │   │   ├── quality_check_router.py    # Quality Check API routes
│   │   │   ├── tick_router.py             # Tick API routes
│   │   │   ├── user_router.py             # User API routes
│   │   │   └── init.py                # Version 1 initialization
│   │
│   ├── config/                # Configuration files (DB, Redis, etc.)
│   │   ├── db_connection.py           # DB connection settings
│   │   ├── development_db.py          # Development database settings
│   │   ├── production_db.py           # Production database settings
│   │   ├── redis_client_connection.py # Redis client configuration
│   │
│   ├── middleware/              # Middleware for various purposes
│   │   ├── cors.py              # CORS middleware
│   │   ├── error_handler.py     # Error handler middleware
│   │   ├── gzip.py              # GZIP compression middleware
│   │   ├── jwt.py               # JWT authentication middleware
│   │   ├── logger.py            # Logger middleware
│   │   ├── rate_limit.py        # Rate limiting middleware
│   │   ├── timeout.py           # Timeout middleware
│   │   ├── websocket_manager.py # WebSocket manager
│   │
│   ├── services/              # Business logic services
│   │   ├── v1/                # Version 1 of the services
│   │   │   ├── portfolio_service.py        # Portfolio service logic
│   │   │   ├── purchased_orders_service.py # Purchased Orders service logic
│   │   │   ├── quality_check_service.py    # Quality Check service logic
│   │   │   ├── tick_service.py             # Tick service logic
│   │   │   ├── user_service.py             # User service logic
│   │   │   └── init.py                 # Version 1 initialization
│   │
│   ├── utils/                 # Utility functions
│   │   ├── base_model.py      # Base model utility
│   │   ├── extract_zip.py     # Utility to extract ZIP files
│   │   ├── process_csv.py     # Utility to process CSV files
│   │   ├── save_csv_data.py   # Utility to save CSV data
│   │
│   ├── core/                  # Core functionality
│   │   ├── ssl/               # SSL certificates
│   │   │   ├── ca-cert.pem    # CA certificate
│   │
│   ├── db/                    # Database-related files
│   │   ├── session.py         # Database session management
│   │   ├── models/            # Database models
│   │   │   ├── orders.py      # Orders model
│   │   │   ├── purchased_orders.py # Purchased Orders model
│   │   │   ├── ticks.py       # Ticks model
│   │   │   ├── users.py       # Users model
│   │   │   └── init.py    # Models initialization
│   │
│   ├── schemas/               # Data schemas
│   │   ├── base.py            # Base schema
│   │   ├── order.py           # Order schema
│   │   ├── purchased_order.py # Purchased Order schema
│   │   ├── portfolio.py       # Portfolio schema
│   │   ├── quality_check.py   # Quality check schema
│   │   ├── tick.py            # Tick schema
│   │   ├── user.py            # User schema
│   │
│   └── init.py            # App package initialization
│
├── tests/                     # Unit and integration tests
│   ├── test_database_connection.py  # DB connection tests
│   ├── test_websocket.py      # WebSocket functionality tests
│   ├── generate_jwt.py        # Generate Random Text
│   ├── session_connection_test.py # Test db connection
│   ├── monitor.html           # Test Websocket in frontend
│
```

## Installation
### Clone the Repository:
```bash
git clone https://github.com/your-repository/stock-portfolio-api.git
cd stock-portfolio-api
```
### Create a Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### Install Dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Before running the application, configure the following:
- **Database**: Update settings in `app/config/db_connection.py`.
- **Redis**: Configure the Redis client in `app/config/redis_client.py`.
- **Environment Variables**: Set required variables in a `.env` file.

Example `.env` file:
```ini
# FastAPI Server
PORT=8000

# DB Config
PROD_DB_CONNECTION=postgres://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>?sslmode=require

DB_USER=<DB_USER>
DB_PASSWORD=<DB_PASSWORD>
DB_HOST=<DB_HOST>
DB_PORT=<DB_PORT>
DB_NAME=<DB_NAME>

# Set to 'development' or 'production'
DB_ENV=development

# Authentication Tokens
JWT_SECRET_KEY=<JWT_SECRET_KEY>
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30

# Redis Configuration
REDIS_HOST=<REDIS_HOST>
REDIS_PORT=<REDIS_PORT>
REDIS_USERNAME=default
REDIS_PASSWORD=<REDIS_PASSWORD>
```

---

## **Running the Application**

### Extracting File
  `python app/utils/extract_zip.py`

### Inserting Data to database
  Utilized batch insertion:
  `python -m app.utils.save_csv_data`
  
### With Docker
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the application at `http://localhost:8000`.

### Without Docker
1. Start the PostgreSQL and Redis services manually.
2. Run the FastAPI application:
   ```bash
   uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Access the application at `http://localhost:8000`.

---

## **Services Folder**

#### **1. `portfolio_service.py`**
- **Purpose**: This service handles the calculation of a user's portfolio positions.
- **Functionality**:
  - Fetches all purchased orders for a specific user.
  - Groups orders by ticker symbol and calculates the total quantity and cost for each symbol.
  - Fetches the latest price for each symbol from the `Orders` table.
  - Computes the average price, current price, and profit/loss (PnL) for each symbol.
  - Returns a summary of the user's portfolio positions, including total PnL.

---

#### **2. `purchased_orders_service.py`**
- **Purpose**: This service manages operations related to purchased orders.
- **Functionality**:
  - Validates the user's token and retrieves the current user.
  - Places a new order for a specific ticker and records it in the `PurchasedOrders` table.
  - Fetches all purchased orders for a user, with optional pagination and caching.
  - Invalidates the cache when a new order is placed to ensure data consistency.

---

#### **3. `quality_check_service.py`**
- **Purpose**: This service performs quality checks on a user's purchased orders.
- **Functionality**:
  - Fetches all purchased orders for a specific user.
  - Performs quality checks such as validating purchase price, purchase quantity, and order timestamp.
  - Flags issues like invalid purchase prices, negative quantities, or future timestamps.
  - Returns a summary of flagged issues along with their severity.

---

#### **4. `tick_service.py`**
- **Purpose**: This service handles operations related to tickers and orders.
- **Functionality**:
  - Fetches a list of tickers with optional filters like search, date range, and pagination.
  - Retrieves orders for a specific ticker, with optional interval filtering.
  - Aggregates tick data into OHLC (Open, High, Low, Close) format for a specific ticker.
  - Updates tickers via WebSocket and broadcasts the updated data to connected clients.

---

#### **5. `user_service.py`**
- **Purpose**: This service manages user-related operations such as signup, login, and authentication.
- **Functionality**:
  - Creates a new user with a hashed password and stores it in the database.
  - Authenticates a user by verifying their email and password.
  - Issues a JWT token upon successful signup or login.
  - Handles errors like duplicate email registration or invalid credentials.

---

## Authentication

### Signup
- **POST** `/api/v1/users/signup`
  - **Description**: Register a new user.
  - **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "jwt_token",
      "token_type": "bearer"
    }
    ```

### Login
- **POST** `/api/v1/users/login`
  - **Description**: Authenticate a user and return a JWT token.
  - **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "jwt_token",
      "token_type": "bearer"
    }
    ```

## Tickers

### Get Tickers
- **GET** `/api/v1/tickers`
  - **Description**: Retrieve a list of tickers with optional search and date filtering.
  - **Query Parameters**:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)
    - `search`: Search term for ticker symbols
    - `start_date`: Start date for filtering (format: DD-MM-YYYY)
    - `end_date`: End date for filtering (format: DD-MM-YYYY)
  - **Response**:
    ```json
    {
      "tickers_with_dates": [
        {
          "id": "uuid",
          "ticker": "AAPL",
          "dates": ["05-04-2022"],
          "sellqty": 100,
          "sellprice": 150.0,
          "ltp": 155.0,
          "ltq": 200,
          "latest_timestamp": "2022-04-05T10:00:00"
        }
      ],
      "total": 1,
      "skip": 0,
      "limit": 100
    }
    ```

### Get Orders by Ticker ID
- **GET** `/api/v1/tickers/{tick_id}`
  - **Description**: Retrieve orders for a specific ticker.
  - **Query Parameters**:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)
    - `interval`: Time interval in minutes to filter orders from current time
  - **Response**:
    ```json
    {
      "ticker": "AAPL",
      "orders": [
        {
          "id": "uuid",
          "ltp": 155.0,
          "sellprice": 150.0,
          "sellqty": 100,
          "ltq": 200,
          "openinterest": 0,
          "tick_id": "uuid",
          "buyprice": 150.0,
          "buyqty": 100,
          "timestamp": "2022-04-05T10:00:00",
          "date": "05/04/2022",
          "time": "10:00:00"
        }
      ],
      "total": 1,
      "skip": 0,
      "limit": 100,
      "interval": null
    }
    ```

### Get OHLC Data
- **GET** `/api/v1/ohlc`
  - **Description**: Retrieve OHLC (Open-High-Low-Close) data for a specific ticker.
  - **Query Parameters**:
    - `ticker`: Ticker symbol to fetch OHLC data for
    - `start_date`: Start date for filtering (format: DD-MM-YYYY)
    - `end_date`: End date for filtering (format: DD-MM-YYYY)
  - **Response**:
    ```json
    [
      {
        "ticker": "AAPL",
        "date": "2022-04-05",
        "open": 150.0,
        "high": 155.0,
        "low": 149.0,
        "close": 154.0
      }
    ]
    ```

## Orders

### Place Order
- **POST** `/api/v1/place-order`
  - **Description**: Place a new order.
  - **Request Body**:
    ```json
    [
      {
        "tick_id": "uuid",
        "purchase_price": 150.0,
        "purchase_qty": 100
      }
    ]
    ```
  - **Response**:
    ```json
    [
      {
        "id": "uuid",
        "user_id": "uuid",
        "tick_id": "uuid",
        "purchase_price": 150.0,
        "purchase_qty": 100,
        "timestamp": "2022-04-05T10:00:00"
      }
    ]
    ```

### Get Purchased Orders
- **GET** `/api/v1/orders/purchased`
  - **Description**: Retrieve purchased orders for the authenticated user.
  - **Query Parameters**:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)
  - **Response**:
    ```json
    {
      "orders": [
        {
          "id": "uuid",
          "user_id": "uuid",
          "tick_id": "uuid",
          "purchase_price": 150.0,
          "purchase_qty": 100,
          "timestamp": "2022-04-05T10:00:00"
        }
      ],
      "total": 1,
      "skip": 0,
      "limit": 100
    }
    ```

## Portfolio

### Get Portfolio Position
- **POST** `/api/v1/portfolio-position`
  - **Description**: Retrieve the portfolio positions for the authenticated user.
  - **Response**:
    ```json
    {
      "user_id": "uuid",
      "positions": [
        {
          "symbol": "AAPL",
          "quantity": 100,
          "average_price": 150.0,
          "current_price": 155.0,
          "pnl": 500.0,
          "timestamp": "2022-04-05T10:00:00"
        }
      ],
      "total_pnl": 500.0
    }
    ```

## Quality Checks

### Get Quality Checks
- **GET** `/api/v1/quality-checks`
  - **Description**: Perform quality checks on the user's orders and return flagged issues.
  - **Response**:
    ```json
    {
      "user_id": "uuid",
      "issues": [
        {
          "issue_id": "uuid",
          "description": "Invalid purchase price for order_id=uuid",
          "severity": "high",
          "timestamp": "2022-04-05T10:00:00"
        }
      ],
      "total_issues": 1,
      "timestamp": "2022-04-05T10:00:00"
    }
    ```

## WebSocket

### WebSocket Tickers
- **WebSocket** `/api/v1/tickers/ws`
  - **Description**: Establish a WebSocket connection to receive real-time ticker updates.
  - **Response**:
    ```json
    {
      "tickers_with_dates": [
        {
          "id": "uuid",
          "ticker": "AAPL",
          "dates": ["05-04-2022"],
          "sellqty": 100,
          "sellprice": 150.0,
          "ltp": 155.0,
          "ltq": 200,
          "latest_timestamp": "2022-04-05T10:00:00"
        }
      ],
      "total": 1,
      "skip": 0,
      "limit": 100
    }
    ```

---

## **Middleware Folder**

---

### **1. `cors.py`**
- **Purpose**: Handles Cross-Origin Resource Sharing (CORS) for your API.
- **Functionality**:
  - Allows or restricts requests from different origins (domains) based on configuration.
  - Adds appropriate headers (`Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, etc.) to responses.
  - Ensures secure communication between the frontend and backend by controlling which domains can access your API.

---

### **2. `error_handler.py`**
- **Purpose**: Centralized error handling for the application.
- **Functionality**:
  - Catches and processes exceptions globally, ensuring consistent error responses.
  - Logs errors for debugging and monitoring purposes.
  - Returns user-friendly error messages with appropriate HTTP status codes (e.g., `400 Bad Request`, `500 Internal Server Error`).

---

### **3. `gzip.py`**
- **Purpose**: Implements GZIP compression for responses.
- **Functionality**:
  - Compresses HTTP responses to reduce payload size, improving performance.
  - Automatically applies compression to responses larger than a specified threshold (e.g., 1000 bytes).
  - Adds the `Content-Encoding: gzip` header to compressed responses.

---

### **4. `jwt.py`**
- **Purpose**: Manages JSON Web Token (JWT) authentication.
- **Functionality**:
  - Generates JWT tokens for authenticated users.
  - Validates JWT tokens in incoming requests to ensure the user is authenticated.
  - Extracts user information (e.g., user ID) from the token for use in downstream processing.
  - Handles token expiration and renewal.

---

### **5. `logger.py`**
- **Purpose**: Implements logging for the application.
- **Functionality**:
  - Logs incoming requests, responses, and errors for monitoring and debugging.
  - Configures log levels (e.g., `INFO`, `DEBUG`, `ERROR`) and log formats.
  - Integrates with external logging services or tools (e.g., ELK stack, Sentry) if needed.

---

### **6. `rate_limit.py`**
- **Purpose**: Implements rate limiting to prevent abuse of the API.
- **Functionality**:
  - Limits the number of requests a client can make within a specified time window (e.g., 100 requests per minute).
  - Uses Redis or an in-memory store to track request counts.
  - Returns a `429 Too Many Requests` response when the limit is exceeded.

---

### **7. `timeout.py`**
- **Purpose**: Implements request timeouts to prevent long-running requests from blocking the server.
- **Functionality**:
  - Sets a maximum duration for processing requests (e.g., 10 seconds).
  - Automatically cancels requests that exceed the timeout limit.
  - Returns a `504 Gateway Timeout` response for timed-out requests.

---

### **8. `websocket_manager.py`**
- **Purpose**: Manages WebSocket connections and communication.
- **Functionality**:
  - Establishes and maintains WebSocket connections with clients.
  - Manages the lifecycle of WebSocket connections (open, close, error handling).
  - Supports broadcasting messages to multiple clients or sending messages to specific clients.
  - Handles message validation, encoding, and decoding (e.g., handling JSON or binary data).
  - Ensures proper resource cleanup and handles unexpected disconnects.
  - Provides mechanisms for integrating with other application services (e.g., notifications, real-time updates).