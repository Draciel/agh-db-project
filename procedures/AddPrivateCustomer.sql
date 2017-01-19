CREATE PROCEDURE AddPrivateCustomer
    @FirstName VARCHAR(35),
    @LastName  VARCHAR(35),
    @Email     VARCHAR(50),
    @Phone     BIGINT
AS BEGIN
  DECLARE @PersonId AS BIGINT
  DECLARE @CustomerId AS BIGINT

  BEGIN TRANSACTION;
  BEGIN TRY
    INSERT INTO [dbo].[Customers]
    ([Email], [Phone])
    VALUES
      (@Email, @Phone);

    SET @CustomerId = SCOPE_IDENTITY()

    INSERT INTO [dbo].[People]
    ([FirstName]
      , [LastName])
    VALUES
      (@FirstName, @LastName);
    SET @PersonId = SCOPE_IDENTITY()

    INSERT INTO [dbo].[PrivateCustomers]
    ([CustomerId]
      , [PersonId])
    VALUES
      (@CustomerId, @PersonId);

    COMMIT TRANSACTION;
  END TRY
  BEGIN CATCH
    ROLLBACK;
    EXECUTE ShowError;
  END CATCH;
END
