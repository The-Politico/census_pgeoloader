import errno
import os
import subprocess
import zipfile

import click
import psycopg2
import requests
import us


class ConnectionException(Exception):
    pass


class DatabaseException(Exception):
    pass


class Shp2pgsqlException(Exception):
    pass


class StateException(Exception):
    pass


GROUP = "group"
BLOCK = "block"
TRACT = "tract"
GEO_CHOICES = [TRACT, GROUP, BLOCK]
SRID = "4269"  # GCS North American 1983
YEAR = "2016"
API = {
    TRACT: "https://www2.census.gov/geo/tiger/TIGER{}/TRACT/tl_{}_{}_tract.zip", # noqa
    GROUP: "https://www2.census.gov/geo/tiger/TIGER{}/BG/tl_{}_{}_bg.zip",
    BLOCK: "https://www2.census.gov/geo/tiger/TIGER{}/TABBLOCK/tl_{}_{}_tabblock10.zip", # noqa
}


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def download_file(url, temp):
    mkdir('{}'.format(temp))
    local_filename = os.path.join(temp, url.split('/')[-1])
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


def unzip(filename):
    base_dir = os.path.dirname(os.path.abspath(filename))
    base_name = os.path.splitext(os.path.basename(filename))[0]
    write_dir = os.path.join(base_dir, base_name)
    zip_ref = zipfile.ZipFile(filename, 'r')
    mkdir(write_dir)
    zip_ref.extractall(write_dir)
    return os.path.join(write_dir, '{}.shp'.format(base_name))


def prepare_db(shapefile, table, srid, cur):
    query = subprocess.check_output((
        'shp2pgsql',
        '-p',
        '-s {}'.format(srid),
        shapefile,
        table
    ))
    try:
        cur.execute('CREATE EXTENSION IF NOT EXISTS POSTGIS;')
    except:
        raise DatabaseException('Could not create extension POSTGIS')
    cur.execute('DROP TABLE IF EXISTS {};'.format(table))
    cur.execute(query)


def load_into_db(shapefile, table, srid, cur):
    query = subprocess.check_output((
        'shp2pgsql',
        '-a',
        '-s {}'.format(srid),
        shapefile,
        table
    ))
    cur.execute(query)


@click.command()
@click.option(
    '--table', '-t', default='census_shapes',
    help='Name of table to create in DB. Default is "census_shapes".')
@click.option(
    '--temp', '-p', default='./shapefiles',
    help="Directory to download files to. Default is \"./shapefiles\"")
@click.option(
    '--year', '-y', default='2016', help='Year. Default is \"2016\".')
@click.option(
    '--geo', '-g', default=TRACT, type=click.Choice(GEO_CHOICES),
    help="Geographic unit. Default is \"tract\".")
@click.option(
    '--srid', '-s', default=SRID,
    help="Specify an SRID transform, e.g., \"4269:4326\". Default is \"4269\"."
)
@click.argument('db', nargs=1)
@click.argument('states', nargs=-1)
def load(table, temp, year, geo, srid, db, states):
    try:
        conn = psycopg2.connect(db)
    except:
        raise ConnectionException('Could not connect to PostgreSQL database.')
    cur = conn.cursor()

    # Allow to specify all states.
    if states[0] == '+':
        states = [state.fips for state in us.states.STATES]

    prepare = True  # Use the first state to prepare the database table
    for state in states:
        try:
            name = us.states.lookup(state).name
        except:
            raise StateException('Can\'t find state "{}"'.format(state))
        fips = us.states.lookup(state).fips
        click.echo('Requesting {}'.format(name))
        zipfile = download_file(API[geo].format(year, year, fips), temp)
        shpfile = unzip(zipfile)
        if prepare:
            click.echo('Preparing database')
            prepare_db(shpfile, table, srid, cur)
            prepare = False
        click.echo('Loading {}s'.format(geo))
        load_into_db(shpfile, table, srid, cur)
        click.echo('----------')
    conn.commit()
