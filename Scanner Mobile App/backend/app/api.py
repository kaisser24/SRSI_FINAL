from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlalchemy as db
from sqlalchemy import update
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import exists
from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound

# Database Configuration
user = "kvong"
password = "Passw0rd"
host = "radyweb.wsc.western.edu"
port = 3306
database = "truedemo_srsi"

DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# SQLAlchemy Configuration
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transaction"
    s_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, index=True)
    scan_time = Column(db.DateTime, default=datetime.utcnow)
    bin_id = Column(Integer)

class GenderCode(Base):
    __tablename__ = "gender_code"
    gen_code = Column(String, primary_key=True)
    gen_name = Column(String)

class GearlineCode(Base):
    __tablename__ = "gearline_code"
    gear_code = Column(String, primary_key=True)
    gear_name = Column(String)

class PriceCode(Base):
    __tablename__ = "price_code"
    pri_code = Column(String, primary_key=True)
    lower_bound = Column(Float)
    upper_bound = Column(Float)

class BinList(Base):
    __tablename__ = "bin_list"
    bin_number = Column(Integer, primary_key=True)
    assigned_sku = Column(String)
    sku_desc = Column(String)
    price_point = Column(String)
    gender = Column(String)
    silhouette = Column(String)
    sub_silhouette = Column(String)
    gearline = Column(String)

class Scan(BaseModel):
    scan_num: str

    class Config:
        from_attributes = True

class SKUList(Base):
    __tablename__ = "sku_list"
    sku = Column(String, Sequence('user_id_seq'), primary_key=True, index=True)
    upc = Column(String, index=True)
    price = Column(Float)
    gender = Column(String)
    sub_silhouette = Column(String)
    gearline = Column(String)

class BinToCarton(Base):
    __tablename__ = "bin_to_carton"
    bc_id = Column(Integer, primary_key=True, index=True)
    carton_id = Column(Integer, index=True)
    bin_number = Column(Integer, index=True)

class Bin(BaseModel):
    bin_number: int

class Carton(Base):
    __tablename__ = "carton"
    carton_id = Column(Integer, primary_key=True, index=True)
    item_count = Column(Integer)
    is_active = Column(Integer)
    time_open = Column(db.DateTime)
    time_closed = Column(db.DateTime)

metadata = db.MetaData()
Base = automap_base(metadata=metadata)

engine = create_engine(DATABASE_URL)
Base.prepare(autoload_with=engine)
connection = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SKUBin = Base.classes.bin_list

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
    "http://127.0.0.1:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global last_carton_id
last_carton_id = None

global last_bin
last_bin = None

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your scan list."}

@app.get("/last_carton", tags=["carton"])
async def get_last_carton() -> dict:
    try:
        with SessionLocal() as db:
            last_carton = (
                db.query(Carton)
                .join(BinToCarton, Carton.carton_id == BinToCarton.carton_id)
                .filter(BinToCarton.bin_number == last_bin)
                .filter(Carton.is_active == 1)
                .filter(Carton.time_closed.is_(None))
                .order_by(Carton.time_open.desc())
                .first()
            )

            if last_carton:
                return {
                    "data": {
                        "carton_id": last_carton.carton_id,
                        "bin_id": last_bin,
                        "item_count": last_carton.item_count,
                        "time_open": last_carton.time_open,
                    }
                }
            else:
                raise HTTPException(status_code=404, detail=f"No active cartons found for bin_number {last_bin}")

    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"No active cartons found for bin_number {last_bin}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.put("/close_carton/{carton_id}", tags=["carton"])
async def close_carton(carton_id: int) -> dict:
    db = SessionLocal()
    try:
        update_stmt = update(Carton).where(Carton.carton_id == carton_id).values(is_active=0, time_closed=datetime.utcnow())
        db.execute(update_stmt)

        db.commit()
        return {"data": f"Carton with id {carton_id} has been closed."}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to close carton. Error: {str(e)}"}
    finally:
        db.close()

@app.get("/Carton", tags=["carton"])
async def get_carton() -> dict:
    return {"last_scanned": 5}


