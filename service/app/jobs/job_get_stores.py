from fastapi import Depends, HTTPException
from dataclasses import dataclass
from datetime import datetime
import logging
from app.jobs.job import Job
import orjson

# Define logger
logger = logging.getLogger(__name__)

@dataclass
class Store:
    id: int
    name: str
    name_secondary: str
    name_short: str
    email: str
    telephone: str
    city_name: str
    country_code: str
    district_id: int
    district_name: str
    datetime_opened: datetime
    datetime_closed: datetime
    store_organizational_unit: str
    store_organizational_unit_name: str
    store_type: str
    store_format: int
    format_name: str
    gln: str
    chain_id: int
    chain_name: str
    area_id: int
    area_name: str
    region_id: int
    region_name: str
    size_total_sqft: int
    size_selling_sqft: int
    timezone_name: str

class LoadStores(Job):
    """Retrieve store info from supergraph and store it in JDA."""

    def task(self) -> None:
        """Run update task."""
        stores = self.get_stores_from_graphql()
        self.load_store_info_in_jda(stores)

    def get_stores_from_graphql(self) -> list[Store]:
        """Load store info from supergraph."""
        logger.info("Fetching store info from supergraph")

        stores = self.fetch_stores()

        logger.info("Store info fetched successfully")
        return stores

    def fetch_stores(self) -> list[Store]:
        graphql_query = """
        query GetStores {
          stores(filters: {last_update_time: "2021-10-01 00:00:00"}) {
            items {
              id
              name
              address {
                city_name
                country_code
                district_id
                district_name
                postal_code
              }              
              contact {
                telephone
                email
              }
              linear_distance
              name_secondary
              name_short
              datetime_opened
              datetime_closed
              size_selling_sqft
              size_total_sqft
              timezone_name
              opening_hours              
              organization {
                area_id
                area_name
                chain_id
                chain_name
                format_name
                gln
                store_format
                store_organizational_unit
                store_organizational_unit_name
                store_type
              }

            }
          }
        }
        """
        response = self.supergraph_client.post(
            url="",
            json={"query": graphql_query},
            timeout=60,
        )
        response.raise_for_status()
        return [
            Store(
                   id=store["id"],
                   name=store["name"],
                   name_secondary=store["name_secondary"],
                   name_short=store["name_short"],
                   email=store["contact"]["email"],
                   telephone=store["contact"]["telephone"],
                   city_name=store["address"]["city_name"],
                   country_code=store["address"]["country_code"],
                   district_id=store["address"]["district_id"],
                   district_name=store["address"]["district_name"],
                   postal_code=store["address"]["postal_code"],
                   contact_name=store["address"]["name"],                   
                   datetime_opened=store["datetime_opened"],
                   datetime_closed=store["datetime_closed"],
                   store_organizational_unit=store["organization"]["store_organizational_unit"],
                   store_organizational_unit_name=store["organization"]["store_organizational_unit_name"],
                   store_type=store["organization"]["store_type"],
                   store_format=store["organization"]["store_format"],
                   format_name=store["organization"]["format_name"],
                   gln=store["organization"]["gln"],
                   chain_id=store["organization"]["chain_id"],
                   chain_name=store["organization"]["chain_name"],
                   area_id=store["organization"]["area_id"],
                   area_name=store["organization"]["area_name"],
                   size_total_sqft=store["size_total_sqft"],
                   size_selling_sqft=store["size_selling_sqft"],
                   timezone_name=store["timezone_name"]
            )
            for store in orjson.loads(response.content)["data"]["stores"]["items"]
        ]
    
    def persist_store_data(self, stores: list[Store]) -> None:
        """Store store info in JDA."""
        logger.info(f"Storing info in JDA for {len(stores)} stores")
        with self.ros_connection.cursor() as cursor:
            # Run update
            try:
                cursor.executemany(
                    """
                      BEGIN
                     INSERT INTO intowner.csg_etos_store_in ( store
                                                            , store_name
                                                            , store_name3
                                                            , store_name10
                                                            , store_open_date
                                                            , store_close_date
                                                            , phone_number
                                                            , fax_number
                                                            , email
                                                            , total_square_ft
                                                            , selling_square_ft
                                                            , linear_distance
                                                            , store_format
                                                            , store_format_name
                                                            , org_unit_id
                                                            , org_unit_name
                                                            , store_type
                                                            , timezone_name
                                                            , gln
                                                            , chain
                                                            , chain_name
                                                            , area
                                                            , area_name
                                                            , region
                                                            , region_name
                                                            , district
                                                            , district_name
                                                            , city
                                                            , state
                                                            , country_id
                                                            , post
                                                            , store_mgr_name
                                                            , contact_name
                                                            , jda_processed_flag
                                                            , jda_processed_time)
                                                      VALUES (:store
                                                            , :store_name
                                                            , :store_name3
                                                            , :store_name10
                                                            , :store_open_date
                                                            , :store_close_date
                                                            , :phone_number
                                                            , :fax_number
                                                            , :email
                                                            , :total_square_ft
                                                            , :selling_square_ft
                                                            , :linear_distance
                                                            , :store_format
                                                            , :store_format_name
                                                            , :org_unit_id
                                                            , :org_unit_name
                                                            , :store_type
                                                            , :timezone_name
                                                            , :gln
                                                            , :chain
                                                            , :chain_name
                                                            , :area
                                                            , :area_name
                                                            , null
                                                            , null
                                                            , :district
                                                            , :district_name
                                                            , :city
                                                            , :state
                                                            , :country_id
                                                            , :post
                                                            , :store_mgr_name
                                                            , :contact_name
                                                            , 'U'
                                                            , SYSTIMESTAMP);
                      END;
                      """,
                     [
                        (
                            store.store,
                            store.name,
                            store.name_secondary,
                            store.name_short,
                            store.datetime_opened,
                            store.datetime_closed,
                            store.telephone,
                            store.telephone,
                            store.email,
                            store.size_total_sqft,
                            store.size_selling_sqft,
                            store.linear_distnace,
                            store.store_format,
                            store.format_name,
                            store.store_organizational_unit,
                            store.store_organizational_unit_name,
                            store.store_type,
                            store.timezone_name,
                            store.gln,
                            store.chain_id,
                            store.chain_name,
                            store.area_id,
                            store.area_name,
                            store.district_id,
                            store.district_name,
                            store.city_name,
                            store.country_code,
                            store.postal_code,
                            store.contact_name,
                            store.contact_name
                        )
                        for store in stores
                    ],
                 )
                self.ros_connection.commit()
                logger.info("Stores committed successfully")
            except Exception as e:
                logger.error("Error while inserting stores")
                self.ros_connection.rollback()
                raise e
        logger.info("Insert process completed successfully.")
                                        