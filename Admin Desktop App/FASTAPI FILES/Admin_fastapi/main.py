
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import pandas as pd
from pydantic import BaseModel
import database
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
from datetime import datetime

#TEST DOWNLOAD CODE 
from pathlib import Path

#HAVE TO RUN UVICORN IN VC AS python -m uvicorn main:app --reload

class BIN(BaseModel):
      binID: int
      pricePoint: str
      gender: str
      silouette: str
      subSilouette: str
      gearLine: str

class SearchDates(BaseModel): #define a class to hold user input
    dates: list #a list with the from and to dates

class ItemsDownloaded(BaseModel): #Download information
    returns: int = 0 #number of entries returned
    error: str = ""
    errMsg: str = ""

class ItemsInserted(BaseModel):
    duplications: int = 0
    insertions: int = 0
    error: str = ""
    errMsg: str = ""

app = FastAPI()
origins = [
     "127.0.0.1:8000",
     "http://localhost",
     "http://localhost:8100"
]
app.add_middleware(
     CORSMiddleware,
     allow_origins=origins,
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)
#uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.get("/")
async def root():
        content = """
<body>
<form action="/uploadcvs/" method="post" enctype="multipart/form-data">
<input name="file" type="file" >
<input type="submit">
</form>
</body>
    """
        return HTMLResponse(content=content)



@app.post("/uploadbinlist/")
async def upload_csv(file: UploadFile) -> ItemsInserted:
    try:
        #initialize messages that will be returned
        err = ""
        errMsg = ""
        duplicated = 0
        inserted = 0
        #get the headers from the bin_list in the database
        binData = pd.read_sql_table('bin_list',database.connection)
        binHeaders = list(binData.columns.values)


        csvData = pd.read_csv(file.file, index_col=False, dtype=str) #read in the csv file as a pandas dataframe
        csvHeaders = list(csvData.columns.values) #get the headers of the file

        if(csvHeaders == binHeaders): #make sure the user uploaded a bin_list csv
            duplicated = csvData.duplicated(subset='bin_number', keep='first').sum() #Count the number of duplicate bins in the uploaded file
            csvData = csvData.drop_duplicates(subset='bin_number', keep='first') #delete any duplicates because bin_number 



            inserted = csvData.shape[0] - duplicated #the number of items that will be inserted into the bin_list

            if(inserted > 0): #only try to upload if there is something to upload
                
                #Read in the child table bin_to_carton to a pandas dataframe and drop the table
                binCartonData = pd.read_sql_table('bin_to_carton', database.connection)
                dropBinCarton = text('DROP TABLE IF EXISTS bin_to_carton;')
                database.connection.execute(dropBinCarton)

                #TEST TRANSACTION CODE
                transactionData = pd.read_sql_table('transaction',database.connection)
                dropTransaction = text('DROP TABLE IF EXISTS transaction;')
                database.connection.execute(dropTransaction)
                

                dropBin = text('DROP TABLE IF EXISTS bin_list;') #Drop the bin_list table
                database.connection.execute(dropBin)

                #Recreate the bin_list table
                createBin = text('CREATE TABLE bin_list(bin_number INT NOT NULL PRIMARY KEY,assigned_sku varchar(20),sku_desc varchar(20),price_point varchar(20),gender varchar(20),silhouette varchar(50),sub_silhouette varchar(50),gearline varchar(50));')
                database.connection.execute(createBin)
                database.connection.commit() #commit the changes to the database

                #insert the data from the csv file into bin_list
                csvData.to_sql(name="bin_list", con=database.connection, if_exists="append", index=False)

                #recreate the bin_to_carton table and reinsert its data from the pandas dataframe
                createBinCarton = text('CREATE TABLE bin_to_carton(bc_id int(10) NOT NULL PRIMARY KEY auto_increment,carton_id mediumint(9) NOT NULL,bin_number int(20) NOT NULL,CONSTRAINT bc_carton_id_fk FOREIGN KEY (carton_id) REFERENCES carton (carton_id),CONSTRAINT bc_bin_number_fk FOREIGN KEY (bin_number) REFERENCES bin_list (bin_number));')
                database.connection.execute(createBinCarton)

                #CREATE TRANSACTION STUFF
                #TEST TRANSACTION CODE 2
                createTransaction = text('CREATE TABLE transaction(s_id int(20) NOT NULL AUTO_INCREMENT,sku varchar(50) NOT NULL,scan_time datetime NOT NULL, bin_id INT, PRIMARY KEY (s_id),CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku), CONSTRAINT bin_list_fk FOREIGN KEY (bin_id) REFERENCES bin_list (bin_number));')
                database.connection.execute(createTransaction)
                database.connection.commit()
                #TEST TRANSACTION CODE 3
                transactionData.to_sql(name = 'transaction', con=database.connection, if_exists='append', index=False)
                binCartonData.to_sql(name = 'bin_to_carton', con = database.connection, if_exists='append', index=False)

            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
        else:
            #Set error and return values
            err = "Incorrect csv format!"
            errMsg = "Expected Format: bin_number | assigned_sku | sku_desc | price_point | gender | silhouette | sub_silhouette | gearline"
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    except Exception as ex:
        err = "Unknown Error!"
        errMsg = str(ex)
        return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    #Check for duplication Return number of duplicaitons
    #Return number of items entered into the database
    #Return an error if the csv format is wrong

