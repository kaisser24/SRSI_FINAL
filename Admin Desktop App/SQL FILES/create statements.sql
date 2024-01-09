CREATE TABLE bin_list(
bin_number INT NOT NULL PRIMARY KEY, 
assigned_sku varchar(20),
sku_desc varchar(20), 
price_point varchar(20), 
gender varchar(20), 
silhouette varchar(50), 
sub_silhouette varchar(50), 
gearline varchar(50));

CREATE TABLE carton(
carton_id MEDIUMINT NOT NULL AUTO_INCREMENT,
item_count int NOT NULL,
is_active boolean NOT NULL,
time_open datetime,
time_closed datetime,
PRIMARY KEY (carton_id)
);

CREATE TABLE bin_to_carton(
bc_id int(10) NOT NULL PRIMARY KEY auto_increment,
carton_id mediumint NOT NULL,
bin_number int NOT NULL,
CONSTRAINT bc_carton_id_fk FOREIGN KEY (carton_id) REFERENCES carton (carton_id),
CONSTRAINT bc_bin_number_fk FOREIGN KEY (bin_number) REFERENCES bin_list (bin_number)
);
CREATE TABLE gender_code (
	gen_code varchar(3) PRIMARY KEY,
    gen_name varchar(30)
    );
    
CREATE TABLE gearline_code (
	gear_code varchar(50) PRIMARY KEY,
    gear_name varchar(50)
    );

CREATE TABLE price_code (
	pri_code varchar (20) PRIMARY KEY,
    lower_bound float,
    upper_bound float
    );

CREATE TABLE sku_list(
	sku varchar(50) NOT NULL PRIMARY KEY,
	upc varchar(50) NOT NULL,
	price float NOT NULL,
	gender varchar(3) NOT NULL,
	sub_silhouette varchar(50),
	gearline varchar(50) NOT NULL,
	CONSTRAINT fk_sku_gender FOREIGN KEY (gender) REFERENCES gender_code(gen_code),
	CONSTRAINT fk_sku_gearline FOREIGN KEY (gearline) REFERENCES gearline_code(gear_code)
);

CREATE TABLE transaction(
s_id int(20) NOT NULL AUTO_INCREMENT,
sku varchar(50) NOT NULL,
scan_time datetime NOT NULL,
bin_id INT(20),
PRIMARY KEY (s_id),
CONSTRAINT transaction_sku_fk FOREIGN KEY (sku) REFERENCES sku_list (sku)
#CONSTRAINT bin_list_fk FOREIGN KEY (bin_id) REFERENCES bin_list (bin_number)
);


    
