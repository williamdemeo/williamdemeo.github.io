---
title: reactive
date: '2015-04-18'
---

These are *very rough* personal notes from a Coursera course I took in 2015 called
[Principles of Reactive Programming](https://www.coursera.org/course/reactive)
by Martin Odersky, Erik Meijer, Roland Kuhn.

The link to the version of the course that I took is
[https://class.coursera.org/reactive-002](https://class.coursera.org/reactive-002).

General information about the course and possible future sessions is found at
[https://www.coursera.org/course/reactive](https://www.coursera.org/course/reactive).

--------------------------------

# Getting Started! (Assignment 0)

This is the first assignment.  The goal is to familiarize yourself with the
infrastructure and the tools required during this class. The grade
in this assignment will be excluded from your final grade for the course.

## Part 0: Install Required Tools
Before anything else, we need to make sure that all tools are
correctly installed. Take a look at the
[Tools Setup](https://class.coursera.org/reactive-002/wiki/ToolsSetup) page and
verify that all of the listed tools work.

(If you already did all this for the progfun course, you don't need to do anything more.)

## Part 1: Obtain the Project Files
Download the
[example.zip](https://d28rh4a8wq0iu5.cloudfront.net/reactive/assignments/example.zip)
handout archive file and extract it somewhere on your machine. 

## Part 2: Make sure the Scala REPL is working
During this class we will always launch the Scala REPL (the interactive Scala
console) through sbt, so we don't need to install the Scala
distribution---having sbt is enough. (In case you prefer to have the scala
command, you can download the Scala distribution from 
the [scala-lang.org website](http://www.scala-lang.org/downloads).) 

**Note that `sbt` can only be started inside a project directory**, so we first
navigate to the example directory created in Part 1, then enter `sbt`.


In the future, we can type `console` to get the Scala REPL, but for now, just type

    > eclipse

at the sbt prompt to generate the files needed to load the project into
Eclipse.  See next section for more details.  You can exit sbt with `ctrl-c`.

(If something goes wrong with sbt, open the
[Sbt Tutorial](https://class.coursera.org/reactive-002/wiki/SbtTutorial)
page and follow the first steps until "Running the Scala Interpreter.")

-------------------

## Part 3: Opening the Project in Eclipse

To work on the source code of the project, we must import it into
Eclipse.

### 3.1. Creating the Eclipse project from sbt

**IMPORTANT** Before importing the project into Eclipse, we must first create
the Eclipse project from the sbt command line as mentioned above.

    $ sbt
    > eclipse
    ...

### 3.2. Importing the Project in Eclipse

Once the Eclipse project has been created from sbt, you can import it in
Eclipse. Follow these steps to work on the project using the Scala IDE: 

1. Start up Eclipse
2. Select "File" - "Import" from the menu
3. In the folder "General", select the item "Existing Projects into Workspace" and click "Next >"
4. In the textfield "Select root directory:" select the directory where you unpacked the downloaded handout archive
5. Click "Finish".

### 3.3. Working with Eclipse
In the folder `src/main/scala`, open the package `example` and double-click the
file `Lists.scala`. There are two methods in this file that need to be
implemented (`sum` and `max`).

When working on an assignment, **it is important that you don't change any
existing method**, class or object names or types. Doing so will prevent our
automated grading tools from working and you have a high risk of not obtaining
any points for your solution. 

To learn how to use the Scala IDE, we recommend you to watch the official
tutorial video which is available here:
[http://scala-ide.org/docs/current-user-doc/gettingstarted/index.html](http://scala-ide.org/docs/current-user-doc/gettingstarted/index.html). 
This website also contains a lot more useful information and handy tricks that
make working with eclipse more efficient. 

### 3.4. Running Tests inside Eclipse
You can easily execute the test suites directly inside eclipse. Simply navigate
to source file of the test suite in `src/test/scala`, right-click on it and select
"Run As" - "JUnit Test". 

The JUnit window will display the result of each individual test.


-------------------

## Part 4: Running your Code
Once you start writing some code, you might want to run your code on a few
examples to see if it works correctly. We present two possibilities to run the
methods you implemented. 

### 4.1. Using the Scala REPL

In the sbt console, start the Scala REPL by typing `console`.

    > console
    [info] Starting scala interpreter...

    scala>

The classes of the assignment are available inside the REPL, so you can for
instance import all the methods from object Lists: 

    scala> import example.Lists._
    import example.Lists._

    scala> max(List(1,3,2))
    res1: Int = 3

### 4.2. Using a Main Object

Another way to run your code is to create a new Main object that can be executed
by the Java Virtual Machine. 

1. In eclipse, right-click on the package `example` in `src/main/scala` and select "New" - "Scala Object"
2. Use `Main` as the object name (any other name would also work)
3. Confirm by clicking "Finish"

In order to make the object executable it has to extend the type `App`. Change the
object definition to the following: 

    object Main extends App {
      println(Lists.max(List(1,3,2)))
    }

Now the `Main` object can be executed. In order to do so in eclipse:

1. Right-click on the file `Main.scala`
2. Select "Run As" - "Scala Application"

You can also run the `Main` object in the sbt console by simply using the command `run`.

------------------------

## Part 5: Writing Tests

Throughout the assignments of this course we will require you to write unit
tests for the code that you write. Unit tests are the preferred way to test your
code because unlike REPL commands, unit tests are saved and can be re-executed
as often as required. This is a great way to make sure that nothing breaks when
you have go back later to change some code that you wrote earlier on. 

We will be using the ScalaTest testing framework to write our unit tests. In
eclipse, navigate to the folder `src/test/scala` and open the file
`ListsSuite.scala` in package `example`. This file contains a step-by-step tutorial
to learn how to write and execute ScalaTest unit tests.

<!-- Here is [a copy of the ListSuite.scala file](./code/scala/ListSuite.scala). -->
    
------------------------------

## Part 6: Submitting your Solution

The only way to submit your solution is through sbt.

### 6.1. Generate a new password
In order to submit, you need to have your coursera username and your submission
password. Note that the submission password is a special password you must generate
using a button on the [assignments page](https://class.coursera.org/reactive-002/assignment/index). 

### 6.2. Start sbt
**Important:** Open a terminal, change to your project directory, and start the
  sbt console.  That is, you must start sbt from within your project directory. 

### 6.3. Issue the command for submitting in sbt:

    > submit your.email@domain.com submissionPassword
    [info] Connecting to coursera. Obtaining challenge...
    [info] Computing challenge response...
    [info] Submitting solution...
    [success] Your code was successfully submitted: Your submission has been accepted and will be graded shortly.
    [success] Total time: 2 s, completed Aug 30, 2012 4:30:10 PM
    > 

You are allowed to **resubmit a maximum of 5 times**! Once you submit your solution,
you should see your grade and a feedback about your code on the Coursera website
within 10 minutes. If you want to improve your grade, just submit an improved
solution. The best of all your submissions will count as the final grade. 


