--DROP TABLE IF EXISTS "${table_prefix}app_config";
--CREATE TABLE "public"."${table_prefix}app_config" (
--    "key" text NOT NULL,
--    "value" text ,
--    "update_ts" bigint ,
--    CONSTRAINT "tm_config_text" PRIMARY KEY ("key")
--)
--WITH (oids = false);
DROP TABLE IF EXISTS "${table_prefix}service_jobs";
DROP SEQUENCE IF EXISTS ${table_prefix}service_jobs_job_id_seq;
CREATE SEQUENCE ${table_prefix}service_jobs_job_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}service_jobs" (
    "job_id" bigint DEFAULT nextval('${table_prefix}service_jobs_job_id_seq') NOT NULL,
    "command_uri" character varying(250) NOT NULL,
    "job_name" character varying(50) NOT NULL,
    "job_description" character varying(50),
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}service_jobs_key" PRIMARY KEY ("job_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}service_jobs_command_uri ON public.${table_prefix}service_jobs USING btree (command_uri);



DROP TABLE IF EXISTS "${table_prefix}market_details";
DROP SEQUENCE IF EXISTS ${table_prefix}market_details_market_id_seq;
CREATE SEQUENCE ${table_prefix}market_details_market_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}market_details" (
    "market_id" bigint DEFAULT nextval('${table_prefix}market_details_market_id_seq') NOT NULL,
    "market_uri" character varying(250) NOT NULL,
    "market_name" character varying(50) NOT NULL,
    "market_type" character varying(30) NOT NULL,
    "market_description" character varying(50),
    "market_location" character varying(250),
    "subscribe" 	boolean  ,
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}market_details_key" PRIMARY KEY ("market_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}market_details_market_uri ON public.${table_prefix}market_details USING btree (market_uri);


DROP TABLE IF EXISTS "${table_prefix}market_offer_details";
DROP SEQUENCE IF EXISTS ${table_prefix}market_offer_details_offer_id_seq;
CREATE SEQUENCE ${table_prefix}market_offer_details_offer_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}market_offer_details" (
    "offer_id" bigint DEFAULT nextval('${table_prefix}market_offer_details_offer_id_seq') NOT NULL,
    "market_id" bigint NOT NULL,
    "offer_uri" character varying(150)  ,
    "sequence" character varying(10)  ,
    "currency_unit" character varying(10) NOT NULL,
    "volume_unit" character varying(10) NOT NULL,
    "ts_start" bigint NOT NULL,
    "ts_end" bigint NOT NULL,
    "isp_unit" int NOT NULL,
    "update_ts" bigint NOT NULL,
      "created_ts" bigint NOT  NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}market_offer_details_key" PRIMARY KEY ("offer_id")
)
WITH (oids = false);

CREATE UNIQUE  INDEX ${table_prefix}market_offer_details_unique_key ON public.${table_prefix}market_offer_details USING btree (market_id,ts_start,sequence);
CREATE UNIQUE  INDEX ${table_prefix}market_offer_details_offer_uri_key ON public.${table_prefix}market_offer_details USING btree (offer_uri);

ALTER TABLE ONLY "public"."${table_prefix}market_offer_details"
ADD CONSTRAINT "${table_prefix}market_offer_details_market_id_fkey" FOREIGN KEY (market_id)
REFERENCES ${table_prefix}market_details(market_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;


DROP TABLE IF EXISTS "${table_prefix}market_offer";
CREATE TABLE "public"."${table_prefix}market_offer" (
	"ts" bigint NOT NULL,
	"offer_id" bigint NOT NUll,
	"update_ts" bigint NOT NULL ,
	"isp_start" INT NOT NULL,
	"isp_len" INT NOT NULL,
	"cost"  double precision,
    CONSTRAINT "${table_prefix}market_offer_key" PRIMARY KEY ("offer_id","ts","isp_start" )
)
WITH (oids = false);

ALTER TABLE ONLY "public"."${table_prefix}market_offer"
ADD CONSTRAINT "${table_prefix}market_offer_offer_id_fkey" FOREIGN KEY (offer_id)
REFERENCES ${table_prefix}market_offer_details(offer_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;


DROP TABLE IF EXISTS "${table_prefix}service_log";
DROP SEQUENCE IF EXISTS ${table_prefix}service_log_log_id_seq;
CREATE SEQUENCE ${table_prefix}service_log_log_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;


CREATE TABLE "${table_prefix}service_log" (
   "log_id" bigint DEFAULT nextval('${table_prefix}service_log_log_id_seq') NOT NULL,
  "log_tag" character varying(10) NOT NULL,
  "log_context" character varying(100) NULL,
  "log_message" character varying(250) NOT NULL,
  "log_obj_type" character varying(150) NULL,
  "log_obj_json" text NULL,
  "log_ts" bigint NOT NULL,
    CONSTRAINT "${table_prefix}service_log_pk" PRIMARY KEY ("log_id")
);

CREATE INDEX "${table_prefix}service_log_log_ts" ON public.${table_prefix}service_log USING btree ("log_ts");