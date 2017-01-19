/****** Script for SelectTopNRows command from SSMS  ******/
EXEC AddConference 'Conference', '2017-01-01', '2017-01-03', 500, 250, 0.5

SELECT * FROM Conferences WHERE Name='Conference'

SELECT * FROM ConferenceDays cd INNER JOIN Conferences c ON c.ConferenceId = cd.ConferenceId
WHERE c.Name='Conference'

EXEC AddWorkshop 'Java', 'Workshop about Java'
SELECT * FROM Workshops WHERE Name='Java'

EXEC AddDiscount 1739, '2016-08-01', '2016-09-01', 0.5

/* workshopid, conferencedayid, maxparticipants, price, start, end*/
EXEC AddWorkshopToConferenceDay 1684, 4292, 150, 15, '2017-01-01 14:00:00', '2017-01-01 15:00:00'
SELECT * FROM WorkshopInstances WHERE WorkshopId=1684 AND ConferenceDayId=4292

EXEC AddPrivateCustomer 'Jan', 'Kowalski', 'jan@kowa.pl', 123456789, '777777'
SELECT * FROM PrivateCustomers pc
INNER JOIN Customers c ON c.CustomerId = pc.CustomerId
INNER JOIN People p ON p.PersonId = pc.PersonId
WHERE c.Email = 'jan@kowa.pl'

EXEC AddCompanyCustomer 'company@company.com', 123456789, 'Company name', 'Czarnowiejska', '11a', '34-340', 'Kraków', '1234567890' 
SELECT * FROM Companies c
INNER JOIN Customers cu ON cu.CustomerId = c.CustomerId
WHERE cu.Email = 'company@company.com'

EXEC AddEmployee 'Adam', 'Nowak', 2680, '654654'
SELECT * FROM Employees e
INNER JOIN People p ON p.PersonId = e.PersonId
INNER JOIN Companies c ON c.CustomerId = e.CompanyId
WHERE c.CustomerId = 2680

EXEC AddStudentCard 9080, '000000'

/* customerid, conferenceid, reservationdate=GETDATE() */
EXEC CreateReservation 2680, 1739
SELECT * FROM Reservations WHERE ConferenceId=1739 AND CustomerId=2680

/* personid, reservationid, conferencedayid */
EXEC ReserveConferenceDay 9080, 6447, 4292
SELECT * FROM ConferenceDayReservations WHERE ReservationId=6447

/* personid, workshopinstanceid */
EXEC ReserveWorkshop 9080, 3375
SELECT * FROM WorkshopReservations WHERE PersonId=9080 AND WorkshopInstanceId=3375

EXEC DeleteReservation 6447

/* personid, reservationid, conferencedayid*/
EXEC DeleteConferenceDayReservation

/*conferencedayreservationid, workshopinstanceid */
EXEC DeleteWorkshopReservation

SELECT COUNT(1) FROM Reservations