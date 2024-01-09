import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

#define database credentials
user = "kkellogg"
password = "Passw0rd"
host = "radyweb.wsc.western.edu"
port = 3306
database = "truedemo_srsi"

Base = automap_base()
#get connection
def getEngine():
    return db.create_engine(url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(user,password,host,port,database))

try:
    engine = getEngine()
    Base.prepare(autoload_with=engine)
    connection = engine.connect() #Connection variable used to interact with the database in main.py
    meta = db.MetaData()
    print(f"connection to the {host} for user {user} created sucessfully.")

except Exception as ex:
    print(f"connection could not be made due to the following error:{ex} \n")
