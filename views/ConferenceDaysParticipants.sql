CREATE VIEW ConferenceDaysParticipants
AS
  SELECT
    c.ConferenceId,
    c.Name,
    cd.ConferenceDayId,
    cd.Day,
    p.PersonId,
    p.FirstName,
    p.LastName
  FROM ConferenceDayReservations cdr
    INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = cdr.ConferenceDayId
    INNER JOIN People p ON p.PersonId = cdr.PersonId
    INNER JOIN Conferences c ON c.ConferenceId = cd.ConferenceId
