CREATE PROCEDURE AddEmployee
    @FirstName VARCHAR(35),
    @LastName  VARCHAR(35),
    @CompanyId BIGINT
AS
  BEGIN
    DECLARE @PersonId AS BIGINT

    BEGIN TRANSACTION;
    BEGIN TRY
    INSERT INTO [dbo].[People]
    ([FirstName], [LastName])
    VALUES
      (@FirstName, @LastName);
    SET @PersonId = SCOPE_IDENTITY()

    INSERT INTO [dbo].[Employees]
    ([PersonId], [CompanyId])
    VALUES
      (@PersonId, @CompanyId);
    COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
      ROLLBACK;
      EXECUTE ShowError;
    END CATCH

  END