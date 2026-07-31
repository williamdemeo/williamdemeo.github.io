+++
template = "page.html"
title = "Coq"
date = 2014-06-06
author = "William DeMeo"
+++

## Background

This page collects some basic information about Coq, and is mainly intended for
my research students interested in learning how to use Coq.

+ **What is Coq?**
  Coq is a proof assistant and a functional programming language.

+ **What is a proof assistant?**
  A proof assistant is a tool that automates the more routine aspects of building
  proofs while depending on human guidance for more difficult aspects.
  Coq is one such tool. It provides a rich environment for interactive
  development of machine-checked formal reasoning.  

+ **How to get started?**
  There are a number of ways to get started with Coq. Here I'll first give
  an overview of my experience, and then, further on down the page, I'll provide
  some more details.

  I got started with Coq by watching
  [Andrej Bauer's series of YouTube tutorials](http://www.youtube.com/watch?v=COe0VTNF2EA&list=PLDD40A96C2ED54E99&feature=share).
  These videos give some nice introductory lessons which show exactly how one
  interacts with Coq. For example, in the video
  [How to use Coq with Proof General](http://youtu.be/l6zqLJQCnzo), Andrej shows how to use Coq to prove
  that *Pierce's Law* is equivalent to the *Law of Excluded Middle*.  

  (Proof General is one way to interact with Coq, which is the great for
  those accustomed to the Emacs editor. For those who aren't into Emacs,
  an alternative interface to Coq exists, called CoqIDE, about which I know
  absolutely nothing. I installed Coq and Proof General on Ubuntu 14.04 very
  easily using the Synaptic package manager; no custom configuration required.)

+ **How to continue?**
  Again, more details about how to really get going with Coq and how to use it
  for theorem proving and functional programming, but if you want to stop
  reading here, then I highly recommend reading (and solving the
  exercises in) the first 5 or 6 chapters of the book,
  [Software Foundations][].

  (At the time of this writing, the link above points to the url
  [https://softwarefoundations.cis.upenn.edu/lf-current/toc.html](https://softwarefoundations.cis.upenn.edu/lf-current/toc.html). However, the url of the Software Foundations book occasionally changes.  If the link is broken, you can find the book by simply googling "Software Foundations Pierce".)
  

  The [Software Foundations][]
  book is an outstanding resource.  Not only is it well written and
  accessible, even to non-computer scientists, but also it's fun to read because
  of the many engaging exercises sprinkled throughout the book that test your
  understanding of the material.

  With some prior programming experience---and especially with some functional
  programming experience---you can probably proceed quickly through SF and learn
  a lot about Coq by solving most, if not all, of the exercises. I would guess
  that an intelligent undergraduate, with a little background in elementary 
  logic, math, and programming, could get through a few chapters of SF per week.

## Getting Started with Proof General

This section collects some notes on basic commands used to interact with Coq
using [Proof General].  We will begin with Andrej Bauer's YouTube tutorials,
and then move on to the Basics section of the book
[Software Foundations][].

### Quickstart
To get started using Coq with Proof General, I recommend
[the YouTube tutorial by Andrej Bauer](http://youtu.be/l6zqLJQCnzo).

<iframe width="640" height="360" src="//www.youtube.com/embed/l6zqLJQCnzo"
frameborder="0" allowfullscreen></iframe>

Andrej has a
[collection of nice tutorials](https://www.youtube.com/watch?v=COe0VTNF2EA&list=PLDD40A96C2ED54E99&feature=share);
the video embedded above concerns Proof General.

I will not reiterate everything that Andrej covers in his tutorials.
Rather, the main point here is to describe, and record for my own
reference, a few emacs commands that are most useful when using Proof General
with Coq (since this isn't covered in the Software Foundations book).

Let's assume Coq and Proof General have been installed in Ubuntu, using, e.g.,

    sudo apt-get install proofgeneral coq

Startup emacs with a new file called `pierce_lem.v`:

    emacs pierce_lem.v

You should see the Proof General welcome screen for a few seconds, then an
emacs buffer containing the (empty) contents of the new `pierce_lem.v` file.

Add the following line to the `pierce_lem.v` file by typing it in the buffer window:

    Definition pierce := forall (p q : Prop), ((p -> q) -> p) -> p.

Then enter the emacs control sequence: `C-c C-n` (that is, hold down the control
key while typing `c`, then hold down control while typing `n`).

If you see a new emacs buffer window labeled \*goals\* containing the text "pierce is
defined" and if the Definition appears in color, then Coq has accepted the new
definition.

Now, on the next line, type the definition of the law of excluded middle:

    Definition lem := forall (p : Prop), p \/ ~p.

and type `C-c C-n`, and then the theorem we want to prove:

    Theorem pierce_equiv_lem : pierce <-> lem.

After entering `C-c C-n` at the end of this line, Coq shows the goals and subgoals
that we need to establish in order to prove the theorem.

(Andrej mentions that by default Proof General complains if you try to edit
lines that have already been accepted by Coq.  It seems this is no longer the
case---you can freely edit any line, and it will revert to unchecked status.
However, if your installation complains when you try to edit lines that have
already been accepted, you can manually uncheck them using the command `C-c C-u`.)

Comments may be added between starred parens, like this:

    (* this is a comment *)

In Andrej's Proof General YouTube tutorial, he only mentions a couple of Proof
General commands, such as:

+ `C-c C-n` proof-assert-next-command-interactive  
+ `C-c C-u` proof-undo-last-successful-command  
+ `C-c C-p` show goals

Some other useful commands are

+ `C-c C-RET` proof-goto-point  
+ `C-c C-b` proof-process-buffer  
+ `C-c C-r` proof-retract-buffer

The first of these evaluates the proof script up to the point (where cursor is
located), the second processes the whole buffer, and the third retracts the
whole buffer (i.e., clears all definitions).

These and other commands are mentioned in [Section 2.6](http://proofgeneral.inf.ed.ac.uk/htmlshow.php?title=Proof+General+user+manual+%28latest+release%29&file=releases%2FProofGeneral-latest%2Fdoc%2FProofGeneral%2FProofGeneral_3.html#Script-processing-commands) of the Proof General documentation.

Here is the link to [the main Proof General documentation page](http://proofgeneral.inf.ed.ac.uk/htmlshow.php?title=Proof+General+user+manual+%28latest+release%29&file=releases%2FProofGeneral-latest%2Fdoc%2FProofGeneral%2FProofGeneral.html#Top)
and [the section on Coq](http://proofgeneral.inf.ed.ac.uk/htmlshow.php?title=Proof+General+user+manual+%28latest+release%29&file=releases%2FProofGeneral-latest%2Fdoc%2FProofGeneral%2FProofGeneral_12.html#Coq-Proof-General).

After following along with Andrej's first tutorial on Proof General, I recommend
proceeding with the fourth in his series:

<iframe width="640" height="360" src="//www.youtube.com/embed/z861PoZPGqk?list=PLDD40A96C2ED54E99" frameborder="0" allowfullscreen></iframe>

## Software Foundations Book

Download and extract the
[lf.tgz file](https://softwarefoundations.cis.upenn.edu/lf-current/lf.tgz) for
the Software Foundations (volume 1) book as follows.

	mkdir -p ~/git; mkdir ~/git/Coq; cd ~/git/Coq
    wget https://softwarefoundations.cis.upenn.edu/lf-current/lf.tgz
	tar xvzf lf.tgz
	rm lf.tgz

**Remarks**

1. You may of course choose a directory other than ~/git/Coq, but the commands shown
below assume we are working in the ~/git/Coq directory.

2. If you use Git, you may wish to create a new repository with the Software
  Foundation book's files, so you can modify them as you work through them
  without worrying if you break them.  Do this as follows:

        git init
		git add lf/*
		git commit -m "initial commit of sf book files"

### Basics
To be continued...


[Software Foundations]: https://softwarefoundations.cis.upenn.edu/lf-current/toc.html
