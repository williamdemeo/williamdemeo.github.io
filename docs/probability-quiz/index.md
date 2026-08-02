---
title: Jane Street Test
date: '2014-03-19'
---

--8<-- "archived.md"

<!-- ---
layout: post
title: "Jane Street Test"
date: 2014-03-19 20:27:46 -0400
comments: true
published: true
categories: [Probability, Interview Questions, Finance]
--- -->

The questions below appeared on an online test administered by 
Jane Street Capital Management to assess whether a person is worthy of 
a phone interview.

<!-- more -->

### Question 1
Suppose we choose four numbers at random without replacement from the first
20 prime numbers. What is the probability that the sum of these four numbers is odd?

**Solution** By definition, an *even* number is an integer multiple of 2; that
is, even numbers have the form $2n$, for some integer $n$. An *odd* number is
one more than an even number; that is, odd numbers have the form $2n+1$ for
some integer $n$. 
  
If all four numbers are odd, then the sum is even.  This follows
from the fact that the sum of two odd numbers is even: $(2n+1) + (2k+1) =
2(n+k) + 2 = 2(n+k+1)$.  And the sum of two even numbers is again even: $2n+2k =
2(n+k)$.  Therefore, in order for the sum of the four primes chosen to
be odd, the only even prime number, 2, must be among the four numbers we
selected.

Here are two ways to compute the probability that 2 is one of the four numbers selected:
First, consider the probability of *not* selecting 2:
$$
P(\text{2 is not among the chosen primes}) = 
\frac{19}{20}
\frac{18}{19}
\frac{17}{18}
\frac{16}{17}
=
\frac{16}{20}
=
\frac{4}{5}.
$$

Then the probability that 2 is among the four chosen prime numbers is 
$1 - \frac{4}{5}$, or $\frac{1}{5}$.

Alternatively, we could count the number of four-tuples that have a 2.  This is
the same as taking 4 times the number of ways to choose the other three numbers: 
$19\cdot 18\cdot 17$. (The factor of 4 appears since we could put the 2 in any of four
positions).  Now divide this by the total number of four-tuples, 
$20 \cdot 19\cdot 18\cdot 17$, to arrive at the same answer as above:

$$
\frac{4\cdot 19\cdot 18\cdot 17}
{20 \cdot 19\cdot 18\cdot 17} = 
\frac{4}{20} = \frac{1}{5}.
$$  


### Question 2
Suppose you have an 8 sided die with sides labeled 1 to 8.  You roll the die
once and observe the number $f$ showing on the first roll.  Then you have the
option of rolling a second time.  If you decline the option to roll again, you win
$f$ dollars. If instead you exercise the option to roll a second time, 
and if $s$ shows on the second roll, then you win $f + s$ dollars if $f+s < 10$ 
and 0 dollars if $f+s \geq 10$.  What is the best strategy?

**Solution** 

A strategy is given by specifying what to do in response to 
each possible first roll, $f$. The best strategy will maximize the expected winnings.
  
The expected winnings if we roll just once is simply the number that appears, $f$.

Let $S$ be the random variable representing the value showing on the second
roll. This is uniformly distributed with $P(S=s) = 1/8$.
Therefore, if we observe $f$ and then decide to roll twice, the expected
winnings are

$$
  E(W | f, \mathrm{roll\ twice}) = \sum_{s=1}^8 (f+s)\chi_{\{f+s < 10\}} P(S=s)
  = \frac{1}{8}\sum_{s=1}^8 (f+s)\chi_{\{f+s < 10\}}
$$

where $\chi$ denotes the characteristic function, that is,
$\chi\_{\mathrm{True}}=1$ and $\chi\_{\mathrm{False}}=0$.

If we let $N= \min\{8, 10 - f -1\}$, then the expected value of rolling twice is

$$
E(W | f, \mathrm{roll\ twice}) = \frac{1}{8}\sum_{s=1}^{N} (f+s)
$$

