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
