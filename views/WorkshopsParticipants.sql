CREATE VIEW WorkshopsParticipants
AS
  SELECT
    c.ConferenceId,
    c.Name AS ConferenceName,
    wi.WorkshopInstanceId,
    w.WorkshopId,
    w.Name AS WorkshopName,
    wi.StartDate,
    wi.EndDate,
    p.PersonId,
    p.FirstName,
    p.LastName
  FROM WorkshopReservations wr
    INNER JOIN People p ON p.PersonId = wr.PersonId
    INNER JOIN ConferenceDayReservations cdr ON cdr.ConferenceDayReservationId = wr.ConferenceDayReservationId
    INNER JOIN WorkshopInstances wi ON wi.WorkshopInstanceId = wr.WorkshopInstanceId
    INNER JOIN Workshops w ON w.WorkshopId = wi.WorkshopId
    INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = wi.ConferenceDayId
    INNER JOIN Conferences c ON c.ConferenceId = cd.ConferenceId