If we observe $f=1$ on the first roll, then 

$$
E(W | f=1, \mathrm{roll\ twice})  = \frac{1}{8} \sum_{s=1}^8 (1+s)= \frac{11}{2}.
$$

Since this is greater than 1, we should certainly exercise the option to roll
twice if 1 shows up on the first roll.

Continuing this way, we have

$$
E(W | f=2, \mathrm{roll\ twice}) =  \frac{1}{8}\sum_{s=1}^{7} (2+s)
=  \frac{1}{8}(2\cdot7 + 1 + 2+ 3+ \cdots + 7)
= 6.
$$

$$
E(W | f=3, \mathrm{roll\ twice}) =\frac{1}{8}\sum_{s=1}^{6} (3+s)
= \frac{1}{8}(3\cdot 6 +1 + 2+ 3+ \cdots + 6)
= \frac{39}{8}.
$$

$$
E(W | f=4, \mathrm{roll\ twice}) = \frac{1}{8}\sum_{s=1}^{5} (4+s)
= \frac{1}{8}(4\cdot 5+1 + 2+ 3+ \cdots + 5)
= \frac{35}{8}.
$$

Since this is larger than 4, we should roll twice when observing 4 on the first roll.

However, if $f = 5$, then 

$$
E(W | f=5, \mathrm{roll\ twice}) = \frac{1}{8}\sum_{s=1}^{4} (5+s)
= \frac{1}{8}((5)(4)+1 + 2+ 3+ \cdots + 4)
= \frac{30}{8}.
$$

Since this is *less* than 5, we should *not* roll a second time when a 5 is observed
on the first roll.

**General strategy:** Exercise the option to roll a second time if the first
results in 1, 2, 3, or 4.  Otherwise, decline the second roll and take the value
shown on the first roll. 


------------------------------------------------------------------

### Question 3

(The original question was for 3 coins, with respective probabilities 0.5, 0.3, and
0.2 of coming up heads.  This version is a generalization to $n$ coins with
arbitrary probabilities that sum to 1.)

Suppose you have a bag with $n$ coins, $C\_1, C\_2, \dots, C\_n$,  and coin
$C\_i$ has probability $p\_i$ of coming up heads when flipped.  Assume 
$p\_1 + p\_2 + \cdots p\_n = 1$.  Suppose you draw a coin from the bag at random
and flip it and it comes up heads.  If you flip
the same coin it again, what is the probability it comes up heads?

Denote by $H\_i$ the event that heads turns up on the $i$-th flip, and by a
slight abuse of notation, let $C\_i$ denote the event that we are flipping coin $C_i$.
Then 

$$
P(H_2 | H_1) = \sum_{i=1}^n P(H_2| C_i, H_1) P(C_i|H_1)
= \sum_{i=1}^n p_i P(C_i|H_1)
$$

Applying Bayes' Theorem,

$$
P(C_i|H_1) = \frac{P(C_i,H_1)}{P(H_1)} = 
\frac{P(H_1|C_i) P(C_i)}{P(H_1)}.
$$

Assuming all coins are equally likely to have been drawn from the bag,
$P(C_i)=\frac{1}{n}$. Therefore,

$$
P(H_1) = \sum_{i=1}^n P(H_1| C_i) P(C_i) = \frac{1}{n}\sum_{i=1}^n p_i =
\frac{1}{n},
$$

whence,

$$
P(C_i|H_1) = \frac{P(H_1|C_i) P(C_i)}{P(H_1)} = p_i \frac{1/n}{1/n} = p_i.
$$

Therefore,

$$
P(H_2 | H_1) = \sum_{i=1}^n p_i^2.
$$

For the special case given in the original problem, we have

$$
P(H_2 | H_1) = (0.5)^2 + (0.3)^2 + (0.2)^2 = 0.25 + 0.09 + 0.04 = 0.38.
$$



------------------------------------------------------------------

### Question 4