@app.post("/uploaditemlist/")
async def upload_csv(file: UploadFile) -> ItemsInserted:
    #From sku_list.csv we must delete intries 41546-41549
    #sku's (3027014-100-9, 3027014-100-10, 3027014-100-10.5, 3027014-100-11)

    try:
        #initialize messages that will be returned
        err = ""
        errMsg = ""
        duplicated = 0
        inserted = 0
        #initialize the count of SKUs dropped becasue of gearline or gender
        gearDropped = 0
        genderDropped = 0
        
        #read in the data from the csv into a dataframe
        csvData = pd.read_csv(file.file, index_col=False, dtype=str)
        csvHeaders = list(csvData.columns.values) #get the headers of the csv file
          

        if(len(csvHeaders) < 6): #if there are not enough columns throw an error
            err = "Incorrect csv format!"
            errMsg = "Too few columns."
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}

        try:
            #assosiate specifically named columns to the ones used in the database
            sku_maps = {csvData['SKU'].name:'sku' ,csvData['STBRCD'].name :'upc' ,csvData['STRPRC'].name :'price' , csvData['STSC4'].name :'gender', csvData['STVNPR'].name:'sub_silhouette', csvData['STPRGR'].name:'gearline'}
        except:
            err = "Incorrect csv format!"
            errMsg = "Needed columns: SKU | STBRCD | STRPRC | STSC4 | STVNPR | STPRGR"
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}

        csvData.rename(columns=sku_maps, inplace=True)#rename the columns in the dataframe to the mapped values
        csvData = csvData[['sku','upc','price','gender','sub_silhouette','gearline']]#drop all but the needed columns
        csvHeaders = list(csvData.columns.values)

        check = len(csvData)
        # find any invalid gearline
        gear_mapData = pd.read_sql_table('gearline_code',database.connection)#Read in the gearline map
        test = csvData[csvData["gearline"].isin(gear_mapData['gear_code']) == True] #removes any gearline codes that aren't found in the gearline map
        gearDropped = check - len(test)
        csvData = test

        gender_mapData = pd.read_sql_table('gender_code', database.connection)#read in the gender map
        test = csvData[csvData["gender"].isin(gender_mapData['gen_code']) == True]#removes any gender codes that aren't found in the gender map
        genderDropped = check - len(test)
        csvData = test 

        

        if(csvHeaders):
            #finds any duplicates of SKU values and removes them from the data to be inserted
            duplicated = csvData.duplicated(subset='sku', keep='first').sum()
            csvData = csvData.drop_duplicates(subset='sku', keep='first')

            inserted = csvData.shape[0] - duplicated #number of valid values to inert

            if(inserted > 0): #only insert into the table if there are values to insert
                #Drop the child table of sku_list: transaction
                transactionData = pd.read_sql_table('transaction',database.connection)
                dropTransaction = text('DROP TABLE IF EXISTS transaction;')
                database.connection.execute(dropTransaction)

                #Drop the sku_list table
                dropSku = text('DROP TABLE IF EXISTS sku_list;')
                database.connection.execute(dropSku)

                #recreate the sku_list table
                createSku = text('CREATE TABLE sku_list(sku varchar(50) NOT NULL PRIMARY KEY,upc varchar(50) NOT NULL,price float NOT NULL,gender varchar(3) NOT NULL,sub_silhouette varchar(50),gearline varchar(50) NOT NULL,CONSTRAINT fk_sku_gender FOREIGN KEY (gender) REFERENCES gender_code(gen_code),CONSTRAINT fk_sku_gearline FOREIGN KEY (gearline) REFERENCES gearline_code(gear_code));')
                database.connection.execute(createSku)
                database.connection.commit()#commit the changes to the database

                #insert the new data into sku_list
                csvData.to_sql(name="sku_list", con=database.connection, if_exists="append", index=False)

                #recreate the tranaction table
                createTransaction = text('CREATE TABLE transaction(s_id int(20) NOT NULL,sku varchar(50) NOT NULL,scan_time datetime NOT NULL,PRIMARY KEY (s_id),CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku));')
                #createTransaction = text('CREATE TABLE transaction(s_id int(20) NOT NULL AUTO_INCREMENT,sku varchar(50) NOT NULL,scan_time datetime NOT NULL, bin_id INT, PRIMARY KEY (s_id),CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku), CONSTRAINT bin_list_fk FOREIGN KEY (bin_id) REFERENCES bin_list (bin_number));')
                database.connection.execute(createTransaction)
                database.connection.commit()#commit changes to the database

                #reinsert the transaction data into the transaction table
                transactionData[transactionData["sku"].isin(csvData['sku']) == True] #removes any values associated with SKUs that no longer exist
                transactionData.to_sql(name = 'transaction', con=database.connection, if_exists='append', index=False)
                errMsg = f"incompatable genders: {genderDropped}\n  incompatable gearlines: {gearDropped}"
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
        else:
            err = "Incorrect csv format!"
            errMsg = "Unknown Error"
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    except Exception as ex:
        err = "Unknown Error!"
        errMsg = str(ex)
        return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    #Check for duplication Return number of duplicaitons
    #Return number of items entered into the database
    #Return an error if the csv format is wrong

