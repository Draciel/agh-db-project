CREATE PROCEDURE AddDiscount
    @ConferenceId BIGINT,
    @StartDate    DATETIME,
    @EndDate      DATETIME,
    @Discount     FLOAT
AS
  BEGIN
    DECLARE @ConferenceStart AS DATE
    SET @ConferenceStart = (SELECT StartDate FROM Conferences WHERE ConferenceId=@ConferenceId)

    IF @StartDate > @ConferenceStart
      BEGIN
        RAISERROR ('Discounted timeframe can not start after the conference', 10, 1);
        RETURN;
      END

    IF @EndDate > @ConferenceStart
      BEGIN
        RAISERROR ('Discounted timeframe can not end after the conference', 10, 1);
        RETURN;
      END

    INSERT INTO [dbo].[Discounts]
    ([ConferenceId]
      , [StartDate]
      , [EndDate]
      , [Discount])
    VALUES
      (@ConferenceId
        , @StartDate
        , @EndDate
        , @Discount)
  END