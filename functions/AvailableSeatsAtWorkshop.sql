CREATE FUNCTION AvailableSeatsAtWorkshop(@WorkshopInstanceId BIGINT)
  RETURNS INT
AS
  BEGIN
    DECLARE @return AS INT
    DECLARE @CurrentParticipants AS INT
    DECLARE @MaxParticipants AS INT

    SET @MaxParticipants = (SELECT wi.MaxParticipants
                            FROM WorkshopInstances wi
                            WHERE wi.WorkshopInstanceId = @WorkshopInstanceId)

    SET @CurrentParticipants = (SELECT COUNT(wr.PersonId)
                                FROM WorkshopReservations wr
                                  INNER JOIN WorkshopInstances wi ON wi.WorkshopInstanceId = wr.WorkshopInstanceId
                                WHERE wr.WorkshopInstanceId = @WorkshopInstanceId)

    SET @return = @MaxParticipants - @CurrentParticipants
    RETURN @return
  END
