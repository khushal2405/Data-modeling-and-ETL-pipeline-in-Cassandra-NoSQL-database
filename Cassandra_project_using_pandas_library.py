#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import cassandra
import re
import os
import glob
import numpy as np
import json
import csv


# In[18]:


# checking current working directory
print(f"Current working directory : {os.getcwd()}")

# Get current folder and subfolder event data
filepath = os.getcwd() + '/event_data'

# Create a list of files and collect each filepath
for root, dirs, files in os.walk("event_data_cassandra_project"):
    
# join the file path and roots with the subdirectories using glob
    file_path_list = glob.glob(os.path.join(root,'*'))
    #print(file_path_list)


# In[19]:


df = pd.DataFrame()
for f in file_path_list:
    df1 = pd.read_csv(f)
    df = df.append(df1,ignore_index=True)


# In[20]:


df.to_csv('event_datafile_new.csv')


# In[21]:


# checking the number of rows in new event csv file
with open('event_datafile_new.csv', 'r', encoding = 'utf8') as f:
    print(sum(1 for line in f))


# In[ ]:


#creating cluster
# This should make a connection to a Cassandra instance your local machine 
# (127.0.0.1)

from cassandra.cluster import Cluster
try:
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    print("Connection Established !!")
except Exception as e:
    print(f"Connection Failed !! Error : {e}")


# In[ ]:


#creating keyspace
keyspace_query = """CREATE KEYSPACE IF NOT EXISTS sparkify 
                    with REPLICATION = 
                    { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }
                """

# Creating Keyspace
try:
    session.execute(keyspace_query)
except Exception as e:
    print(f"Failed to create keyspace!! Error : {e}")


# In[23]:


# Setting KEYSPACE to the keyspace specified above
session.set_keyspace('sparkify')


# In[24]:


# query1: SELECT artist, song, length FROM session_item where sessionId = 338 and itemInSession = 4
#so out primary key will be (sessionId, itemInSession), where sessionId is the partition key and itemInSession is the clustering column.
create_query1 = """CREATE TABLE IF NOT EXISTS session_item (artist text, song text, length float, sessionId int, itemInSession int, PRIMARY KEY (sessionId, itemInSession))"""

try: 
    session.execute(create_query1)
    print("Table Created!!")
except Exception as e:
    print(f"Table creation failed!! Error : {e}")


# In[ ]:


# Using the event file
file = 'event_datafile_new.csv'

# Reading csv file and inserting rows into cassandra tables.
with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
        query = "INSERT INTO session_item (artist, song, length, sessionId, itemInSession) "
        query = query + " VALUES (%s, %s, %s, %s, %s) "
        session.execute(query, (line[0], line[10], float(line[5]), int(line[8]), int(line[3])) )


# In[ ]:


# SELECT statement to verify the data was entered into the table
select_query1 = "SELECT artist, song, length FROM  session_item where sessionId = 338 and itemInSession = 4"
try:
    rows = session.execute(select_query1)
except Exception as e:
    print(e)
    
for row in rows:
    print(row)


# In[ ]:


# query2: SELECT artist, song, firstName, lastName FROM user_session where sessionId = 182 and userId = 10
#Our Primary key will be ((sessionId, userId), itemInSession)), where (sessionId, userId) is the partition key and itemInSession is the clustering column.


# In[ ]:


# Creating table for query2 
create_query2 = """CREATE TABLE IF NOT EXISTS user_session (sessionId int, userId int, artist text, song text, firstName text, lastName text, itemInSession int, PRIMARY KEY ((sessionId, userId), itemInSession)) WITH CLUSTERING ORDER BY (itemInSession ASC) """

try: 
    session.execute(create_query2)
    print("Table Created!!")
except Exception as e:
    print(f"Table creation failed!! Error : {e}")


# In[ ]:


file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
        query = "INSERT INTO user_session (sessionId, userId, artist, song, firstName, lastName, itemInSession) "
        query = query + " VALUES (%s, %s, %s, %s, %s, %s, %s) "
        session.execute(query, (int(line[8]), int(line[10]), line[0], line[9], line[1], line[4], int(line[3])  ) )


# In[ ]:


# SELECT statement to verify the data was entered into the table
select_query2 = "SELECT artist, song, firstName, lastName FROM  user_session where sessionId = 182 and userId = 10"
try:
    rows = session.execute(select_query2)
except Exception as e:
    print(e)

for row in rows:
    print(row)


# In[ ]:


# query3:  SELECT song, firstName, lastName FROM user_song where song = 'All Hands Against His Own'
# Our Primary key will be ((song), userId)), where song is the partition key and userId is the clustering column.
# Creating table for query3

create_query3 = """CREATE TABLE IF NOT EXISTS user_song (song text, userId int, firstName text, lastName text, PRIMARY KEY ((song), userId))"""

try: 
    session.execute(create_query3)
    print("Table Created!!")
except Exception as e:
    print(f"Table creation failed!! Error : {e}")


# In[ ]:


file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
        query = "INSERT INTO user_song (song, userId, firstName, lastName) "
        query = query + " VALUES (%s, %s, %s, %s) "
        session.execute(query, (  line[9], int(line[10]), line[1], line[4] )  )
        


# In[ ]:


# SELECT statement to verify the data was entered into the table
select_query2 = "SELECT song, firstName, lastName FROM user_song where song = 'All Hands Against His Own'"
try:
    rows = session.execute(select_query2)
except Exception as e:
    print(e)

for row in rows:
    print(row)


# In[ ]:


#closing session and cluster
session.shutdown()
cluster.shutdown()

