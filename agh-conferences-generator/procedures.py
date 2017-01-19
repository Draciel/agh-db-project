import pyodbc
import pymssql
from db import cursor, conn


class Procedure:
    name = None
    query_params = []
    query = 'EXEC dbo.{} {}'

    @classmethod
    def exec(cls, params, autocommit=False):
        fields = [
            '{' + param + '}' if not quote else '\'{' + param + '}\''
            for param, quote in cls.query_params
        ]
        final_params = ','.join(fields)
        final_query = cls.query.format(cls.name, final_params).format(**params)
        res = cursor.execute(final_query)

        if autocommit:
            conn.commit()

class AddConference(Procedure):
    name = 'AddConference'
    query_params = (
        ('name', True),
        ('start_date', True),
        ('end_date', True),
        ('max_participants', False),
        ('price', False),
        ('student_discount', False)
    )


class AddWorkshop(Procedure):
    name = 'AddWorkshop'
    query_params = (
        ('name', True),
        ('description', True)
    )


class AddDiscount(Procedure):
    name = 'AddDiscount'
    query_params = (
        ('conference_id', False),
        ('start', True),
        ('end', True),
        ('discount', False)
    )


class AddPrivateCustomer(Procedure):
    name = 'AddPrivateCustomer'
    query_params = (
        ('first_name', True),
        ('last_name', True),
        ('email', True),
        ('phone', False)
    )


class AddCompanyCustomer(Procedure):
    name = 'AddCompanyCustomer'
    query_params = (
        ('email', True),
        ('phone', False),
        ('company_name', True),
        ('street', True),
        ('street_number', True),
        ('postal_code', True),
        ('city', True),
        ('nip', True)
    )


class AddEmployee(Procedure):
    name = 'AddEmployee'
    query_params = (
        ('first_name', True),
        ('last_name', True),
        ('company_id', False)
    )

class AddStudentCard(Procedure):
    name = 'AddStudentCard'
    query_params = (
        ('person_id', False),
        ('student_card_id', True)
    )


class AddWorkshopToConferenceDay(Procedure):
    name = 'AddWorkshopToConferenceDay'
    query_params = (
        ('workshop_id', False),
        ('conference_day_id', False),
        ('max_participants', False),
        ('price', False),
        ('start_date', True),
        ('end_date', True)
    )


class ReserveWorkshop(Procedure):
    name = 'ReserveWorkshop'
    query_params = (
        ('person_id', False),
        ('workshop_instance_id', False)
    )


class ReserveConferenceDay(Procedure):
    name = 'ReserveConferenceDay'
    query_params = (
        ('person_id', False),
        ('reservation_id', False),
        ('conference_day_id', False)
    )


class ReserveWorkshopInsert(Procedure):
    @classmethod
    def exec(cls, params, autocommit=False):
        cursor.execute("""
        INSERT INTO [dbo].[WorkshopReservations]
               ([WorkshopInstanceId]
               ,[ConferenceDayReservationId]
               ,[PersonId])
         VALUES
               ({workshop_instance_id}
               ,{conference_day_reservation_id}
               ,{person_id})
        """.format(**params))


class ReserveConferenceDayInsert(Procedure):
    @classmethod
    def exec(cls, params, autocommit=False):
        cursor.execute("""
        INSERT INTO [dbo].[ConferenceDayReservations]
                   ([ConferenceDayId]
                   ,[Reservationid]
                   ,[PersonId])
             VALUES
                   ({conference_day_id}
                   ,{reservation_id}
                   ,{person_id})
        """.format(**params))


class CreateReservation(Procedure):
    name = 'CreateReservation'
    query_params = (
        ('customer_id', False),
        ('conference_id', False),
        ('reservation_date', True)
    )