@app.get("/scan", tags=["scans"])
async def get_scans() -> dict:
    db = SessionLocal()
    scans = db.query(Transaction).all()
    db.close()

    scans_dict = [{"id": scan.s_id, "sku": scan.sku} for scan in scans]
    return {"data": scans_dict}


@app.post("/scan", tags=["scans"])
async def add_scan(scan: Scan) -> dict:
    global last_carton_id
    global last_bin
    db1 = SessionLocal()
    new_carton = None

    try:
        sku_entry = db1.query(SKUList).filter(SKUList.upc == scan.scan_num).first()

        if sku_entry:
            joined_query = (
                db1.query(SKUList.sku, SKUList.price, GenderCode.gen_name, GearlineCode.gear_name, PriceCode.pri_code, BinList.bin_number)
                .join(GenderCode, SKUList.gender == GenderCode.gen_code)
                .join(GearlineCode, SKUList.gearline == GearlineCode.gear_code)
                .join(PriceCode, db.between(SKUList.price, PriceCode.lower_bound, PriceCode.upper_bound))
                .join(BinList, (GenderCode.gen_name == BinList.gender) & (GearlineCode.gear_name == BinList.gearline) & (PriceCode.pri_code == BinList.price_point))
                .filter(SKUList.upc == scan.scan_num)
                .first()
            )

            if joined_query:
                sku, price, gen_name, gear_name, pri_code, bin_number = joined_query
                print("Join result:", sku, price, gen_name, gear_name, pri_code, bin_number)

                last_bin = bin_number

                # Check if there's an associated open carton for the current bin_number
                existing_carton = (
                    db1.query(Carton)
                    .join(BinToCarton, Carton.carton_id == BinToCarton.carton_id)
                    .filter(BinToCarton.bin_number == bin_number)
                    .filter(Carton.is_active == 1)
                    .filter(Carton.time_closed.is_(None))
                    .first()
                )

                if existing_carton:
                    # Increment item_count in the corresponding Carton
                    db1.query(Carton).filter_by(carton_id=existing_carton.carton_id).update(
                        {Carton.item_count: Carton.item_count + 1},
                        synchronize_session=False
                    )
                else:
                    # If there is no associated open carton, create a new carton
                    new_carton = Carton(item_count=1, is_active=1, time_open=datetime.utcnow(), time_closed=None)
                    db1.add(new_carton)
                    db1.commit()
                    db1.refresh(new_carton)

                    # Create a new row in the BinToCarton table
                    new_bin_to_carton = BinToCarton(carton_id=new_carton.carton_id, bin_number=bin_number)
                    db1.add(new_bin_to_carton)
                    db1.commit()

                    # Update last_carton_id regardless of whether it's a new or existing carton
                    last_carton_id = int(new_bin_to_carton.carton_id) if new_bin_to_carton else int(existing_carton.carton_id)

                db1_scan = Transaction(sku=sku, scan_time=datetime.utcnow(), bin_id=bin_number, s_id=None)
                db1.add(db1_scan)
                db1.commit()
                db1.refresh(db1_scan)

                return {
                    "data": {
                        "message": "Scan added",
                        "scan": {
                            "id": db1_scan.s_id,
                            "sku": db1_scan.sku,
                            "bin_id": db1_scan.bin_id
                        },
                        "last_carton_id": last_carton_id
                    }
                }

            else:
                print("No matching entry found in join operation for SKU:", sku_entry.sku)
                return {"error": f"No matching entry found in join operation for SKU: {sku_entry.sku}"}

        else:
            print("No matching entry found for SKU:", scan.scan_num)
            return {"error": f"No matching entry found for SKU: {scan.scan_num}", "sku_not_found": True}

    except Exception as e:
        db1.rollback()
        print(str(e))
        return {"error": f"Error: {str(e)}"}
    finally:
        db1.close()

@app.put("/scan/{id}", tags=["scans"])
async def update_scan(id: int, scan: Scan) -> dict:
    db = SessionLocal()
    db_scan = db.query(Transaction).filter(Transaction.s_id == id).first()

    if db_scan:
        db_scan.sku = scan.scan_num 
        db.commit()
        db.refresh(db_scan)
        db.close()
        return {"data": f"Scan with id {id} has been updated."}

    db.close()
    return {"data": f"Scan with id {id} not found."}