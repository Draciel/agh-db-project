CREATE VIEW [Invoices] AS
  SELECT
    r.ReservationId,
    c.ConferenceId,
    c.Name                                        AS ConferenceName,
    r.CustomerId,
    CASE WHEN cm.CustomerId IS NOT NULL
      THEN cm.CompanyName
    ELSE CONCAT(p.FirstName, ' ', p.LastName) END AS CustomerName,
    cm.NIP,
    cm.Street,
    cm.StreetNumber,
    cm.PostalCode,
    cm.City,
    (
      SELECT COUNT(PersonId)
      FROM ConferenceDayReservations
      WHERE ReservationId = r.ReservationId
    )                                             AS ConferenceDayReservationsCount,
    (
      SELECT COUNT(wr.PersonId)
      FROM WorkshopReservations wr
        INNER JOIN ConferenceDayReservations cdr ON cdr.ConferenceDayReservationId = wr.ConferenceDayReservationId
      WHERE cdr.ReservationId = r.ReservationId
    )                                             AS WorkshopReservationsCount,
    (
      SELECT SUM(wi.Price)
      FROM WorkshopReservations wr
        INNER JOIN ConferenceDayReservations cdr ON wr.ConferenceDayReservationId = cdr.ConferenceDayReservationId
        INNER JOIN WorkshopInstances wi ON wi.WorkshopInstanceId = wr.WorkshopInstanceId
      WHERE cdr.ReservationId = r.ReservationId
      GROUP BY cdr.ReservationId
    ) + (
      SELECT SUM(Price * (1 - StudentDiscount) * (1 - ConferenceDiscount))
      FROM (
             SELECT
               re.ReservationId,
               CASE WHEN (s.StudentCardNumber IS NOT NULL)
                 THEN c.StudentDiscount
               ELSE 0 END AS StudentDiscount,
               c.Price,
               CASE WHEN (SELECT Discount
                          FROM Discounts
                          WHERE ConferenceId = re.ConferenceId AND
                                re.ReservationDate BETWEEN StartDate AND EndDate) IS NOT NULL
                 THEN (SELECT Discount
                       FROM Discounts
                       WHERE ConferenceId = re.ConferenceId AND
                             re.ReservationDate BETWEEN StartDate AND EndDate)
               ELSE 0 END AS ConferenceDiscount
             FROM ConferenceDayReservations cdr
               LEFT JOIN Students s ON s.PersonId = cdr.PersonId
               INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = cdr.ConferenceDayId
               INNER JOIN Conferences c ON c.ConferenceId = cd.ConferenceId
               INNER JOIN Reservations re ON re.ReservationId = cdr.ReservationId) prices
      WHERE ReservationId = r.ReservationId
      GROUP BY ReservationId
    )                                             AS TotalAmount
  FROM Reservations r
    INNER JOIN Conferences c ON c.ConferenceId = r.ConferenceId
    INNER JOIN Customers cu ON cu.CustomerId = r.CustomerId
    LEFT JOIN Companies cm ON cm.CustomerId = cu.CustomerId
    LEFT JOIN PrivateCustomers pc ON pc.CustomerId = cu.CustomerId
    LEFT JOIN People p ON p.PersonId = pc.PersonId