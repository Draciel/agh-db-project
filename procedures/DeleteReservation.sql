CREATE PROCEDURE DeleteReservation
    @ReservationId      bigint
AS
  BEGIN
    DELETE FROM [dbo].[Reservations]
    WHERE ReservationId=@ReservationId;
  END
