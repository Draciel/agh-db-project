import argparse

from generator import Generator

parser = argparse.ArgumentParser(description='Generate data for conferences mssql database')
parser.add_argument('--years', type=int, default=3)
parser.add_argument('--conferences_per_month', type=int, default=2)
parser.add_argument('--conference_min_length', type=int, default=2)
parser.add_argument('--conference_max_length', type=int, default=3)
parser.add_argument('--avg_conference_visitors', type=int, default=200)
parser.add_argument('--avg_workshops_per_day', type=int, default=4)
parser.add_argument('--avg_employees_per_company', type=int, default=20)


args = parser.parse_args()

generator = Generator(
    years=args.years,
    conferences_per_month= args.conferences_per_month,
    conference_min_length=args.conference_min_length,
    conference_max_length=args.conference_max_length,
    avg_workshops_per_day=args.avg_workshops_per_day,
    avg_conference_visitors=args.avg_conference_visitors,
    avg_employees_per_company=args.avg_employees_per_company
)
generator.generate()
