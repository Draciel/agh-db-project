import copy
import random
import datetime
from dateutil import relativedelta
from dateutil.parser import parse
from dateutil.parser import parser
from faker import Factory
from tqdm import tqdm

import procedures
from helpers import fixed_mean_random, random_part
from db import conn, cursor

fake = Factory.create('pl_PL')

conference_technology = ['Java', 'Python', 'C++', 'Go', 'Scala', 'Android']
conference_adj = ['Future', 'Efficient', 'Scalable', 'Innovative', 'Modern']
conference_city = ['Kraków', 'Warszawa', 'Wrocław', 'Poznań', 'Katowice']
workshops_topics = [
    'Design Patterns in',
    'Parallel processing in',
    'Test Driven Development in',
    'Monitoring',
    'Stress testing in',
    'Optimization techniques in',
    'Devops',
    'Continuous Integration for',
    'Continuous Deployment for'
]


class Generator:

    def __init__(self,
        years,
        conferences_per_month,
        conference_min_length,
        conference_max_length,
        avg_workshops_per_day,
        avg_conference_visitors,
        avg_employees_per_company
    ):
        self.years = years
        self.conferences_per_month = conferences_per_month
        self.conference_min_length = conference_min_length
        self.conference_max_length = conference_max_length
        self.avg_workshops_per_day = avg_workshops_per_day
        self.avg_conference_visitors = avg_conference_visitors
        self.avg_employees_per_company = avg_employees_per_company

        self.student_cards = set()

    def get_student_card(self):
        card_id = ''.join(str(random.randint(1,9)) for _ in range(6))
        while card_id in self.student_cards:
            card_id = ''.join(str(random.randint(1,9)) for _ in range(6))

        self.student_cards.add(card_id)
        return card_id

    def generate(self):
        """
        Create conferences
        Create workshops
        Create private clients
        Create company clients + employees
        Create reservations per conference
        """

        no_of_conferences, visitors = self.add_conferences()
        workshop_ids = self.add_workshops()
        companies_ids, companies_employees = self.add_companies(no_of_conferences, visitors)
        private_customers, person_ids = self.add_private_customers(no_of_conferences, visitors)
        conferences_ids, company_reservations_dict, private_reservations_dict = self.add_reservations(no_of_conferences, private_customers, companies_ids)
        self.add_discounts(conferences_ids)
        participants_dict = self.add_conference_day_reservations(
            conferences_ids, company_reservations_dict, private_reservations_dict,
            companies_employees, person_ids
        )
        slots, workshop_instances = self.add_workshops_to_conferences(conferences_ids, workshop_ids)
        self.add_workshop_reservations(slots, workshop_instances, participants_dict)
        cursor.execute('SELECT ConferenceId FROM Conferences')
        self.set_paid_at_dates([conf_id for conf_id, in cursor.fetchall()])

    def add_discounts(self, conferences_ids):
        for conference_id, max_part, start in conferences_ids:
            if random.randint(0, 1) == 0:
                continue

            start = parse(start)
            discount = random.uniform(0.2, 0.6)
            rounded_discount = round(discount, 1)

            number_of_discounts = random.randint(1, 3)
            for i in range(number_of_discounts):
                discount_start = start - relativedelta.relativedelta(months=number_of_discounts - i)
                discount_end = discount_start + relativedelta.relativedelta(months=1)

                procedures.AddDiscount.exec({
                    'conference_id': conference_id,
                    'start': discount_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': discount_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'discount': rounded_discount / (i+1)
                })

    def add_workshop_reservations(self, slots, workshop_instances, participants_dict):
        """

        :param slots: {conference_day: {workshop_id: time}
        :param workshop_instances:
        :param participants_dict: {conference_day: [person_ids]}
        :return:
        """

        print('Creating workshop reservations...')
        days_dict = {}
        for conference_day_id, workshop_id, workshop_instance_id, max_part in workshop_instances:
            if conference_day_id not in days_dict:
                days_dict[conference_day_id] = []
            days_dict[conference_day_id].append((workshop_id, workshop_instance_id, max_part))

        for conference_day_id, workshops in tqdm(days_dict.items()):
            already_reserved = {}

            for workshop_id, workshop_instance_id, max_part in workshops:
                batch = []
                time_slot = slots[conference_day_id][workshop_id]
                random.shuffle(participants_dict[conference_day_id])
                for person_id, cdr_id in participants_dict[conference_day_id]:
                    if person_id not in already_reserved:
                        already_reserved[person_id] = set()

                    if time_slot not in already_reserved[person_id]:
                        batch.append((workshop_instance_id, cdr_id, person_id))
                        already_reserved[person_id].add(time_slot)

                    if len(batch) >= max_part:
                        break

                cursor.executemany("""
                    INSERT INTO [dbo].[WorkshopReservations]
                           ([WorkshopInstanceId]
                           ,[ConferenceDayReservationId]
                           ,[PersonId])
                     VALUES
                           (%s, %s, %s)
                """, batch[:max_part])
                conn.commit()

    def add_reservations(self, no_of_conferences, private_customers, companies_ids):
        cursor.execute('SELECT TOP {} ConferenceId, MaxParticipants, StartDate FROM Conferences ORDER BY ConferenceId DESC'.format(no_of_conferences))
        conferences_ids = [(conf_id, max_part, start) for conf_id, max_part, start in cursor.fetchall()]

        print('Adding reservations...')
        for conference_id, max_part, start in tqdm(conferences_ids):
            start = parse(start) - relativedelta.relativedelta(days=3)
            first_reservation = start - relativedelta.relativedelta(months=3)
            days = (start - first_reservation).days

            private = int(max_part * random.uniform(0.4, 0.6))
            companies = max_part - private

            random.shuffle(private_customers)
            for customer_id in private_customers[:private]:
                reservation_date = first_reservation + relativedelta.relativedelta(days=random.randint(0, days))
                reservation_date = reservation_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))

                procedures.CreateReservation.exec({
                    'customer_id': customer_id,
                    'conference_id': conference_id,
                    'reservation_date': reservation_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            random.shuffle(companies_ids)
            for customer_id in companies_ids[:int(companies / self.avg_employees_per_company)]:
                reservation_date = first_reservation + relativedelta.relativedelta(days=random.randint(0, days))
                reservation_date = reservation_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))

                procedures.CreateReservation.exec({
                    'customer_id': customer_id,
                    'conference_id': conference_id,
                    'reservation_date': reservation_date.strftime('%Y-%m-%d %H:%M:%S')
                })

        conn.commit()

        cursor.execute('SELECT CustomerId, ReservationId, ConferenceId FROM Reservations WHERE CustomerId IN ({})'.format(','.join(map(lambda x: str(x), companies_ids))))
        company_reservations = [(customer_id, reservation_id, conference_id) for customer_id, reservation_id, conference_id in cursor.fetchall()]
        company_reservations_dict = {}  # {conference id : [(reservation_id, customer_id)]
        for customer_id, reservation_id, conference_id in company_reservations:
            if conference_id not in company_reservations_dict:
                company_reservations_dict[conference_id] = []
            company_reservations_dict[conference_id].append((reservation_id, customer_id))

        cursor.execute('SELECT CustomerId, ReservationId, ConferenceId FROM Reservations WHERE CustomerId IN ({})'.format(','.join(map(lambda x: str(x), private_customers))))
        private_reservations = [(customer_id, reservation_id, conference_id) for customer_id, reservation_id, conference_id in cursor.fetchall()]
        private_reservations_dict = {}  # {conference id : [(reservation_id, customer_id)]
        for customer_id, reservation_id, conference_id in private_reservations:
            if conference_id not in private_reservations_dict:
                private_reservations_dict[conference_id] = []
            private_reservations_dict[conference_id].append((reservation_id, customer_id))

        return conferences_ids, company_reservations_dict, private_reservations_dict

    def add_conference_day_reservations(self, conferences_ids, companies_reservations_dict, private_reservation_dict,
                                        companies_employees, person_ids):

        conferences_ids_only = [conference_id for conference_id, _, _ in conferences_ids]
        cursor.execute('SELECT ConferenceId, ConferenceDayId FROM ConferenceDays WHERE ConferenceId IN ({})'.format(','.join(map(lambda x: str(x), conferences_ids_only))))
        days_dict = {}
        for conference_id, conference_day_id in cursor.fetchall():
            if conference_id not in days_dict:
                days_dict[conference_id] = []
            days_dict[conference_id].append(conference_day_id)

        private_people_dict = {
            customer_id: person_id
            for customer_id, person_id in person_ids
        }

        print('Adding conference day reservations...')
        for conference_id, max_part, start in tqdm(conferences_ids):
            batch = []
            for conference_day_id in days_dict[conference_id]:
                semi_batch = []
                for reservation_id, customer_id in private_reservation_dict.get(conference_id, []):
                    semi_batch.append((conference_day_id, reservation_id, private_people_dict[customer_id]))
                    # procedures.ReserveConferenceDayInsert.exec({
                    #     'person_id': private_people_dict[customer_id],
                    #     'reservation_id': reservation_id,
                    #     'conference_day_id': conference_day_id
                    # })

                for reservation_id, customer_id in companies_reservations_dict.get(conference_id, []):
                    employees = companies_employees.get(customer_id, [])
                    random.shuffle(employees)
                    number_of_employees = random.randint(int(len(employees) * 0.8), len(employees))
                    for person_id in employees[:number_of_employees]:
                        semi_batch.append((conference_day_id, reservation_id, person_id))
                        # procedures.ReserveConferenceDayInsert.exec({
                        #     'conference_day_id': conference_day_id,
                        #     'reservation_id': reservation_id,
                        #     'person_id': person_id
                        # })
                batch += semi_batch[:max_part]

            cursor.executemany("""
            INSERT INTO [dbo].[ConferenceDayReservations]
                       ([ConferenceDayId]
                       ,[Reservationid]
                       ,[PersonId])
                 VALUES
                       (%s, %s, %s)
            """, batch)
            conn.commit()

        cursor.execute('''
          SELECT cdr.ConferenceDayReservationId, cd.ConferenceDayId, cdr.PersonId
          FROM ConferenceDayReservations cdr
          INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = cdr.ConferenceDayId
          WHERE cd.ConferenceId IN ({})
          '''.format(','.join(map(lambda x: str(x), conferences_ids_only))))

        participants_dict = {}
        for cdr_id, conference_day_id, person_id in cursor.fetchall():
            if conference_day_id not in participants_dict:
                participants_dict[conference_day_id] = []
            participants_dict[conference_day_id].append((person_id, cdr_id))

        return participants_dict


    def add_workshops_to_conferences(self, conferences_ids, workshop_ids):
        conferences_ids_only = [conference_id for conference_id, _, _ in conferences_ids]
        cursor.execute('SELECT ConferenceId, ConferenceDayId, Day FROM ConferenceDays WHERE ConferenceId IN ({})'.format(
            ','.join(map(lambda x: str(x), conferences_ids_only))
        ))

        days = {}
        for conference_id, conference_day_id, day in cursor.fetchall():
            day = parse(day)
            if conference_id not in days:
                days[conference_id] = []

            days[conference_id].append((conference_day_id, day))

        slots = [
            ((12, 00), (13, 00)),
            ((13, 00), (14, 00)),
            ((14, 00), (15, 00)),
        ]

        workshops_slots = {}

        print('Adding workshops to conference days...')
        for conference_id, max_part, conference_start in tqdm(conferences_ids):
            workshops = copy.copy(workshop_ids)
            random.shuffle(workshops)

            for conference_day_id, day in days[conference_id]:
                workshops_slots[conference_day_id] = {}

                for start, end in slots:
                    for _ in range(random.randint(1, 2)):
                        if len(workshops) > 0:
                            price = random.uniform(0, 500)
                            rounded_price = round(price, -(len(str(int(price))) - 2))

                            workshop_id = workshops.pop(0)
                            procedures.AddWorkshopToConferenceDay.exec({
                                'workshop_id': workshop_id,
                                'conference_day_id': conference_day_id,
                                'max_participants': random.randint(int(max_part/2), max_part),
                                'price': rounded_price,
                                'start_date': day.replace(hour=start[0], minute=start[1], second=0),
                                'end_date': day.replace(hour=end[0], minute=end[1], second=0)
                            })

                            workshops_slots[conference_day_id][workshop_id] = start

        conn.commit()

        cursor.execute('''
          SELECT wi.ConferenceDayId, wi.WorkshopId, wi.WorkshopInstanceId, wi.MaxParticipants FROM WorkshopInstances wi
          INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = wi.ConferenceDayId
          WHERE cd.ConferenceId IN ({})
        '''.format(','.join(map(lambda x: str(x), conferences_ids_only))))

        return workshops_slots, [(conference_day_id, workshop_id, workshop_instance_id, max_part)
                                     for conference_day_id, workshop_id, workshop_instance_id, max_part in cursor.fetchall()]

    def set_paid_at_dates(self, conferences_ids):
        cursor.execute('''
        SELECT r.ReservationId, r.ReservationDate, c.StartDate FROM Reservations r
        INNER JOIN Conferences c ON c.ConferenceId = r.ConferenceId
        WHERE r.ConferenceId IN ({})
        '''.format(','.join(map(lambda x: str(x), conferences_ids))))

        reservations = [(reservation_id, reservation_date, start) for reservation_id, reservation_date, start in cursor.fetchall()]
        batch = []
        print('Setting PaymentDates...')
        for res_id, date_s, conf_start_s in tqdm(reservations):
            date = parse(date_s) if isinstance(date_s, str) else date_s
            conf_start = parse(conf_start_s) if isinstance(conf_start_s, str) else conf_start_s

            payment_after_days = random.randint(0, (conf_start - date).days - 1)

            payment_date = date + relativedelta.relativedelta(days=payment_after_days)
            payment_date = payment_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))

            batch.append((
                payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                res_id
            ))

            if len(batch) >= 100:
                cursor.executemany(
                    "UPDATE Reservations SET PaymentDate=%s WHERE ReservationId=%d",
                    batch
                )
                conn.commit()
                batch = []

        cursor.executemany(
            "UPDATE Reservations SET PaymentDate=%s WHERE ReservationId=%d",
            batch
        )
        conn.commit()

    def add_private_customers(self, no_of_conferences, visitors):
        company_to_private_ratio = 0.2
        retention = 0.7
        private_customers = int(company_to_private_ratio * sum(visitor for visitor in visitors) * (1-retention))
        print('Adding private customers...')
        for index in tqdm(range(private_customers)):
            params = {
                'email': fake.email(),
                'phone': int(''.join(fake.phone_number().split(' '))),
                'first_name': fake.first_name(),
                'last_name': fake.last_name()
            }

            procedures.AddPrivateCustomer.exec(params)

        conn.commit()
        cursor.execute('SELECT TOP {} CustomerId, PersonId FROM PrivateCustomers ORDER BY CustomerId DESC'.format(private_customers))
        person_ids = [(customer_id, person_id) for customer_id, person_id in cursor.fetchall()]
        customers_ids = []
        for customer_id, person_id in person_ids:
            customers_ids.append(customer_id)
            if random.randint(0, 1) == 1:
                procedures.AddStudentCard.exec({'person_id': person_id, 'student_card_id': self.get_student_card()})

        return customers_ids, person_ids

    def add_companies(self, no_of_conferences, visitors):
        company_to_private_ratio = 0.8
        retention = 0.7

        company_visitors_count = company_to_private_ratio * sum(visitor for visitor in visitors) * (1-retention)
        no_of_companies = int(company_visitors_count /self.avg_employees_per_company)

        companies_employees = {}
        employees_counts = fixed_mean_random(self.avg_employees_per_company, 3, no_of_companies)
        print('Adding companies...')
        for i in tqdm(range(no_of_companies)):
            procedures.AddCompanyCustomer.exec({
                'email': fake.company_email(),
                'phone': int(''.join(fake.phone_number().split(' '))),
                'company_name': fake.company(),
                'city': fake.city(),
                'street': fake.street_name(),
                'street_number': fake.building_number(),
                'postal_code': fake.postcode(),
                'nip': int(''.join(str(random.randint(1,9)) for _ in range(10))),
            }, autocommit=True)
        conn.commit()

        cursor.execute('SELECT TOP {} CustomerId FROM Companies ORDER BY CustomerId DESC'.format(no_of_companies))
        companies_ids = [customer_id for customer_id, in cursor.fetchall()]

        print('Adding employees...')
        for i, customer_id in enumerate(tqdm(companies_ids)):
            for index in range(employees_counts[i]):
                params = {
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'company_id': customer_id
                }

                procedures.AddEmployee.exec(params)

        conn.commit()

        cursor.execute('SELECT PersonId, CompanyId FROM Employees WHERE CompanyId IN ({})'.format(','.join(map(lambda x: str(x), companies_ids))))
        for person_id, company_id in cursor.fetchall():
            if company_id not in companies_employees:
                companies_employees[company_id] = []
            companies_employees[company_id].append(person_id)

            if random.randint(0, 1) == 1:
                procedures.AddStudentCard.exec({'person_id': person_id, 'student_card_id': self.get_student_card()})
        conn.commit()

        return companies_ids, companies_employees

    def add_workshops(self):
        count = 0
        print('Adding workshops...')
        for topic in tqdm(workshops_topics):
            for lang in conference_technology:
                procedures.AddWorkshop.exec({
                    'name': '{} {}'.format(topic, lang),
                    'description': 'Introduction to {} {}'.format(topic, lang)
                })
                count += 1

        conn.commit()

        cursor.execute('SELECT TOP {} WorkshopId FROM Workshops ORDER BY WorkshopID DESC'.format(
            count
        ))
        return [workshop_id for workshop_id, in cursor.fetchall()]


    def add_conferences(self):
        start = datetime.datetime.now() - relativedelta.relativedelta(years=self.years)
        start = start.replace(day=1)
        conferences_per_month = fixed_mean_random(self.conferences_per_month, 1, self.years * 12)
        all_conferences = sum(amount for amount in conferences_per_month)
        visitors = fixed_mean_random(self.avg_conference_visitors, 5, all_conferences)
        counter = 0
        print('Adding conferences...')
        for no_of_conferences in tqdm(conferences_per_month):
            for _ in range(no_of_conferences):
                length = random.randint(self.conference_min_length, self.conference_max_length)
                start = start.replace(day=random.randint(1, 20))
                end = start + relativedelta.relativedelta(days=length - 1)

                price = random.uniform(50, 1000)
                rounded_price = round(price, -(len(str(int(price))) - 2))

                name = '{} {} - {} {}'.format(
                    random_part(conference_adj),
                    random_part(conference_technology),
                    random_part(conference_city),
                    start.strftime('%Y')
                )

                procedures.AddConference.exec({
                    'name': name,
                    'start_date': start.strftime('%Y-%m-%d'),
                    'end_date': end.strftime('%Y-%m-%d'),
                    'price': rounded_price,
                    'max_participants': visitors[counter],
                    'student_discount': round(random.uniform(0, 1), 2)
                })

                counter += 1

            start = start + relativedelta.relativedelta(months=1)

        conn.commit()

        return all_conferences, visitors
