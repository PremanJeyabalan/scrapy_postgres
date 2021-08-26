CREATE TABLE container_no_bookmarks
(
container_id CHAR(11) NOT NULL,
description_c VARCHAR(100),
updated_at TIMESTAMP,
date_c DATE,
final_port_of_load VARCHAR(100),
final_port_of_load_eta DATE,
shipped_to VARCHAR(100),
price_calculation_date DATE,
location VARCHAR(100),
vessel VARCHAR(100),
voyage 	VARCHAR(20),
CONSTRAINT container_key PRIMARY KEY (container_id, description_c)
);

CREATE TABLE bill_of_lading_bookmarks 
(
bol_id CHAR(12),
container_id CHAR(11) NOT NULL,
description_c VARCHAR(100),
bl_issuer VARCHAR(30),
updated_at TIMESTAMP,
departure_date DATE,
vessel VARCHAR(100),
port_of_load VARCHAR(100),
port_of_discharge VARCHAR(100),
transhipment VARCHAR(100),
price_calculation_date DATE, 
FOREIGN KEY (container_id, description_c) REFERENCES container_no_bookmarks(container_id, description_c),
CONSTRAINT bill_of_lading_key PRIMARY KEY (bol_id, container_id, description_c)
);