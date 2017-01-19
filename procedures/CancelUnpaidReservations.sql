CREATE PROCEDURE [CancelUnpaidReservations]
AS
  DELETE FROM Reservations
  WHERE DATEADD(DAY, 7, ReservationDate) < GETDATE() AND PaymentDate IS NULL