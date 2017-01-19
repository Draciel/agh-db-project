CREATE PROCEDURE [ReserveConferenceDay]
    @PersonId        BIGINT,
    @ReservationId   BIGINT,
    @ConferenceDayId BIGINT
AS
  BEGIN
    IF (dbo.AvailableSeatsAtConferenceDay(@ConferenceDayId) > 0)
      BEGIN
        INSERT INTO [dbo].[ConferenceDayReservations]
        ([ConferenceDayId]
          , [Reservationid]
          , [PersonId])
        VALUES
          (@ConferenceDayId
            , @ReservationId
            , @PersonId);
      END
    ELSE
      RAISERROR ('No more seats are available for this conference day', 10, 1);
  END
