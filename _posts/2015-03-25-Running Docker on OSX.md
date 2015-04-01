---
layout: post
date: 2015-03-25 21:45:00
title: Running Docker on OS X
---

Hello my friends!

I know it has been quite a long time since the last entry in here!
These have been busy months with travels and changes... more on that in a future post! ;)

Today I want to talk about Docker...

Yes, probably most of you are already aware of it. And fewer maybe already did something with it. Oh, and is there anyone who does not know it yet??

## Docker? What is that?

So you haven't heard about Docker yet? Not too bad... 
It also happens with some colleagues, I was recently in a conversation and mentioned Docker and some of them did not know what I was talking about...

To get yourself up to date and know something more on Docker, have a look at my previous post which also contains useful links and video!

**[What is Docker and why everyone likes it?](http://sisteming.github.io/2014/12/03/What%20is%20Docker%20and%20why%20everyone%20likes%20it%3F/)**

**[Docker containers arriving to Bluemix!](http://sisteming.github.io/2014/12/05/Docker%20containers%20arriving%20to%20BlueMix/)**

There is also a great book on Docker which I recommend to buy, it is definitely worth it:

**[The Docker Book](http://www.dockerbook.com/)**


## Ok ok, I want to try it!!

Feeling ready to try it? In that case, get ready to use your command line and have some fun!
Depending on the OS you're using there will be different instructions. 
In my case, I use OS X on my Macbook so I had to look for some nice tutorials to set up the environment!

First I found a really good guide with lots of details on Docker and how to get it working on OS X. Recently, I found a way that looks easier than the first, so I will let you choose your preferred option! 

#### The hard way

This guide will show you very interesting details on Docker like how it works, how it works on Linux, how it is on OS X and all the required steps to get it to work on OS X using Virtualbox and boot2docker. 

I have to say that it's not as hard as it could seem and this will give you more details on some interesting points of docker on your local machine.

[How to use docker on OS X - The missing guide](http://viget.com/extend/how-to-use-docker-on-os-x-the-missing-guide)

#### The easiest way

I recently came accross to [kitematic](https://kitematic.com/), a project that claims to be the easiest way to use Docker on your Mac!

![kitematic]({{ site.baseurl }}/images/kitematic.png)

Well, I can tell you they must be pretty good given that know it is also part of Docker itself!

From a quick try, it looks like it will do the following tasks for you just by opening the app

	-Install Docker and VirtualBox
	-Start Docker VM
	
Once the Docker VM is started, you will get a nice app showing your containers and some recommended already defined images. 

![kitematic App]({{ site.baseurl }}/images/kitematicApp.png)

This seems too easy right? 

![kitematic New container]({{ site.baseurl }}/images/kitematicNewC.png) {: .minipic}

Well, you just select 'Create' on the image you want to use and in seconds (literally!) your new container will be created from the chosen image.

![kitematic container created]({{ site.baseurl }}/images/kitematic_cont.png)

This is cool, isn't it?

## Is there future for Docker?

When I first heard about containers and Docker, my initial thought was that this may be something more to play around or for Dev environments.
Recently Docker is getting more and more attention. But the definitive spark that got me more insterested about it was when I heard that a client was using it for their development environment for DB2!

### Enterprise Docker?

Last month, I was lucky enough to attend IBM conference about Cloud and lots of other stuff, IBM Interconnect. 

It was indeed interesting to see how different products and projects are going to use Docker as base for cloud or virtualized environment.

But it was even cooler when I spotted a Docker booth at the Expo! I definitely went to speak with them and it was great to hear some of their plans. And... of course to get a Docker t-shirt and some stickers too!

![Docker booth]({{ site.baseurl }}/images/dockerbooth.jpeg)

![Docker sticker]({{ site.baseurl }}/images/dockersticker.png)

What do you think about Docker? Are you using it? Have you tried it? 

Feel free to drop a comment with your thoughts below, I will be happy to discuss!


