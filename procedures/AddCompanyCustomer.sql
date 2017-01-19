CREATE PROCEDURE [AddCompanyCustomer]
    @Email        VARCHAR(50),
    @Phone        BIGINT,
    @CompanyName  VARCHAR(35),
    @Street       VARCHAR(35),
    @StreetNumber VARCHAR(10),
    @PostalCode   VARCHAR(6),
    @City         VARCHAR(30),
    @NIP          VARCHAR(10)
AS
  BEGIN
    DECLARE @CustomerId AS BIGINT

    BEGIN TRANSACTION;
    BEGIN TRY
    INSERT INTO [dbo].[Customers]
    ([Email], [Phone])
    VALUES
      (@Email, @Phone);

    SET @CustomerId = SCOPE_IDENTITY()

    INSERT INTO [dbo].[Companies]
    ([CustomerId]
      , [CompanyName]
      , [Street]
      , [StreetNumber]
      , [PostalCode]
      , [City]
      , [NIP])
    VALUES
      (@CustomerId
        , @CompanyName
        , @Street
        , @StreetNumber
        , @PostalCode
        , @City
        , @NIP);
    COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
      ROLLBACK;
      EXECUTE ShowError;
    END CATCH;
  END

