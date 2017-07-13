![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# census_pgeoloader

Command line utility to download Census TIGER/Line shapefiles from the U.S. Census Bureau and aggregate them into a single table in a PostGIS-enabled database.

# Requirements

Uses [shp2pgsql](http://www.bostongis.com/pgsql2shp_shp2pgsql_quickguide.bqg). Assumes PostgreSQL + PostGIS.

# To install

```bash
$ pip install census_pgeoloader
```

# To use

Pass a connection URI to your PostgreSQL database as well as the states you'd like to aggregate.

```bash
$ pgeoloader postgres://postgres@localhost:5432/cdc KS MO TX VA ...
```

Valid values for states are FIPS codes, postal abbreviations or names.

# Options

```bash
Options:
  -t, --table TEXT               Name of table to create in DB. Default is
                                 "census_shapes".
  -p, --temp TEXT                Temporary directory to download files to.
                                 Default is "./shapefiles"
  -y, --year TEXT                Year. Default is "2016".
  -g, --geo [tract|group|block]  Geographic unit. Default is "tract".
  -s, --srid TEXT                Specify an SRID transform, e.g., "4269:4326".
                                 Default is "4269".
  --help                         Show this message and exit.
```

#### Notes:

- `--table` Drops any existing table by that name in the database.
- `--geo` Can pull tracts, block groups or blocks.
- `--srid` Default SRID should be 4269, but you can specify a transform with this option as available in [shp2pgsql](http://www.bostongis.com/pgsql2shp_shp2pgsql_quickguide.bqg).

©2017 POLITICO
