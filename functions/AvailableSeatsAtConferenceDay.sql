CREATE FUNCTION AvailableSeatsAtConferenceDay(@ConferenceDayId BIGINT)
  RETURNS INT
AS
  BEGIN
    DECLARE @return AS INT
    DECLARE @MaxParticipants AS INT
    DECLARE @CurrentParticipants AS INT

    SET @MaxParticipants = (SELECT c.MaxParticipants
                            FROM ConferenceDays cd
                              INNER JOIN Conferences c ON c.ConferenceId = cd.ConferenceId
                            WHERE cd.ConferenceDayId = @ConferenceDayId)

    SET @CurrentParticipants = (SELECT COUNT(PersonId)
                                FROM ConferenceDayReservations
                                WHERE ConferenceDayId = @ConferenceDayId)

    SET @return = @MaxParticipants - @CurrentParticipants
    RETURN @return
  END
