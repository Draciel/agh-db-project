CREATE PROCEDURE [AddConference]
    @Name            VARCHAR(60),
    @StartDate       DATETIME,
    @EndDate         DATETIME,
    @MaxParticipants INT,
    @Price           MONEY,
    @StudentDiscount FLOAT
AS
  BEGIN
    DECLARE @ConferenceId AS BIGINT
    DECLARE @CurrentDate AS DATE

    SET @CurrentDate = CAST(@StartDate AS DATE)

    BEGIN TRANSACTION;
    BEGIN TRY
    INSERT INTO [dbo].[Conferences]
    ([Name]
      , [StartDate]
      , [EndDate]
      , [MaxParticipants]
      , [Price]
      , [StudentDiscount])
    VALUES
      (@Name
        , @StartDate
        , @EndDate
        , @MaxParticipants
        , @Price
        , @StudentDiscount);

    SET @ConferenceId = SCOPE_IDENTITY()

    WHILE (@CurrentDate <= CAST(@EndDate AS DATE))
      BEGIN
        INSERT INTO [dbo].[ConferenceDays]
        ([ConferenceId], [Day])
        VALUES
          (@ConferenceId, @CurrentDate);

        SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
      END

    COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
      ROLLBACK;
      EXECUTE ShowError;
    END CATCH;

  END
