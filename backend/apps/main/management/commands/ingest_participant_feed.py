from pathlib import Path

import pandas as pandas
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = '''
    Ingest participants from a participant feed XLSX file into the DB.
    '''

    def add_arguments(self, parser):
        parser.add_argument('feed_file_path', type=Path,
                            help='Path to an XLSX file with row 1 headers corresponding to Participant attributes and'
                                 ' rows 2+ specifying participants to ingest. Path can be absolute, or relative to the'
                                 ' working directory.')

    def handle(self, feed_file_path: Path, *args, **options):
        if not feed_file_path.exists():
            raise CommandError(f'Path {feed_file_path} does not exist')

        # TODO: Implement me
        df = pandas.read_excel(feed_file_path)
        self.stdout.write(f'Feed file columns: {", ".join(df.columns)}')
        raise NotImplementedError()