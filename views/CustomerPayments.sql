CREATE VIEW CustomerPayments AS
  SELECT
    r.ReservationId,
    r.ReservationDate,
    r.PaymentDate,
    c.CustomerId,
    CASE WHEN cm.CustomerId IS NOT NULL
      THEN cm.CompanyName
    ELSE CONCAT(p.FirstName, ' ', p.LastName) END AS CustomerName,
    c.Email,
    c.Phone
  FROM Reservations r
    INNER JOIN Customers c ON c.CustomerId = r.CustomerId
    LEFT JOIN Companies cm ON cm.CustomerId = c.CustomerId
    LEFT JOIN PrivateCustomers pc ON pc.CustomerId = c.CustomerId
    LEFT JOIN People p ON p.PersonId = pc.PersonId
