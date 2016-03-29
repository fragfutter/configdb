### flask frontend
anything can do a http get.

either put a complete update or send subdocuments or field updates

map/format configdata from/to json objects.

generate document fields from IP addresses.

### mongodb backend
every configfile is just a document. 

every application can have it's own collection

every application defines it's own idgeneration. Hostname, application name,
instance name, etc.

#### negatives
ldap/kerberos is enterprise feature

### couchdb
erlang, http interface. Authentication delegated to apache. -> ldap, kerberos. 


### meta
attach meta information to each document. 
