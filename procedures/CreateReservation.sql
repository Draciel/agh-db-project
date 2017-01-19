CREATE PROCEDURE CreateReservation
    @CustomerId      VARCHAR(35),
    @ConferenceId    VARCHAR(35),
    @ReservationDate DATETIME = NULL
AS
  BEGIN

    IF @ReservationDate IS NULL
      BEGIN
        SET @ReservationDate = GETDATE()
      END

    INSERT INTO [dbo].[Reservations]
    ([ConferenceId]
      , [CustomerId]
      , [ReservationDate])
    VALUES
      (@ConferenceId
        , @CustomerId
        , @ReservationDate);

  END
