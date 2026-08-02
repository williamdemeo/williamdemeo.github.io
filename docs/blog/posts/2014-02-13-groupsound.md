---
title: GroupSound
slug: groupsound
date: 2014-02-13
categories:
  - Mathematics
tags:
  - harmonic analysis
  - finite groups
  - signal processing
description: >-
  What does a nonabelian group sound like?  Using a finite group as an adjustable parameter of a digital audio filter.
---
*What does a nonabelian group sound like?*

[The GroupSound project](http://soundmath.github.io/GroupSound/) is
about harmonic analysis on finite groups. Classical dsp filtering algorithms can
be implemented as operations involving functions (e.g., audio signals) defined
on a finite group. That is, the group serves as the domain, or "index set," of
the functions.  In this project, we explore the idea of using the finite group 
as an adjustable parameter of a digital audio filter. 
<!-- more -->

--8<-- "dated.md"

Underlying many digital signal processing (dsp) algorithms, in particular those
used for digital audio filters, is the convolution operation, which is a
weighted sum of translations $f(x-y)$. Most classical results of dsp are easily
and elegantly derived if we define our functions on $\mathbb{Z}/n\mathbb{Z}$, the
abelian group of integers modulo n. If we replace this underlying "index set"
with a nonabelian group, then translation may be written $f(y^{-1}x)$, and the
resulting audio filters arising from convolution naturally produce different
effects than those obtained with ordinary (abelian group) convolution. 

By listening to samples produced using various nonabelian groups, we try to get
a sense of the "acoustical characters" of finite groups.  

Please visit
[the GroupSound project webpage](http://soundmath.github.io/GroupSound/) for
more details. 
