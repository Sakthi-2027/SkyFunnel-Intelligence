from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
DATABASE_PATH = "database/skyfunnel.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    num_passengers = Column(Integer)
    sales_channel = Column(String)
    trip_type = Column(String)
    purchase_lead = Column(Integer)
    length_of_stay = Column(Integer)
    flight_hour = Column(Integer)
    flight_day = Column(String)
    route = Column(String)
    booking_origin = Column(String)
    wants_extra_baggage = Column(Integer)
    wants_preferred_seat = Column(Integer)
    wants_in_flight_meals = Column(Integer)
    flight_duration = Column(Float)
    booking_complete = Column(Integer)

   
    is_last_minute_booking = Column(Integer)
    is_weekend_flight = Column(Integer)
    total_extras_selected = Column(Integer)
    route_popularity = Column(Integer)
    is_long_haul = Column(Integer)

def get_engine():
    engine = create_engine(DATABASE_URL, echo=False)
    return engine

def create_tables(engine):
    Base.metadata.create_all(engine)
    print(f"Table 'bookings' ready in {DATABASE_PATH}")