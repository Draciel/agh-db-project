CREATE PROCEDURE AddStudentCard
    @PersonId          BIGINT,
    @StudentCardNumber VARCHAR(6)
AS
  INSERT INTO [dbo].[Students]
  ([PersonId]
    , [StudentCardNumber])
  VALUES
    (@PersonId
      , @StudentCardNumber)