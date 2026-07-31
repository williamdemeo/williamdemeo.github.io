+++
layout = "page"
title = "update alternatives"
date = 2014-03-13
+++

Here are some notes on `update-alternatives` and some examples demonstrating its
use. The purpose of the update-alternatives utility program is to manage,
on a single machine, serveral versions of programs that all provide the same
functionality. 

---------------------

## Contents
- [Synopsis](#synopsis)
- [Examples](#examples)
	- [Eclipse](#eclipse)
	- [Java](#java)
	- [Ruby](#ruby)

----------------------------------------------

## Synopsis 

Excerpts from the
[update-alternatives man page](http://linux.die.net/man/8/update-alternatives):

It is possible for several programs fulfilling the same or similar functions to
be installed on a single system at the same time. Debian's alternatives system
aims to manage this situation.  A generic name in the filesystem is shared by
all files providing interchangeable functionality.  The alternatives system and
the system administrator together determine which actual file is referenced by
this generic name.  

The generic name is not a direct symbolic link to the selected alternative.
Instead, it is a symbolic link to  a  name in the alternatives  directory, which
in turn is a symbolic link to the actual file referenced.  This is done so that 
the system administrator's changes can be confined within the /etc directory.

When  each  package  providing a file with a particular functionality is
installed, changed or removed, update-alternatives is called to update
information about that file in  the  alternatives  system. 

-----------------------------------------------------------

## Examples

### Eclipse

Eclipse seems idosyncratic and tempremental to me, and I have found various
versions working well sometimes and poorly other times.  Also, there are useful
plugins that are only available for some versions and not others.

I currently have three versions of Eclipse installed---a
[version from TypeSafe][] and two
[simultaneous releases](http://wiki.eclipse.org/Simultaneous_Release): 
[Kepler][] and [Luna][] (a developer build).
(The version from TypeSafe is just a Kepler release with 
the Scala IDE plugin preinstalled.  Note that you can manually install the Scala
IDE plugin with other versions Eclipse.)
This section describes how to get these multiple versions of Eclipse to happily
coexist on the same machine.  

If you don't already have any Eclipse versions installed, see 
[the appendix](#installing-multiple-versions-of-eclipse)
for some installation links and tips.

-------------------------

**Create startup scripts** This step may become optional in the future, but it
seems for now it provides a workaround to deal with bugs in Ubuntu and/or
Eclipse that effect the Eclipse menus.

For each version of Eclipse, create a startup script that includes any options that
would otherwise be added to the command line when launching Eclipse.
For example, in the file `$HOME/opt/Eclipse/kepler/eclipse-kepler`, put

    #!/bin/bash
    export UBUNTU_MENUPROXY=0
    $HOME/opt/Eclipse/kepler/eclipse -vmargs -Xmx4096M

The option `-vmargs -Xmx4096M` sets the available memory to 4096 Mb.  You can
either adjust or remove this parameter to suit your hardware.  In fact, this
seems to cause problems with some versions of the IDE, so it may be safer to
leave it off unless you run into memory problems without it.

See
[this page](http://wiki.eclipse.org/FAQ_How_do_I_increase_the_heap_size_available_to_Eclipse%3F)
for more about the vmargs command line uption.

The line `export UBUNTU_MENUPROXY=0` was added to work around
[a bug](http://stackoverflow.com/questions/19452390/eclipse-menus-dont-show-up-after-upgrading-to-ubuntu-13-10)
that causes problems with Eclipse's menus.

Now, make the file you just created executable; e.g.,

    chmod a+x $HOME/opt/Eclipse/kepler/eclipse-kepler

To summarize, here are three example startup scripts I use for three different
versions of Eclipse:

In the file `$HOME/opt/Eclipse/luna/eclipse-luna`,

        #!/bin/bash
        export UBUNTU_MENUPROXY=0
        $HOME/opt/Eclipse/luna/eclipse

In the file `$HOME/opt/Eclipse/kepler/eclipse-kepler`,

        #!/bin/bash
        export UBUNTU_MENUPROXY=0
        $HOME/opt/Eclipse/kepler/eclipse

In, the file `$HOME/opt/Eclipse/scala/eclipse-scala`

        #!/bin/bash
        export UBUNTU_MENUPROXY=0
        $HOME/opt/Eclipse/scala/eclipse

-------------------------

Assuming each of your versions of Eclipse is stored in it own directory under
`$HOME/opt/Eclipse`
(as described in [the appendix](#installing-multiple-versions-of-eclipse)),
you can now configure these various versions of Eclipse by invoking the
following at the command line:

	sudo update-alternatives --install /usr/bin/eclipse eclipse $HOME/opt/Eclipse/scala/eclipse-scala 400
	sudo update-alternatives --install /usr/bin/eclipse eclipse $HOME/opt/Eclipse/luna/eclipse-luna 300
	sudo update-alternatives --install /usr/bin/eclipse eclipse $HOME/opt/Eclipse/kepler/eclipse-kepler 200

The numbers 200, 300, 400 indicate the respective priorities, and
since scala has the highest number, it will be the default program (but we can
change the default later).

You can remove any alternative that you added accidentally. For example, 

	sudo update-alternatives --remove eclipse $HOME/opt/Eclipse/scala/eclipse-scala
	
The command `update-alternatives --query eclipse` should now print something
like this:

    Name: eclipse
    Link: /usr/bin/eclipse
    Status: auto
    Best: /home/williamdemeo/opt/Eclipse/scala/eclipse-scala
    Value: /home/williamdemeo/opt/Eclipse/scala/eclipse-scala

    Alternative: /home/williamdemeo/opt/Eclipse/kepler/eclipse-kepler
    Priority: 200

    Alternative: /home/williamdemeo/opt/Eclipse/luna/eclipse-luna
    Priority: 300

    Alternative: /home/williamdemeo/opt/Eclipse/scala/eclipse-scala
    Priority: 400


Now, or later, you can change the priority of these three alternative versions of
Eclipse with the command `update-alternatives --config eclipse`, which
should output the following: 

    There are 3 choices for the alternative eclipse (providing /usr/bin/eclipse).

      Selection    Path                                                  Priority   Status
    ------------------------------------------------------------
    * 0            /home/williamdemeo/opt/Eclipse/scala/eclipse-scala     400       auto mode
      1            /home/williamdemeo/opt/Eclipse/kepler/eclipse-kepler   200       manual mode
      2            /home/williamdemeo/opt/Eclipse/luna/eclipse-luna       300       manual mode
      3            /home/williamdemeo/opt/Eclipse/scala/eclipse-scala     400       manual mode


If you want to create an application launcher for the Unity dash for any of
these alternatives, or any program for that matter, do so as follows:

    mkdir -p ~/.local/share/applications
    gnome-desktop-item-edit --create-new ~/.local/share/applications/
	
Click on the icon in the dialog box that pops up, and choose, for
example, `$HOME/opt/Eclipse/scala/icon.xpm`.  Fill in the rest of the dialog box
as appropriate. For example, you want the Command field to point to one of the bash
scripts we created above---like `$HOME/opt/Eclipse/scala/eclipse-scala`---and
not directly to an `eclipse` command.


----------------------------------------------------------

### Java
After downloading JDK 7 from the
[Oracle JDK 7 downloads page](http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html).
I unpacked it and moved it to a directory called /usr/lib/jvm/jdk1.7.0/. I then
made it the default Java on my machine using the commands below. (The first
block of 9 commands can be copy-and-pasted to the command line all at once.) 
		
        sudo update-alternatives --install "/usr/bin/java" "java" "/usr/lib/jvm/jdk1.7.0/bin/java" 1;
        sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/jvm/jdk1.7.0/bin/javac" 1;
        sudo update-alternatives --install "/usr/bin/javaws" "javaws" "/usr/lib/jvm/jdk1.7.0/bin/javaws" 1;
        sudo update-alternatives --install "/usr/bin/jcontrol" "jcontrol" "/usr/lib/jvm/jdk1.7.0/bin/jcontrol" 1;
        sudo chmod a+x /usr/bin/java;
        sudo chmod a+x /usr/bin/javac;
        sudo chmod a+x /usr/bin/javaws;
        sudo chmod a+x /usr/bin/jcontrol;
        sudo chown -R root:root /usr/lib/jvm/jdk1.7.0;

The following commands are interactive and should be invoked individually:
		
        sudo update-alternatives --config java
        sudo update-alternatives --config javac
        sudo update-alternatives --config javaws
        sudo update-alternatives --config jcontrol


----------------------------------------------------------

### Ruby

This example comes from an old
[forum post](https://groups.google.com/forum/#!topic/rails-oceania/iislbRF9tJ8)


    # install ruby1.8 & friends with priority 500
    # so this will be the default "auto" choice
    update-alternatives --install /usr/bin/ruby ruby /usr/bin/ruby1.8 500 \
                        --slave   /usr/share/man/man1/ruby.1.gz ruby.1.gz \
                                      /usr/share/man/man1/ruby.1.8.gz \
                        --slave   /usr/bin/ri ri /usr/bin/ri1.8 \
                        --slave   /usr/bin/irb irb /usr/bin/irb1.8 

    # install ruby1.9 & friends with priority 400
    update-alternatives --install /usr/bin/ruby ruby /usr/bin/ruby1.9 400 \
                        --slave   /usr/share/man/man1/ruby.1.gz ruby.1.gz \
                                       /usr/share/man/man1/ruby.1.9.gz \
                        --slave   /usr/bin/ri ri /usr/bin/ri1.9 \
                        --slave   /usr/bin/irb irb /usr/bin/irb1.9 

    # choose your interpreter 
    # changes symlinks for /usr/bin/ruby , 
    # /usr/bin/irb, /usr/bin/ri and man (1) ruby
    update-alternatives --config ruby 


----------------------------------

## Appendix

### Installing multiple versions of Eclipse

1. Make a directory under your home directory called `~/opt/Eclipse`.

2. Download the versions of Eclipse you want to 
   try---e.g., [Luna][], [Kepler][], the [version from TypeSafe][]---and 
   place the tar.gz files in `~/opt/Eclipse`.

3. Untar each tar.gz file, and rename it appropriately.  For example,

        tar xvzf eclipse-standard-luna-M6-linux-gtk-x86_64.tar.gz 
		mv eclipse luna

   That is, each time you untar one of these files, the resulting directory will
   be called eclipse.  You should change the name eclipse to the name of the
   version so that they don't conflict with one another.
   
   In the end you should have, say, three directories:
   
        ~/opt/Eclipse/luna
        ~/opt/Eclipse/kepler
        ~/opt/Eclipse/scala
		
   each one containing a different version of Eclipse.  Now you can follow the
   instructions above to get them configured as alternatives in Linux.

### Out of Memory Errors

If you are getting out of memory erros when running your programs in Eclipse,
check out
[this page](http://wiki.eclipse.org/FAQ_How_do_I_increase_the_heap_size_available_to_Eclipse%3F).


[Luna]:	https://www.eclipse.org/downloads/index-developer.php
[Kepler]: http://www.eclipse.org/downloads/
[version from TypeSafe]: http://scala-ide.org/download/sdk.html


