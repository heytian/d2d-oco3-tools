-- Step 1: combining CO2 SAM data from 2019-2025

CREATE TABLE co2_sam (
    sounding_id TEXT,
    xco2 FLOAT,
    operation_mode TEXT,
    xco2_quality_flag TEXT,
    target_name TEXT,
    latitude FLOAT,
    longitude FLOAT,
    index_right TEXT,
    target_name_2 TEXT,
    datetime TEXT,
    local_time TEXT,
    timezone TEXT,
    city TEXT,
    country TEXT
);

-- Step 2: cities and population from Natural Earth data
CREATE TABLE ne_cities (
    city TEXT,
    country TEXT,
    latitude FLOAT,
    longitude FLOAT,
    population INT
);

-- Step 3: add geometry columns
ALTER TABLE co2_sam ADD COLUMN geom GEOMETRY(Point, 4326);
ALTER TABLE ne_cities ADD COLUMN geom GEOMETRY(Point, 4326);

-- Step 4: populate geometry
UPDATE co2_sam SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
UPDATE ne_cities SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);

-- Step 5: create spatial index
CREATE INDEX idx_co2_geom ON co2_sam USING GIST(geom);
CREATE INDEX idx_cities_geom ON ne_cities USING GIST(geom);

-- Step 6: run nearest neighbour join
CREATE TABLE co2_sam_cities_pop AS
SELECT
    c2.sounding_id,
    c2.xco2,
    c2.operation_mode,
    c2.xco2_quality_flag,
    c2.target_name,
    c2.latitude,
    c2.longitude,
    c2.index_right,
    c2.target_name_2,
    c2.datetime,
    c2.local_time,
    c2.timezone,
    ref.city,
    ref.country,
    ref.population
FROM co2_sam c2
CROSS JOIN LATERAL (
    SELECT city, country, population
    FROM ne_cities
    ORDER BY c2.geom <-> ne_cities.geom
    LIMIT 1
) ref;

-- Step 7: create smaller version by checking column size
---- step 7.1: check column size to see which ones to cut
SELECT
    attname AS column,
    pg_size_pretty(sum(pg_column_size(attname::text)))
FROM pg_attribute
WHERE attrelid = 'co2_sam_cities_pop'::regclass
AND attnum > 0
GROUP BY attname
ORDER BY sum(pg_column_size(attname::text)) DESC;
---- step 7.2: then create smaller version
CREATE TABLE co2_sam_cities_pop_s AS
SELECT
    xco2,
    datetime,
    local_time,
    latitude,
    longitude,
    city,
    country,
    population
FROM co2_sam_cities_pop;
---step 7.3 change column types to further reduce size (run once)
ALTER TABLE co2_sam_cities_pop_s
    ALTER COLUMN datetime TYPE TIMESTAMP
        USING datetime::timestamp,
    ALTER COLUMN local_time TYPE TIMESTAMP
        USING local_time::timestamp;
    ALTER COLUMN xco2 TYPE REAL; -- didn't really affect size

-- other debugging functions

SELECT
    EXTRACT(YEAR FROM datetime::timestamp) AS year,
    COUNT(*) as row_count
FROM co2_sam_cities_pop
GROUP BY year
ORDER BY year;

SELECT pg_size_pretty(pg_total_relation_size('co2_sam_cities_pop_s'));

SHOW data_directory;
