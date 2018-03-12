.separator ,
CREATE TABLE divvy
	(id integer,
		landmark integer,
		lat real,
		lon real,
		station_name varchar(100)
	);
.import divvy.csv divvy
CREATE TABLE cta
	(
		route integer,
		stop_id integer,
		stop_name varchar(1000),
		lat real,
		lon real,
		id integer
		);
.import bus_stops.csv cta

CREATE TABLE shuttles
	(
		stop_name varchar(100),
		lat real,
		lon real,
		route varchar(100)
		);
.import shuttle_data.csv shuttles