+++
title= "java on linux"
date= 2016-12-06
+++
<!-- 
---
layout: post
title: "java on linux"
date: 2017-12-06 20:41:09 -0700
comments: true
categories: 
--- -->


This post details the steps I use to update or install
the latest version of the Java Development Kit (JDK) on 
my Linux systems.

<!-- more -->

(These notes are mainly for my own reference, but also
come in handy when I need to something to point to when
a colleague or student needs to know how to do this.)

### Download the latest JDK from Oracle

http://www.oracle.com/technetwork/java/javase/downloads/index.html

I'll assume we're using Linux on an x64 machine, so we would,
for example, download a file with a name like

`jdk-9.0.1_linux-x64_bin.tar.gz`

(As of Dec 6, 2018, the direct link to this file is [here](http://download.oracle.com/otn-pub/java/jdk/9.0.1+11/jdk-9.0.1_linux-x64_bin.tar.gz))


### Unpack the tar.gz file downloaded in step 1

I'll assume we downloaded the tar.gz file into the directory `~/opt/Java`

    tar xvzf jdk-9.0.1_linux-x64_bin.tar.gz
    
### Set up the `/usr/lib/jvm` directory

1. create the directory `/usr/lib/jvm`

        sudo mkdir -p /usr/lib/jvm

2. If you already have directory named `/usr/lib/jvm/jdk-9.0.1`, move it out of the way:
   
        sudo mv /usr/lib/jvm/jdk-9.0.1{,.orig}

3. Move your newly unpacked jdk directory to `/usr/lib/jvm` and rename it `jdk1.9.0`:
   
        sudo mv ~/opt/Java/jdk-9.0.1 /usr/lib/jvm/jdk1.9.0
	
### Make jdk1.9.0 the default Java on your system

Use the `update-alternatives` program for this (see also: [notes on configuring JDK 1.7 on Ubuntu](http://askubuntu.com/questions/55848/how-do-i-install-oracle-java-jdk-7)):

This first block of 9 commands can be copy-and-pasted to the command line all at once:
		
        sudo update-alternatives --install "/usr/bin/java" "java" "/usr/lib/jvm/jdk1.9.0/bin/java" 1;
        sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/jvm/jdk1.9.0/bin/javac" 1;
        sudo update-alternatives --install "/usr/bin/javaws" "javaws" "/usr/lib/jvm/jdk1.9.0/bin/javaws" 1;
    		sudo update-alternatives --install "/usr/bin/jcontrol" "jcontrol" "/usr/lib/jvm/jdk1.9.0/bin/jcontrol" 1;
        sudo chmod a+x /usr/bin/java;
        sudo chmod a+x /usr/bin/javac;
        sudo chmod a+x /usr/bin/javaws;
        sudo chmod a+x /usr/bin/jcontrol;
        sudo chown -R root:root /usr/lib/jvm/jdk1.9.0;

The following commands are interactive and should be invoked individually:
		
        sudo update-alternatives --config java
  
        sudo update-alternatives --config javac
  
        sudo update-alternatives --config javaws
  
        sudo update-alternatives --config jcontrol

Check which version of Java your system is currently using with the command `java -version`.
