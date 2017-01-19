CREATE FUNCTION IsWorkshopTimeValidForPerson(@PersonId BIGINT, @WorkshopInstanceId BIGINT)
  RETURNS BIT
AS
  BEGIN
    DECLARE @return AS BIT
    DECLARE @colidingWorkshops AS BIT
    DECLARE @Day AS DATE
    DECLARE @Start AS DATETIME
    DECLARE @End AS DATETIME
    DECLARE @ConferenceDayId AS BIGINT
    DECLARE @ConferenceDayReservationId AS BIGINT

    SELECT
        @Start = StartDate,
        @End = EndDate,
        @ConferenceDayId = ConferenceDayId
    FROM WorkshopInstances
    WHERE WorkshopInstanceId = @WorkshopInstanceId;


    SET @ConferenceDayReservationId = (
      SELECT cr.ConferenceDayReservationId
      FROM ConferenceDayReservations cr
      WHERE cr.PersonId = @PersonId AND cr.ConferenceDayId = @ConferenceDayId
    )

    /* return error if @ConferenceDayReservationId null */

    SET @return = 1
    IF (
         SELECT 1
         FROM WorkshopReservations wr
           INNER JOIN WorkshopInstances wi ON wi.WorkshopInstanceId = wr.WorkshopInstanceId
         WHERE
           wr.PersonId = @PersonId
           AND wr.ConferenceDayReservationId = @ConferenceDayReservationId
           AND wr.WorkshopInstanceId != @WorkshopInstanceId
           AND (
             (wi.StartDate BETWEEN @Start AND @End)
             OR (wi.EndDate BETWEEN @Start AND @End)
           )
       ) = 1
      BEGIN
        SET @return = 0
      END

    RETURN @return
  END
