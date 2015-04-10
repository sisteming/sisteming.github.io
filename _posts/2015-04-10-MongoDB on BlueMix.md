---
layout: post
date: 2015-04-01 21:45:00
title: MongoDB on BlueMix
---

Hi my friends!

For some reasons that I will explain in a future post, I have been looking at MongoDB and I was curious about its availability on BlueMix.

## MongoDB on BlueMix? Why not?

The progress of MongoDB in the last few years has been very successful. As a sign of this, it is getting more and more used, specially for modern web applications with Node.js, Python, Angular.js or even the so popular now *MEAN* framework.

On the other side, BlueMix is also getting popular and more and more services are being added each month. It is interesting to see how many services are being implemented not only from IBM but also from the community or third parties.

This is the case for MongoDB on BlueMix, where we have two possible alternatives to use.


## MongoDB NoSQL database (community)

Many applications developed on BlueMix are using MongoDB. For simple applications deployed within BlueMix, this service from the community 
can be used. 

![MongoDB service details]({{ site.baseurl }}/images/mongodb_community.png)

Once we bind the service to our application, we are able to connect the application to our new MongoDB database. Whether we use Node.js, Java or Ruby, we can find the instructions to connect to our MongoDB database from [Getting started with MongoDB service](https://www.ng.bluemix.net/docs/#services/MongoDB/index.html#MongoDB)

![Getting Started with MongoDB]({{ site.baseurl }}/images/gettingstarted.png)

## MongoLab (third party)

According to the BlueMix service description, MongoLab is a fully-managed cloud database service featuring highly-available MongoDB databases, automated backups, web-based tools, 24/7 monitoring, and expert support.

![Mongolab service]({{ site.baseurl }}/images/mongolab.png)

From the service console on mongolab, we can easily see our mongodb databases, collections, and create even more just with few clicks.

![Mongolab Console details]({{ site.baseurl }}/images/mongolab_detail.png)

![Mongolab Connection details]({{ site.baseurl }}/images/mongolab_detail2.png)

### Getting your hards dirty

Why don't you try yourself to see what could suit you better?

Here is an interesting article that will show you how to build a real-time poll application with Node.js, Express, AngularJS and MongoDB. And yes, all on Bluemix!

![Build a real-time polls application with Node.js, Express, AngularJS, and MongoDB](https://www.ibm.com/developerworks/library/wa-nodejs-polling-app/)

Have you already used one of the services and have a preference? Or have you implemented the application in the tutorial above?
Feel free to drop me a comment below!



