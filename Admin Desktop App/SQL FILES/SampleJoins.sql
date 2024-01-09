-- Join statement for the gender to get the codes
SELECT *
FROM sku_list s
JOIN gender_code g on s.gender = g.gen_code
JOIN gearline_code gr on s.gearline = gr.gear_code
JOIN price_code p ON s.price >= p.lower_bound AND s.price <= p.upper_bound
join bin_list b on g.gen_name = b.gender AND gr.gear_name = b.gearline AND p.pri_code = b.price_point;

-- Pull all scans from x date to y date
	-- Return: sku, Bin #, Count, Date x, Date y
    
SELECT sku_list.sku, bin_list.bin_number, transaction.scan_time FROM sku_list JOIN gender_code ON sku_list.gender = gender_code.gen_code JOIN gearline_code ON sku_list.gearline = gearline_code.gear_code JOIN price_code  ON sku_list.price >= price_code.lower_bound AND sku_list.price <= price_code.upper_bound JOIN bin_list ON gender_code.gen_name = bin_list.gender AND gearline_code.gear_name = bin_list.gearline  AND price_code.pri_code = bin_list.price_point JOIN transaction ON transaction.sku = sku_list.sku WHERE transaction.scan_time BETWEEN '2023-11-13 00:00:00' AND '2023-11-15 23:59:59' GROUP BY sku_list.sku;


#number of closed cartons per bin
SELECT COUNT(carton.carton_id) as number_cartons_closed, bin_list.bin_number FROM carton JOIN bin_to_carton  ON carton.carton_id = bin_to_carton.carton_id JOIN bin_list ON bin_to_carton.bin_number = bin_list.bin_number WHERE carton.is_active = 0 AND carton.time_open BETWEEN '2023-11-13 00:00:00' AND '2023-11-17 23:59:59' GROUP BY bin_list.bin_number;

#number of items in each carton
SELECT carton.carton_id, carton.item_count,carton.is_active, bin_list.bin_number, bin_list.gender, bin_list.price_point, bin_list.gearline FROM carton JOIN bin_to_carton ON carton.carton_id = bin_to_carton.carton_id JOIN bin_list  ON bin_to_carton.bin_number = bin_list.bin_number WHERE carton.time_open BETWEEN '2023-11-13 00:00:00' AND '2023-11-17 23:59:59';