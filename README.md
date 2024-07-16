# Pokemon API

This project implements a RESTful API using FastAPI to serve a list of Pokémon data fetched from the PokeAPI and stored in a PostgreSQL database.

## Setup Instructions

### Prerequisites

- Python 3.7+
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pokemon-api.git
   cd pokemon-api


2. Install dependencies:
   pip install -r requirements.txt

3. Set up PostgreSQL database:

    Create a PostgreSQL database named Pokemon_db.
    Update the database connection string in config.py with your credentials.

4. Run the migration to create the database tables:
    python migrate.py

5. Fetch Pokémon data from PokeAPI and store in the database and run app:
    uvicorn main:app 