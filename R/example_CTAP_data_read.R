

#install.packages("RSQLite")
require(RSQLite)

# Open connection
db.file <- '/ukko/projects/ReKnow/Data/processed/ReKnowPilot/export/psdres.sqlite'
sqlite    <- dbDriver("SQLite")
exampledb <- dbConnect(sqlite, db.file)

# Get structure information
dbListTables(exampledb)
dbListFields(exampledb, "subject")
dbListFields(exampledb, "measurement")
dbListFields(exampledb, "restab")

# Load test data
df <- dbGetQuery(exampledb, "SELECT * FROM restab LIMIT 100")
str(df)
head(df)

# Load all data from two variables
dbGetQuery(exampledb, "SELECT DISTINCT VARIABLE FROM restab")
df <- dbGetQuery(exampledb, 'SELECT * FROM restab WHERE VARIABLE IN ("P8_13_abs","P8_13_rel")')
str(df)
unique(df$variable)
unique(df$channel)
xtabs(~channel+variable, data=df)








dbDisconnect(exampledb)
