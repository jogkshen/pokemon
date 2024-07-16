# main.py

import logging
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from fastapi import FastAPI, Depends
from app.models import Base, Pokemon
from app.config import DATABASE_URL, POKEAPI_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Create async SQLAlchemy engine with asyncpg
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Dependency to get async database session
async def get_session():
    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True
    )
    async with async_session() as session:
        yield session

# Ensure tables are created when starting the application
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Function to fetch and store Pokemon data
async def fetch_pokemons():
    try:
        async with httpx.AsyncClient() as client:
            # Fetch Pokemon data from PokeAPI
            response = await client.get(f"{POKEAPI_BASE_URL}pokemon?limit=200")
            response.raise_for_status()  # Raise HTTP error if response is not successful
            
            data = response.json()
            pokemon_urls = [(pokemon['name'], pokemon['url']) for pokemon in data['results']]

            # Store fetched Pokemon data into database
            async with get_session() as session:
                for name, url in pokemon_urls:
                    pokemon_data = await client.get(url)
                    pokemon_data.raise_for_status()
                    
                    pokemon_info = pokemon_data.json()
                    types = [type['type']['name'] for type in pokemon_info['types']]
                    image_url = pokemon_info['sprites']['front_default']
                    
                    db_pokemon = Pokemon(name=name, image_url=image_url, types=types)
                    session.add(db_pokemon)
                
                await session.commit()
                logging.info("Pokemon data fetched and stored successfully.")
    
    except httpx.HTTPStatusError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

# FastAPI endpoint to fetch pokemons

@app.get("/api/v1/pokemons")
async def get_pokemons(name: str = None, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Pokemon)
        if name:
            query = query.where(Pokemon.name.ilike(f"%{name}%"))
        
        result = await session.execute(query)
        pokemons = result.scalars().all()  # Fetch all rows as SQLAlchemy objects
        
        return pokemons
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": "An error occurred while fetching pokemons"}

# FastAPI startup event to create tables and fetch Pokemon data
@app.on_event("startup")
async def startup_event():
    await create_tables()
    await fetch_pokemons()

# Example with a different port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)

