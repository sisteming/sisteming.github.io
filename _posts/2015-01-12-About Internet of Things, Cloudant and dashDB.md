---
layout: post
date: 2015-01-12 11:00:00
title: About Internet of Things, Cloudant and dashDB
---

Happy New Year my friends!

I hope you all had a relaxing holiday and enjoyed a good time with a lot of *FFF* moments: Family, Friends and Food (I let you decide the order you prefer!!!)

I am back after a good break and revisiting the blog I know we left this with dashDB. 
As we head into this new year, I am pretty sure that many cool things will come for dashDB, so in the meantime, I will go through one of the features I personally like the most about dashDB.

## **Situation**

We live in a world where lots of data are being generated every day. From traditional online services, to social media or connected services, it is all about data. And probably you already heard about IoT: Internet of Things. This will easily increase the amount of data we generate and have available to analyze. Just as a matter of fact, I bet the presence of wearable devices as Christmas gifts was important this year, with many other devices starting to go in the direction and generating for us more more data!

I will go through some cool gadgets and sensors for IoT in a future post, but for now my question is: 

*How do we store all this data coming from devices, social media, sensors?* 

*How can we analyze this data to get insights on the information that is useful to us?*

This is where the connection of Systems of Engagement to Systems of Record has a strategic importance.

## **Connecting Systems of Engagement to Systems of Record**

Systems of Engagements definition can be checked here: 
[Systems of Engagement - Wikipedia](http://en.wikipedia.org/wiki/Systems_of_Engagement)

Examples of these are social media platform, sensors, connected devices, wearables...

Systems of Record instead are what we all know by traditional IT systems where we store data, like our loved databases!

One example of connecting both kind of systems is offered by dashDB and Cloudant. We can have data coming from systems of engagements like sensors or social media platforms like Twitter stored into a JSON NoSQL database on Cloudant. Then this data can be seamlessly synchronized into a table inside our dashDB database to have the power of SQL (and R!) to analyze and visualize data coming from our NoSQL database.


#### *Internet of Things, Raspberry Pi and Cloudant*

I will show you here how easy is to have our data synchronized from Cloudant into dashDB.

As an example, I will use a NodeRed application deployed in BlueMix and using the Internet of Things foundation application ([Internet of Things Foundation - BlueMix](https://internetofthings.ibmcloud.com/))

![IoT]({{ site.baseurl }}/images/IOTfund.png)

Basically, I have at home a RaspberryPi, running an agent and sending device information to the IoT platform on BlueMix. With this, I am able to retrieve the information from my device and work with it to for example store it in a JSON datastore on Cloudant.

To do this step, I can easily use the following module on NodeRed, and it will store the information retrieved from my Raspberry Pi at home (CPU load or temperature) into my Cloudant database previously created.

![NodeRed]({{ site.baseurl }}/images/nodered_model.png)

#### *Connecting Cloudant to dashDB*

Now that I am ready and storing my RaspberryPi data into Cloudant, we can go and connect dashDB to our Cloudant database. 

To do this, we just need to deploy a new dashDB service into our BlueMix dashboard by selecting dashDB from the catalog:

![dashDB]({{ site.baseurl }}/images/dashdb_cat.png)

Once the service is deployed, we just go to "Manage" -> "Sync from Cloudant".
The screen is very simple and we just have to include our Cloudant database API URL and our login details. In this case, my database has been given the read privilege for everybody (inside Cloudant), so I do not need to add those details. 
We also select a table prefix that will be added to the table created inside dashDB and containing the data from Cloudant.

Once all the information is ready, we just start to sync the database and we can see the information progress like this: 

![Cloudant Sync]({{ site.baseurl }}/images/cloudantsync1.png)

This process will discover the document structure of the Cloudant datastore to create the necessary table structure inside our relational database in dashDB.
This just takes a few seconds and when is completed, we will receive the confirmation that the data sync from Cloudant is in progress - and currently working!

![Cloudant Sync]({{ site.baseurl }}/images/cloudantsync2.png)

This is it. Done. By these simple steps, we have now all the data from our Cloudant database synchronized seamlessly into dashDB ready to be analyzed or visualized to get the insights we need. And remember, this is a continuous replication, so any data added to the Cloudant database will be in sync in dashDB too!

#### *Working with my data*

Now I only have to go to "Manage" -> "Work with Tables" in dashDB to access the table created during this process. The table name will start by iot_* as it was the table prefix I selected during the setup.

After a quick look at the table and its data, I am all set to run a quick query to verify the information I need about my Raspberry Pi CPU load and temperature!

![Query Cloudant data]({{ site.baseurl }}/images/dashdb_querydata.png)


This is it for today my friends!

I hope you enjoyed this quick view on dashDB and how to synchronize data from Cloudant! 

Feel free to add any question on the comments below or just add me on Twitter! [@marcobonezzi](https://twitter.com/marcobonezzi)