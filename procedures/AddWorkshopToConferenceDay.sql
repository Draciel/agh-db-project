CREATE PROCEDURE [AddWorkshopToConferenceDay]
    @WorkshopId      BIGINT,
    @ConferenceDayId BIGINT,
    @MaxParticipants INT,
    @Price           MONEY,
    @StartDate       DATETIME,
    @EndDate         DATETIME
AS
  BEGIN

    IF dbo.DuringConferenceDay(@StartDate, @EndDate, @ConferenceDayId) = 1
      BEGIN
        INSERT INTO [dbo].[WorkshopInstances]
        ([WorkshopId]
          , [ConferenceDayId]
          , [MaxParticipants]
          , [Price]
          , [StartDate]
          , [EndDate])
        VALUES
          (@WorkshopId
            , @ConferenceDayId
            , @MaxParticipants
            , @Price
            , @StartDate
            , @EndDate);
      END
    ELSE
      BEGIN
        RAISERROR ('Workshop can not be added in this timeframe, it has to match conference day timeframe', 10, 1);
      END
  END