CREATE PROCEDURE DeleteWorkshopReservation
    @ConferenceDayReservationId   BIGINT,
    @WorkshopInstanceId BIGINT
AS
  BEGIN
    DELETE FROM [dbo].[WorkshopReservations]
    WHERE ConferenceDayReservationId = @ConferenceDayReservationId AND WorkshopInstanceId = @WorkshopInstanceId;
  END
