# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from datetime import datetime
import pytz

class MSCPipeline:
    def __init__(self):
        self.create_connection()
        pass
    def create_connection(self):
        self.conn = psycopg2.connect(database="shipping_eta_info", user="postgres", password="password", host="host.docker.internal", port=5432)
        self.curr = self.conn.cursor()

    def store_db(self, item):
        def store_container(container: dict):
            self.curr.execute("SELECT description_c FROM container_no_bookmarks WHERE container_id = %s", tuple([container['id']]))
            result = self.curr.fetchall()
            if 'final_pod_eta' in container.keys():
                final_pod_eta = datetime.strptime(container['final_pod_eta'], "%d/%m/%Y")
            else:
                final_pod_eta = None

            movements = container['movements']
            id = container['id']
            local = pytz.timezone("CET")
            updated_at = datetime.strptime(container['updated_at'], "%d/%m/%Y %H:%M:%S")
            updated_at = local.localize(updated_at, is_dst=None).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            final_pod = container['final_pod']  if container['final_pod']  != '' else None
            shipped_to = container['shipped_to'] if container['shipped_to'] != '' else None
            price_calculation_date = datetime.strptime(container['price_calculation_date'], '%d/%m/%Y') if container['price_calculation_date'] != '' else None
            
            descriptions = []
            if len(result) > 0:
                for desc in result:
                    descriptions.append(desc[0])

            for move_object in movements:
                date = datetime.strptime(move_object['date'], "%d/%m/%Y") if move_object['date'] != '' else None
                location = move_object['location'] if move_object['location'] != '' else None
                description = move_object['description'] if move_object['description'] != '' else None
                vessel = move_object['vessel'] if move_object['vessel'] != '' else None
                voyage = move_object['voyage'] if move_object['voyage'] != '' else None
                
                insert_tuple = (id, description, updated_at, date, final_pod, final_pod_eta, shipped_to, price_calculation_date, location, vessel, voyage)
                if move_object['description'] not in descriptions:
                    self.curr.execute("INSERT INTO container_no_bookmarks VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", insert_tuple)

                else:
                    self.curr.execute("SELECT * FROM container_no_bookmarks WHERE container_id = %s AND description_c = %s", (id, move_object['description']))
                    result = self.curr.fetchall()
                    differences = [1 if v != insert_tuple[i] else 0 for i, v in enumerate(result[0])]

                    if 1 in differences:
                        self.curr.execute("UPDATE container_no_bookmarks SET updated_at=%s, date_c=%s, final_port_of_load=%s, final_port_of_load_eta=%s, shipped_to=%s, price_calculation_date=%s, location=%s, vessel=%s, voyage=%s WHERE container_id=%s AND description_c=%s", insert_tuple[2:] + insert_tuple[:2])

            self.conn.commit()

        if item['id_type'] == 'CON':
            store_container(item)

        elif item['id_type'] == 'BOL':
            bol_id = item['id'] if item['id'] != '' else None
            departure_date = datetime.strptime(item['departure_date'], "%d/%m/%Y") if item['departure_date'] != '' else None
            local = pytz.timezone("CET")

            updated_at = datetime.strptime(item['updated_at'], "%d/%m/%Y %H:%M:%S")
            updated_at = local.localize(updated_at, is_dst=None).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            bl_issuer = item['bl_issuer']
            print(bl_issuer)
            vessel = item['vessel'] if item['vessel'] != '' else None
            port_of_load = item['port_of_load'] if item['port_of_load'] != '' else None
            port_of_discharge = item['port_of_discharge'] if item['port_of_discharge'] != '' else None
            transhipment = item['transhipment'] if item['transhipment'] != '' else None
            price_calculation_date = datetime.strptime(item['price_calculation_date'], "%d/%m/%Y") if item['price_calculation_date'] != '' else None
            containers = item['containers']

            for container in containers:
                container_id = container['id']
                store_container(container)
                for move_object in container['movements']:
                    self.curr.execute("SELECT * FROM bill_of_lading_bookmarks WHERE bol_id=%s AND container_id=%s AND description_c=%s", (bol_id, container_id, move_object['description']))
                    result = self.curr.fetchall()
                    
                    insert_tuple = (bol_id, container_id, move_object['description'], bl_issuer, updated_at, departure_date, vessel, port_of_load, port_of_discharge, transhipment, price_calculation_date)
                    if len(result) == 0:
                        self.curr.execute("INSERT INTO bill_of_lading_bookmarks VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", insert_tuple)
                    else:

                        differences = [True if v != insert_tuple[i] else False for i, v in enumerate(result[0])]

                        if True in differences:
                            self.curr.execute("UPDATE bill_of_lading_bookmarks SET bl_issuer=%s, updated_at=%s, departure_date=%s, vessel=%s, port_of_load=%s, port_of_discharge=%s, transhipment=%s, price_calculation_date=%s WHERE bol_id=%s AND container_id = %s AND description_c = %s", insert_tuple[3:] + insert_tuple[:3])
                
                self.conn.commit()
                    

    def process_item(self, item, spider):
        self.store_db(item)
        return item
