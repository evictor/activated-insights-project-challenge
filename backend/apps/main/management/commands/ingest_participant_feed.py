from __future__ import annotations

from abc import abstractmethod
from cmath import isnan
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List
import pandas as pandas
from django.core.management import BaseCommand, CommandError
from django.db import IntegrityError

from apps.main.models import Participant


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

        self.stdout.write(f'Reading {feed_file_path}')
        participants = pandas.read_excel(feed_file_path)

        algo = OneQueryPerParticipantIngestion()
        result = algo.ingest(participants)

        if result.partial_success:
            self.stdout.write(f'Ingestion partially succeeded with {result.human_readable_counts}', self.style.NOTICE)
        elif result.success:
            self.stdout.write(f'Ingestion succeeded with {result.human_readable_counts}', self.style.SUCCESS)
        else:
            self.stdout.write(f'Ingestion failed with {result.human_readable_counts}', self.style.ERROR)

        if len(result.errors):
            self.stdout.write('The following error(s) occurred:', self.style.ERROR)
            for error in result.errors:
                self.stdout.write(error, self.style.ERROR)

        self.stdout.write(f'Total time elapsed: {result.elapsed_time}', self.style.SUCCESS)


@dataclass
class IngestionResult:
    """Usable as a context manager; wrap ingestion code and the context will be profiled"""

    """Set to True when context exits and no errors have occurred"""
    success: bool = False

    """
    Set to True if context exits and some errors occurred (`len(errors) != 0`), but some participants were
    at least successfully processed (`len(num_created) + len(num_existed) > 0`).
    """
    partial_success: bool = False

    """Set when context exits if an error occurred"""
    errors: List[BaseException] = field(default_factory=list)

    """Number of participants created during ingestion"""
    num_created: int = 0

    """Number of participants that already existed"""
    num_existed: int = 0

    """Set when context starts"""
    start_time: datetime = None

    """Set when context exits"""
    end_time: datetime = None

    """Set when context exits"""
    elapsed_time: timedelta = None

    def __enter__(self):
        assert self.start_time is None, 'Unexpected IngestionResult state; start_time is set'
        self.start_time = datetime.now()
        return self

    def add_error(self, error: BaseException):
        self.errors.append(error)

    def inc_created(self):
        """Increment the counter of participants created"""
        self.num_created += 1

    def inc_existed(self):
        """Increment the counter of participants that already existed"""
        self.num_existed += 1

    @property
    def human_readable_counts(self) -> str:
        """
        Human-friendly string describing the numbers of created, existing, and errored participants represented by this
        ingestion result
        """

        clauses = [f'{self.num_created} created']

        if self.num_existed:
            clauses.append(f'{self.num_existed} already existing')

        if num_errors := len(self.errors):
            clauses.append(f'{num_errors} error(s)')

        return ' and '.join(clauses) if len(clauses) <= 2 else ', '.join(clauses[:-1]) + f', and {clauses[-1]}'

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.end_time is None, 'Unexpected IngestionResult state; end_time is set'
        self.end_time = datetime.now()
        self.elapsed_time = self.end_time - self.start_time
        if exc_type is not None:
            self.success = False
            self.errors.append(exc_val)
        self.success = len(self.errors) == 0
        self.partial_success = len(self.errors) > 0 and (self.num_created > 0 or self.num_existed > 0)


class ParticipantIngestionAlgo:
    """Base class for participant ingestion algos to ease swapping, profiling, and comparison among algos"""

    @abstractmethod
    def ingest(self, participants: pandas.DataFrame) -> IngestionResult:
        """Ingest a dataframe of participants into the DB"""


class OneQueryPerParticipantIngestion(ParticipantIngestionAlgo):
    def ingest(self, participants: pandas.DataFrame) -> IngestionResult:
        with IngestionResult() as result:
            for p in participants.itertuples(index=False):
                # noinspection PyProtectedMember
                p_kwargs = p._asdict()

                if isinstance(p.birth_date, str):
                    has_birth_date = p.birth_date.strip() != ''
                elif isinstance(p.birth_date, float):
                    has_birth_date = not isnan(p.birth_date)
                else:
                    result.add_error(
                        TypeError(f'birth_date "{p.birth_date}" is of unexpected type {type(p.birth_date)};'
                                  ' only str YYYY/MM/DD, float NaN, and empty str are allowed')
                    )
                    continue

                if has_birth_date:
                    parts = p.birth_date.split('/')
                    if len(parts) != 3:
                        result.add_error(ValueError(f'Invalid date "{p.birth_date}"; expected format YYYY/MM/DD'))
                        continue

                    p_kwargs['birth_date'] = date(int(parts[0]), int(parts[1]), int(parts[2]))
                else:
                    p_kwargs['birth_date'] = None

                try:
                    Participant.objects.create(**p_kwargs)
                    result.inc_created()
                except IntegrityError as ex:
                    if 'unique' in (msg_lower := str(ex).lower()) and 'participant_code' in msg_lower:
                        result.inc_existed()
                    else:
                        raise ex

        return result
