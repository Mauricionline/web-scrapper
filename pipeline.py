import logging

logging.basicConfig(level=logging.INFO)
import subprocess

logger = logging.getLogger(__name__)
news_sites_uids = ['lostiempos', 'eldeber', 'opinion', 'larazon', 'jornada']
# news_sites_uids = ['opinion']
# news_sites_uids = ['lostiempos']
# news_sites_uids = ['larazon']


def main() -> None:
    _extract()
    _transform()
    _load()


def _extract() -> None:
    """ Execute extract main.py and run a subprocess command"""
    logger.info('Starting extract process')

    for new_site_uid in news_sites_uids:
        subprocess.run(['python3.8', 'main.py', new_site_uid], cwd='./extract')
        subprocess.run(['find', '.', '-name', f'{new_site_uid}*', '-exec', 'mv',
                        '{}', f'../transform/{new_site_uid}_.csv', ';'], cwd='./extract')


def _transform():
    """ Execute a transform main.py and run subprocess rm and mv files *.csv to load """
    logger.info('Starting transform process')
    for new_site_uid in news_sites_uids:
        dirty_data_filename = f'{new_site_uid}_.csv'
        clean_data_filename = f'clean_{dirty_data_filename}'
        subprocess.run(['python3.8', 'main.py', dirty_data_filename], cwd='./transform')
        subprocess.run(['rm', dirty_data_filename], cwd='./transform')
        subprocess.run(['mv', clean_data_filename, f'../load/{new_site_uid}.csv'], cwd='./transform')  # load?


def _load():
    """Execute a load main.py and rm clean data """
    logger.info('Starting load process')
    for new_site_uid in news_sites_uids:
        clean_data_filename = f'{new_site_uid}.csv'
        subprocess.run(['python3.8', 'main.py', clean_data_filename], cwd='./load')
        subprocess.run(['rm', clean_data_filename], cwd='./load')


if __name__ == '__main__':
    main()