@app.post("/uploadskumap/")
async def upload_csv(file: UploadFile) -> ItemsInserted:
    try:
        #initialize message values
        err = ""
        errMsg = ""
        duplicated = 0
        inserted = 0
       

        csvData = pd.read_csv(file.file, index_col=False, dtype=str)
        csvHeaders = list(csvData.columns.values)

        #read in and get the headers of each of the three maps
        price_mapData = pd.read_sql_table('price_code',database.connection)
        price_mapHeaders = list(price_mapData.columns.values)

        gender_mapData = pd.read_sql_table('gender_code', database.connection)
        gender_mapHeaders = list(gender_mapData.columns.values)

        gear_mapData = pd.read_sql_table('gearline_code',database.connection)
        gear_mapHeaders = list(gear_mapData.columns.values)

        #if the csv is the price map
        if(csvHeaders == price_mapHeaders):
            #drop any duplicated price codes
            duplicated = csvData.duplicated(subset='pri_code', keep='first').sum()
            csvData = csvData.drop_duplicates(subset='pri_code', keep='first')

            inserted = csvData.shape[0] - duplicated

            if(inserted > 0):
                #drop the price code table
                dropPriceMap = text('DROP TABLE IF EXISTS price_code;')
                database.connection.execute(dropPriceMap)

                #recreate teh price code table
                createPriceMap = text('CREATE TABLE price_code(pri_code varchar (20) PRIMARY KEY,lower_bound float,upper_bound float);')
                database.connection.execute(createPriceMap)
                database.connection.commit()

                #insert the new data into the price map
                csvData.to_sql(name="price_code", con=database.connection, if_exists="append", index=False)
                errMsg = "Price Map"
                       
                  

            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
        
        #if the csv is the gender map
        elif(csvHeaders == gender_mapHeaders):
            duplicated = csvData.duplicated(subset='gen_code', keep='first').sum()
            csvData = csvData.drop_duplicates(subset='gen_code', keep='first')

            inserted = csvData.shape[0] - duplicated

            if(inserted > 0):
                #read in transaction data and save it to a pandas dataframe
                transactionData = pd.read_sql_table('transaction',database.connection)

                #read in sku_list data and save it to a pandas dataframe
                skuData = pd.read_sql_table('sku_list', database.connection)

                #drop the transaction and sku_list tables
                dropTransaction = text('DROP TABLE IF EXISTS transaction;')
                database.connection.execute(dropTransaction)
                dropSku = text('DROP TABLE IF EXISTS sku_list;')
                database.connection.execute(dropSku)

                #Drop the gender map table
                dropGenderMap = text('DROP TABLE IF EXISTS gender_code;')
                database.connection.execute(dropGenderMap)

                #recreate the gender map table
                createGenderMap = text('CREATE TABLE gender_code(gen_code varchar(3) PRIMARY KEY,gen_name varchar(30));')
                database.connection.execute(createGenderMap)
                database.connection.commit()

                #Upload the new data into the gender map table
                csvData.to_sql(name="gender_code", con=database.connection, if_exists="append", index=False)

                #recreate the sku_list table
                createSku = text('CREATE TABLE sku_list(sku varchar(50) NOT NULL PRIMARY KEY,upc varchar(50) NOT NULL,price float NOT NULL,gender varchar(3) NOT NULL,sub_silhouette varchar(50),gearline varchar(50) NOT NULL,CONSTRAINT fk_sku_gender FOREIGN KEY (gender) REFERENCES gender_code(gen_code),CONSTRAINT fk_sku_gearline FOREIGN KEY (gearline) REFERENCES gearline_code(gear_code));')
                database.connection.execute(createSku)
                database.connection.commit()
                
                #reupload the data into sku_list
                skuData.to_sql(name="sku_list", con=database.connection, if_exists="append", index=False)

                #recreate the transaction table
                createTransaction = text('CREATE TABLE transaction(s_id int(20) NOT NULL,sku varchar(50) NOT NULL,scan_time datetime NOT NULL,PRIMARY KEY (s_id),CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku));')
                database.connection.execute(createTransaction)
                database.connection.commit()

                #reupload the data into the transaction table
                transactionData.to_sql(name = 'transaction', con=database.connection, if_exists='append', index=False)

                #Leting the user know which map they uploaded
                errMsg = "Gender Map"
                       
                  

            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}  
                  
        #See the gender map upload for details on how each section works
        elif(csvHeaders == gear_mapHeaders):
            duplicated = csvData.duplicated(subset='gear_code', keep='first').sum()
            csvData = csvData.drop_duplicates(subset='gear_code', keep='first')

            inserted = csvData.shape[0] - duplicated

            if(inserted > 0):

                transactionData = pd.read_sql_table('transaction',database.connection)
                skuData = pd.read_sql_table('sku_list', database.connection)
                dropTransaction = text('DROP TABLE IF EXISTS transaction;')
                database.connection.execute(dropTransaction)
                dropSku = text('DROP TABLE IF EXISTS sku_list;')
                database.connection.execute(dropSku)

                dropGearMap = text('DROP TABLE IF EXISTS gearline_code;')
                database.connection.execute(dropGearMap)
                createGearMap = text('CREATE TABLE gearline_code(gear_code varchar(50) PRIMARY KEY,gear_name varchar(50));')
                database.connection.execute(createGearMap)
                database.connection.commit()
                csvData.to_sql(name="gearline_code", con=database.connection, if_exists="append", index=False)

                createSku = text('CREATE TABLE sku_list(sku varchar(50) NOT NULL PRIMARY KEY,upc varchar(50) NOT NULL,price float NOT NULL,gender varchar(3) NOT NULL,sub_silhouette varchar(50),gearline varchar(50) NOT NULL,CONSTRAINT fk_sku_gender FOREIGN KEY (gender) REFERENCES gender_code(gen_code),CONSTRAINT fk_sku_gearline FOREIGN KEY (gearline) REFERENCES gearline_code(gear_code));')
                database.connection.execute(createSku)
                database.connection.commit()
                

                skuData.to_sql(name="sku_list", con=database.connection, if_exists="append", index=False)

                createTransaction = text('CREATE TABLE transaction(s_id int(20) NOT NULL,sku varchar(50) NOT NULL,scan_time datetime NOT NULL,PRIMARY KEY (s_id),CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku));')
                database.connection.execute(createTransaction)
                database.connection.commit()

                transactionData.to_sql(name = 'transaction', con=database.connection, if_exists='append', index=False)

                errMsg = "Gearline Map"
                       
                  

            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg} 
        
        else:
            err = "Incorrect csv file"
            errMsg = "Acceptable Maps: Gender | Gearline | Price"
            return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    except Exception as ex:
        err = "Unknown Error!"
        errMsg = str(ex)
        return{"duplications": duplicated, "insertions":inserted, "error":err, "errMsg":errMsg}
    #Check for duplication Return number of duplicaitons
    #Return number of items entered into the database
    #Return an error if the csv format is wrong

