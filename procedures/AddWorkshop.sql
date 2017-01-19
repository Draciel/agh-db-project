CREATE PROCEDURE [AddWorkshop]
    @Name        VARCHAR(50),
    @Description VARCHAR(255)
AS
  INSERT INTO [dbo].[Workshops]
  ([Name], [Description])
  VALUES
    (@Name, @Description);