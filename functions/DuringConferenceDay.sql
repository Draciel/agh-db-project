CREATE FUNCTION DuringConferenceDay(@StartDate DATETIME, @EndDate DATETIME, @ConferenceDayId BIGINT)
  RETURNS BIT
AS
  BEGIN
    DECLARE @return AS BIT
    DECLARE @Day AS DATE

    SET @return = 0
    SET @Day = (SELECT Day
                FROM ConferenceDays
                WHERE ConferenceDayId = @ConferenceDayId)

    SET @return = (SELECT 1
                   WHERE CAST(@StartDate AS DATE) = @Day AND CAST(@EndDate AS DATE) = @Day)
    IF @return IS NULL
      BEGIN
        SET @return = 0
      END

    RETURN @return
  END