def checkDates (dateX, dateY):

    #set the format to year-month-day
    format = "%Y-%m-%d"
    try:
        #try to transform the strings dateX and dateY into datetime objects using the format provided above
        resultX = datetime.strptime(dateX, format)
        resultY = datetime.strptime(dateY, format)

        #if the first date is after the second date return an error code
        if(resultX > resultY):
            return -1
            
        return 0
    except ValueError:
        #If any value fails to be transformed return an error code
        print("Value Error")
        
        return -2
        
    

@app.post("/export/")
async def downloadTransactions(date: SearchDates) -> ItemsDownloaded:
    #read in the two dates and the query type
    dateX = date.dates[0]
    dateY = date.dates[1]
    searchType = date.dates[2]

    #initialize messages
    err = ""
    errMsg = ""
    returned = 0

    #get the error code from checking if dateX and dateY were properlly formated
    check = checkDates(dateX, dateY)

    if(check == -1):
        err = "Invalid dates"
        errMsg = "'From' date must be before 'To' date"
        return{"returns": returned, "error":err, "errMsg":errMsg}
    elif(check == -2):
        err = "Incorrect Format"
        errMsg = "Expected format: yyyy-mm-dd"
        return{"returns": returned, "error":err, "errMsg":errMsg}

    try:
        if(returned == 0):
            if(searchType == "Transactions"):
                #Returns all tansactions made between dateX and dateY
                exportQuery = pd.read_sql_query(f"SELECT sku_list.sku, bin_list.bin_number, transaction.scan_time FROM sku_list JOIN gender_code ON sku_list.gender = gender_code.gen_code JOIN gearline_code ON sku_list.gearline = gearline_code.gear_code JOIN price_code  ON sku_list.price >= price_code.lower_bound AND sku_list.price <= price_code.upper_bound JOIN bin_list ON gender_code.gen_name = bin_list.gender AND gearline_code.gear_name = bin_list.gearline  AND price_code.pri_code = bin_list.price_point JOIN transaction ON transaction.sku = sku_list.sku WHERE transaction.scan_time BETWEEN '{dateX} 00:00:00' AND '{dateY} 23:59:59' GROUP BY sku_list.sku;", database.connection)
            elif(searchType == "CartonCounts"):
                #Retursn the number of items scaned per carton
                exportQuery = pd.read_sql_query(f"SELECT carton.carton_id, carton.item_count,carton.is_active, bin_list.bin_number, bin_list.gender, bin_list.price_point, bin_list.gearline FROM carton JOIN bin_to_carton ON carton.carton_id = bin_to_carton.carton_id JOIN bin_list  ON bin_to_carton.bin_number = bin_list.bin_number WHERE carton.time_open BETWEEN '{dateX} 00:00:00' AND '{dateY} 23:59:59';", database.connection)
            elif(searchType == "CartonsClosed"):
                #returns the number of closed cartons per bin
                exportQuery = pd.read_sql_query(f"SELECT COUNT(carton.carton_id) as number_cartons_closed, bin_list.bin_number FROM carton JOIN bin_to_carton  ON carton.carton_id = bin_to_carton.carton_id JOIN bin_list ON bin_to_carton.bin_number = bin_list.bin_number WHERE carton.is_active = 0 AND carton.time_open BETWEEN '{dateX} 00:00:00' AND '{dateY} 23:59:59' GROUP BY bin_list.bin_number;", database.connection)
            returned = len(exportQuery)

            if(returned > 0):
                #get the users path and append the Downlaods file
                #downloadPath = os.path.expanduser('~\Downloads')

                #export a csv file to the downloads folder and names the file based on what query was used and what dates were selected
                exportQuery.to_csv(f"{searchType}_{dateX}to{dateY}.csv",index=False)
            else:
                err = "No Information Returned"
                errMsg = "Dates returned no results"
        return{"returns": returned, "error":err, "errMsg":errMsg}
    except Exception as ex:
        err = "Unknown Error!"
        errMsg = str(ex)
        return{"returns": returned, "error":err, "errMsg":errMsg}
    


if __name__ == '__main__':
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
   #uvicorn.run("main:app", host="localhost", port=8000, reload=True)
