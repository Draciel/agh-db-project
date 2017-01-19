CREATE PROCEDURE [ReserveWorkshop]
    @PersonId           BIGINT,
    @WorkshopInstanceId BIGINT
AS
  BEGIN

    DECLARE @ConferenceDayId AS BIGINT
    DECLARE @ConferenceDayReservationId AS BIGINT

    SET @ConferenceDayId = (SELECT cd.ConferenceDayId
                            FROM WorkshopInstances wi
                              INNER JOIN ConferenceDays cd ON cd.ConferenceDayId = wi.ConferenceDayId
                            WHERE wi.WorkshopInstanceId = @WorkshopInstanceId)

    SET @ConferenceDayReservationId = (SELECT ConferenceDayReservationId
                                       FROM ConferenceDayReservations
                                       WHERE ConferenceDayId = @ConferenceDayId AND PersonId = @PersonId
    )

    IF dbo.IsWorkshopTimeValidForPerson(@PersonId, @WorkshopInstanceId) = 1
      BEGIN
        RAISERROR ('This person has already reserved another workshop which takes place simultaneously', 10, 1);
        RETURN;
      END

    IF dbo.AvailableSeatsAtWorkshop(@WorkshopInstanceId) > 0
      BEGIN

        INSERT INTO [dbo].[WorkshopReservations]
        ([WorkshopInstanceId]
          , [ConferenceDayReservationId]
          , [PersonId])
        VALUES
          (@WorkshopInstanceId
            , @ConferenceDayReservationId
            , @PersonId)
      END
    ELSE
      BEGIN
        RAISERROR ('No more seats available or this person has already reserved another workshop which takes place simultaneously', 10, 1);
      END

  END
