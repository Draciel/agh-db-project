CREATE PROCEDURE DeleteConferenceDayReservation
    @PersonId        BIGINT,
    @ReservationId   BIGINT,
    @ConferenceDayId BIGINT
AS
  BEGIN
    DELETE FROM [dbo].[ConferenceDayReservations]
    WHERE ReservationId = @ReservationId AND PersonId = @PersonId AND ConferenceDayId = @ConferenceDayId;
  END