Suppose you have two urns that are indistinguishable from the outside.
One of the urns contains 3 one-dollar coins and 7 ten-dollar coins.
The other urn contains 5 one-dollar coins and 5 ten-dollar coins.
Suppose you choose an urn at random and draw a coin from it at random.  
You find that it is a $10 coin.  Now you are given the option to draw 
again (without replacing the first coin) from either the same urn or 
the other urn.  Should you draw from the same urn or switch?

**Solution**

The problem is uninteresting if we assume the draws are made with replacement.
Clearly we should not switch urns in this case.  Assume the second draw is made
without replacing the first coin.

Let $X$ be a random variable denoting the value of the second draw.  We
compute the expected values $E(X | \text{ stay})$ and $E(X | \text{ switch})$
and whichever is higher determines our strategy.

Let us call the urn that starts with 7 ten-dollar coins urn $A$,
and the urn that starts with 5 ten-dollar coins urn $B$.
Let $A\_1$ denote the event that urn $A$ is chosen for the first draw and let
$B\_1$ denote the event that urn $B$ is chosen for the first draw.
Let $T$ denote the event that the first draw produces a ten-dollar coin.  

The probability that a ten-dollar coin appears on the first draw is

$$
P(T) = P(T| A_1) P(A_1)+ P(T| B_1) P(B_1) = \frac{7}{10}\frac{1}{2} +\frac{5}{10}\frac{1}{2} = \frac{3}{5}.
$$

Given that $T$ occurred, the probability we were drawing from $A$ is, by Bayes' Theorem,

$$
P(A_1 | T) = \frac{P(T|A_1) P(A_1)}{P(T)} = \frac{(7/10)(1/2)}{3/5} = \frac{7}{12}.
$$

Similarly the probability we were drawing from $B$, given $T$, is

$$
P(B_1 | T) = \frac{P(T|B_1) P(B_1)}{P(T)} = \frac{(5/10)(1/2)}{3/5} = \frac{5}{12}.
$$

Now, if we decide to draw again from the same urn and that urn happens to be
$A$, there will be 6 ten-dollar coins remaining, so our expected value of
drawing again from $A$ is

$$
E(X | A_1, \text{ same}) = 10\cdot \frac{6}{9} + 1 \cdot \frac{3}{9} =
\frac{21}{3} = 7.
$$

If we decide to draw from the same urn and it happens to be $B$,
there will be 4 ten-dollar coins remaining, so 

$$
E(X | B_1, \text{ same}) = 10\cdot \frac{4}{9} + 1 \cdot \frac{5}{9} =
\frac{45}{9} = 5.
$$

So, if we don't switch urns, the expected value of the second draw is

$$
E(X | \text{ same}) 
= E(X | A_1, \text{ same}) P(A_1)
+ E(X | B_1, \text{ same}) P(B_1) = \frac{7\cdot 7}{12} +
\frac{5 \cdot 5}{12} =  6.16.
$$

Suppose instead we decided to switch urns. In the event $A_1$ that the
first draw was from urn $A$, then urn $B$ will contain its original contents:
5 ten-dollar coins and 5 one-dollar coins. Therefore,

$$
E(X | A_1, \text{ switch}) = 10\cdot \frac{5}{10} + 1 \cdot \frac{5}{10} = 6.5.
$$

If we switch in the event $B_1$, then we choose from a
pristine urn $A$ having 7 ten-dollar coins and 3 one-dollar coins. Thus,

$$
E(X | B_1, \text{ switch}) = 10\cdot \frac{7}{10} + 1 \cdot \frac{3}{10} =
7.3.
$$

Therefore,

$$
E(X | \text{ switch}) 
= E(X | A\_1, \text{ switch}) P(A\_1)+ E(X | B\_1, \text{ switch}) P(B\_1) = 6.5 \frac{7}{12} + 7.3 \frac{5}{12}.
$$

So, the expected value of the second draw if we switch urns is a little more
than 6.83.


**Conclusion:** The best strategy is to switch urns before drawing the second coin.


