from backend.database import Base, engine
from backend.models import Test

Base.metadata.create_all(engine)

print("Database tables created!")