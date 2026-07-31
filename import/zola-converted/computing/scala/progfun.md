---
title: Progfun Course Notes
date: '2014-03-13'
---

These are *very rough* personal notes from a Coursera course I took in 2014 called
[Functional Programming Principles in Scala](https://www.coursera.org/course/progfun).)
by Martin Odersky.

The link to the version of the course that I took is
[https://class.coursera.org/progfun-004](https://class.coursera.org/progfun-004).

General information about the course and possible future sessions is here: 
[https://www.coursera.org/course/progfun](https://www.coursera.org/course/progfun).

In 2015 I took a follow up course called
[Principles of Reactive Programming](https://www.coursera.org/course/reactive)
by Martin Odersky, Erik Meijer, Roland Kuhn. My notes from that course are
[here]({{ root_url }}/scala/reactive).

--------------------------------

## Setup

### Tools Setup for Linux
See [this page](https://class.coursera.org/progfun-003/wiki/ToolsSetup)

1. Install sbt by following the instructions at
[https://www.scala-sbt.org/download.html](https://www.scala-sbt.org/download.html)

(I have upgraded to version 0.13.1, which was the latest as of March 2014.)

2. Unpack the archive to a directory of your choice.

        tar xvzf sbt.tgz

3. Add the `bin/` directory to the `PATH` environment variable:

        echo "export PATH=/PATH/TO/YOUR/sbt/bin:$PATH" >> ~/.bash_profile
        source ~/.bash_profile

in an editor (create it if it doesn't exist) and add the following line export 
Verify that sbt is installed correctly: Open a new terminal (to apply the
changed .bashrc) and type sbt -h, you should see a help message from sbt. If you
have problems installing sbt, ask for help on the forums. 


------------------------------------------

## Week 1

### Lecture 1.1 - Programming Paradigms
The key point of this lecture is

*If we want to implement high-level concepts following their mathematical
theories, there's no place for mutation.*

Avoid mutations; get new ways to abstract and compose functions.

Outside resource Cited:  
[YouTube: O'Reilly OSCON Java 2011: "Working Hard to Keep It Simple"](http://youtu.be/3jg1AheF4n0)

+ non-determinism results from parallel processing plus mutable state.  
+ Functional programming (with immutable variables) makes concurrency much easier
to deal with.

### Lecture 1.2 - Elements of Programming

**Main Ideas**

+ Model of evaluation: the substitution model.  
+ Definitions: the keyword `def`  
+ Function parameters come with their types.  
+ evaluate function arguments from left to right.  
+ The substituion model: all evaluation does is reduce an expression to a
value.  
+ This model can express every algorithm (Church; $\lambda$-calculus)  
+ This can be applied to all expressions as long as there are *no side effects.*
  e.g., you can't represent `x++` using substituion evaluation.  
+ Does every expression reduce to a value in a finite number of steps? No.
  Example: `def loop: Int = loop`  

### Lecture 1.3 - Evaluation Strategies and Termination

+ Two forms of substitution evaluation strategies: *call-by-value* and
  *call-by-name*. Both strategies reduce to the same final values assuming the
  evaluation terminates.  If a call-by-value evaltion terminates, then so does
  call by name, but not conversely.  
+ *Scala is usually call-by-value*  (but if the type of a function parameter
  starts with =>, Scala uses call-by-name). The reason Scala uses call-by-value
  is because it often has exponentially better performance, since you only need
  to evaluate a given argument once, whereas call-by-name performs a new
  evaluation of this same argument for each appearance of the argument inside
  the function.  Also, it's usually easier to know exactly when an expression
  will be evaluated under call-by-value.
+ You can force Scala to use call-by-name as follows: 

```scala  
        def constOne(x: Int, y: => Int) = 1
```

  Here, the line `constOne(1+2, loop)` would terminate because the second
  argument is call-by-name, whereas `constOne(loop,1+2)` would not terminate
  because the first argument is call-by-value.


### Lecture 1.4 - Conditionals and Value Definitions
+ **Boolean expressions**  
  Constants: true false  
  Negation: !b  
  Conunction: b && b  
  Disjunction: b || b  
  Comparison operations: e <= e, e >= e, e < e, e > e, e == e, e != e   
+ **Rewrite Rules**  
  Note that  
  `true && e` evaluates to `e`, `false && e` evaluates to `false`,   
  `true || e` evaluates to `true`, `false || e` evaluates to `e`,  
  so, we could rewrite `if (b) e1 else e2` as `b && e1 || e2`.  
+ **def versus val**  
  Definitions that use `def` are *by-name*; the right-hand-side is evaluated on *each use*.  
  Definitions that use `val` are *by-value*; the right-hand-side is evaluated
  immediately and only once. For example,

```scala  
        val x = 2
		val y = square(x)
```

  Since the right-hand side of a `val` is evaluated at the point of definition,
  `y` has the value 4, not the value `square(x)`.
  
  Example:
  
```scala  
        def loop: Boolean = loop
```

  This defines loop as a function that is supposed to return a Boolean, 
  but simply calls itself. Now, `def x = loop` sets x equal to the loop function, 
  which is no problem, but `val x = loop` crashes because it attempts to evaluate 
  immediately and gets caught in the infinite recursive call.  In the REPL:
  
```scala  
    scala> def loop: Boolean = loop
    loop: Boolean

    scala> def x = loop
    x: Boolean

    scala> val x = loop
```

+ **Exercise** Write `and` and `or` function without using `&&` and `||`.

```scala  
      def and(x: Boolean, y: Boolean) = if(x) y else false
      def or(x: Boolean, y: Boolean) = if(x) true else y
```	  
  Now suppose the second argument of `and` is nonterminating, say, 
      
```scala  
	  and(false, loop)
```	  
  Even though `and` should short circuit because of the false first argument, 
  this doesn't work because the second argument is call-by-value.  We can fix 
  this by modifying the argument to be call-by-name as follows:
  
```scala  
      def and(x: Boolean, y: => Boolean) = if(x) y else false
```

  
### Lecture 1.5 - Example: square roots with Newton's method

First Scala program in Eclipse!

+ Scala needs an explicit return type for recursive functions.  
+ `Ctrl-Shift-f` nicely formats (indents) all code in the current buffer

(easy stuff)

### Lecture 1.6 - Blocks and Lexical Scope
(easy stuff)

### Lecture 1.7 - Tail Recursion

+ **Evaluating a function application**
  Rewriting rule:
  
```scala  
        def f(x1, ..., xn) = B; ... f(v1, ..., vn)
```

  could be written 
  
```scala  
        def f(x1, ..., xn) = B; ... [v1/x1, ..., vn/xn]B
```

  Here, the notation `[v1/x1, ..., vn/xn]B` means 
  "v1 for x1, ..., vn for xn in B", that is, 
  substitute the value vi for xi in the function body B.
  
+ **Tail Recursion**  
  If a function simply calls itself as its last action, the function's
  stack frame can be reused.  This is called *tail recursion*.

  A tail recursive function can execute in constant stack space, so

  *tail recursive functions are iterative processes.*
  
  A tail recursive function is the functional programmer's loop---it excutes
  just as efficiently as a loop in an imperative program.
  
  More generally, if the last action of a function consists of calling
  a single function (which may be the same function), one stack frame
  would be sufficient for both functions. Such calls are called *tail-calls.*
  
  Here is a non-example (i.e., a recursive function that is not tail recursive):
  
```scala  
        def factorial( n: Int ): Int = 
			if (n==0) 1 else n * factorial( n-1 )
```			
  Notice that after the recursive call to factorial, there is still work to be done.
  
  We will rewrite factorial in a tail-recursive way.  However, we pause to ask:
  
  Should every recursive function be reformulated to be tail recursive?
  
  No.  Tail recursion is used to avoid very deep recursive chains.  Most JVM implementations 
  limit the maximal depth of recursion to a couple of thousands of stack frames.
    
  The factorial function is not succeptible to this because the values computed 
  by factorial grow so quickly that they exceed the range of integers before 
  stack overflow. In such cases, use the simpler function definitions and heed Knuth:
  
  "Premature optimization is the root of all evil." --Donald Knuth
  
  To define a tail recursive version of factorial, we use an accumulator:
  
```scala  
        def factorial( n: Int , acc: Int ): Int = 
	        if ( n == 0 ) acc else factorial( n-1, acc*n )
```  

------------------------------------------

## Week 2

### Lecture 2.1 - Higher-Order Functions
We could sum the integers between a and b (inclusive) as follows:

```scala  
    def sumInts(a: Int, b: Int): Int =
  	    if (a > b) 0 else a + sumInts(a+1, b)
```

Then sum the squares of integers between a and b (inclusive):

```scala  
    def sumSquares(a: Int, b: Int): Int =
  	    if (a > b) 0 else a*a + sumSquares(a+1, b)
```

Sum the cubes or sum the factorials, etc.  But this can be done more 
generally and elegantly if we simply pass the functions---e.g., square, 
cube, factorial---as arguments:
  
```scala  
    def sumFunc(f: Int => Int, a: Int, b: Int): Int =
  	    if (a > b) 0 else f(a) + sumFunc(f, a+1, b)
```

Then `sumSquares` could be implemented as
  
```scala  
    def sumSquares(a: Int, b: Int): Int = sumFunc(square, a, b)
	def square(a: Int): Int = a * a
```

But even that's not great because then we end up defining all these
little auxiliary functions.  Since functions are first class objects, we 
use anonymous functions as "function literals" just as we use string literals
as follows:

```scala  
    println("abc")
```

Instead of the also correct, but more tedious,

```scala  
    def str = "abc"
	println(str)
```

The syntax for anonymous functions in Scala is as follows:

```scala  
    (x: Int) => x * x
	(x: Int, y: Int) => x + y
```

Every anonymous function can be expressed using def instead. That is,

```scala  
    (x1: T1, ..., xn: Tn) => E
```

can be implemented as follows:

```scala  
    def f(x1: T1, ..., xn: Tn) => E; f
```

But sometimes we need brackets so the name f doesn't get confused with another function:

```scala  
    {def f(x1: T1, ..., xn: Tn) => E; f}
```

So, returning to the example above, we could have defined sumSquares as:

```scala  
    def sumSquares(a: Int, b: Int): Int = sumFunc((x: Int) => x*x, a, b)
```

or, more simply,

```scala  
    def sumSquares(a: Int, b: Int): Int = sumFunc(x => x*x, a, b)
```

The sum function above uses linear recursion.  We can write a tail recursive version.
(Here the tail recursion is actually useful, unlike in the factorial case.)

```scala  
    def sum(f: Int => Int, a: Int, b: Int): Int = {
        def sumAux(a: Int, acc: Int): Int = {
            if (a > b) acc else sumAux(a+1, acc + f(a))
  		}
        sumAux(a, 0)
    }  

    sum(x => x*x, 0,3)   //> res4: Int = 14
```  

### Lecture 2.2 - Currying
Another version of the sum function could employ Currying.  
First, we could do this simply as follows:

```scala  
    def sum(f: Int => Int)(a: Int, b: Int): Int = {
        def sumAux(a: Int, acc: Int): Int = {
            if (a > b) acc else sumAux(a+1, acc + f(a))
  		}
        sumAux(a, 0)
    }  
```

Then, the expression 

```scala  
    sum(x => x*x)_
```
	
is valid.  It is a "partially applied" function.  

Alternatively, we could get rid of the a and b parameters:

```scala  
    def sum(f: Int => Int): (Int, Int) => Int = {
        def sumAux(a: Int, b: Int): Int = {
            if (a > b) 0 
			else f(a) + sumAux(a+1, b)
  		}
        sumAux
    }  
```

This gives us a function that returns, not an `Int`, but a function
of type `(Int, Int) => Int`.  So now we could define sumSquares as follows:

```scala  
	def sumSquares = sum(x => x*x)
	sumSquares(0, 3) //> res3: Int = 14
```	  

Or avoid the middle man and use the sum function directly, as in

```scala  
    sum(x=> x*x*x)(0, 3)  //> res3: Int = 36
```

This is the same as

```scala  
    (sum(x=> x*x*x))(0, 3)
```

So we see that function application associates to the left.

**Products**  
We can define a product function in a similar way.  We just need to abstract 
out the identity and the binary operation (instead of 0 we have 1, and instead of + we have *).

```scala  
    def product(f:Int => Int)(a: Int, b: Int): Int = {
        if (a>b) 1
        else f(a) * product(f)(a+1, b)
    }                                               //> product: (f: Int => Int)(a: Int, b: Int)Int
```

We can define factorial in terms of this product function.

```scala  
    def factorial(b: Int): Int = product(a=>a)(1,b) //> factorial: (b: Int)Int
    // Test it:
    factorial(3)                                    //> res0: Int = 6
```  

**MapReduce** We can simultaneously generalize sum and product.  Since we are 
providing a mapping (with f), and then reducing (with the binary op), we should call
the generalized version `mapReduce`.

```scala  
    def mapReduce(map: Int => Int, reduce: (Int, Int) => Int, unit: Int)(a: Int, b: Int): Int = {
  	    if(a > b) unit
        else reduce(map(a), mapReduce(map, reduce, unit)(a+1, b))
    }

    // Test it:
	mapReduce(x => x*x, (a, b) => a+b, 0)(0, 3)  //> res1: Int = 14
```

### Lecture 2.3 - Example: Finding Fixed Points 

### Lecture 2.4 - Scala Syntax Summary

### Lecture 2.5 - Functions and Data 
At about 3'30" of the video lecture, the (Java) package called week3 and a
new scala worksheet called rationals.sc are created.

### Lecture 2.6 - More Fun With Rationals

### Lecture 2.7 - Evaluation and Operators

-------------------------------------------------------

## Week 3: Data and Abstraction

### Lecture 3.1 - Class Hierarchies
abstract class -- may contain members that are not implemented.  You cannot
instantiate abstract classes.  You must implement them with a class that extends
the abstract class.

**Example:** IntSet (abstract), Empty extends IntSet, NonEmpty extends IntSet.
The classes that extend (implement) the abstract class implement all the
unimplemented members of the abstract class.  They can also implement members
that were already implmented in the abstract class, but then you need to use
*override.*

superclasses, subclasses.  Every class extends another class.  If no explicit
class is given, then the standard Java Object class is assumed.

The direct or indirect superclasses of a class are called the *base classes.*

Standalone applications.  Hello world program.  Create this in Eclipse not as a Scala
worksheet, but as a *Scala Object.*

The implementation of the union operation for IntSet is a really nice example of
functional object oriented programming.  The union is implemented recursively.
For the Empty object, union obviously returns the argument

```scala  
    def union(other: IntSet) = other
```

For the NonEmpty class, the union is implemented as follows:

```scala  
    class NonEmpty(elem: Int, left: IntSet, right: IntSet) extends IntSet {

        def union(other: IntSet): IntSet =
		    ((left union right) union other) incl elem

    }
```
How cool is *that*?!

How is this done in an object oriented language?  
Using the *dynamic method dispatch* model.  This means that the code invoked by a
method call depends on the runtime type of the object that contains the method.

Dynamic dispatch is analogous to calls to higher-order functions in a purely
functional language.

### Lecture 3.2 - How Classes Are Organized
Classes and objects are organized in packages.  Packages are imported with the
`import` statement.  Some entities are imported automatically in every Scala
program.  These are 

+ all members of package scala  
+ all members of package java.lang
+ all memebers of singleton object scala.Predef

You can explore the standard Scala library using the scaladoc web pages at

[www.scala-lang.org/api/current/index.html](https://www.scala-lang.org/api/current/index.html)

**Traits**
In Scala, like Java, a class can only have one super class.  That is, Scala
is a *single inheritance* language. But sometimes, we want a class to inherit
properties from several super entities.  To do this we use *traits*.  For example,

```scala  
    trait Planar {
		def height: Int
		def width: Int
		def surface = height * width
	}
```

Classes can inherit from at most one class but from arbitrarily many traits.
For example,

```scala  
    class Square extends Shape with Planar with Movable
```

Thus, Square has one superclass called Shape, but it also inherits traits Planar
and Movable.

**Main distinction** Traits do not have val members.

Special types in the hierarchy:  At the top, there is the `Any` class and its
subclasses, `AnyVal` and `AnyRef`.  At the bottom, there is the `Nothing` class
which is a subclass of `Null`.

Null is a subclass of all the types that are reference types.  If, for example, a String
is expected, then you can pass a null value.

```scala  
    val x = null
	val y: String = x
```

However, `val z: Int = null` doesn't work because Null is not a subclass of
subclasses of AnyVal.

Consider the line

```scala  
    if (true) 1 else false                    //> res1: AnyVal = 1
```

The result is of type AnyVal, because the type checker picks a type that
is the least upper bound of the types involved in the expression.  In
this example, we have 1 and false, which are Int and Boolean, resp.  The
"least" type that contains both is AnyVal.


**Errors**

To immediately halt execution of the program and output an error message:

```scala  
    def error(msg: String) = throw new Error(msg)
```

### Lecture 3.3 - Polymorphism

**Type parameterization** Running example: the immutable list

**Cons-List**

Nil -- the empty list  
Cons -- a cell containing the first element of the list and a pointer to the
rest of the list

In Eclipse, create a Scala Trait called `List`.  (at 5'55" of Lecture 3.3)

**Generics**

In Scala, you can put field definitions in parameter lists, instead of in the
body of the class.  For example, the following:

```scala  
    class Cons[T](val head: T, val tail: List[T]) extends List[T] {
	    def isEmpty = false
	}
```

is equivalent to

```scala  
    class Cons[T](_head: T, _tail: List[T]) extends List[T] {
	    def isEmpty = false
		val head = _head
		val tail = _tail
	}
```

**Type Erasure** Type parameters do not affect evaluation in Scala.  We can
  assume that ll type parameters and type arguments are removed before
  evaluating the program.  Scala shares this with Java, Haskell, ML and OCaml.





-------------------------------------------------------

## Week 4: Types and Pattern Matching

### Lecture 4.1 - Functions as Objects

### Lecture 4.3 - Subtyping and Generics
Two basic principles of polymorphism are subtyping and generics.

(See page 54 of Scala by Example, Odersky.)

If we have a function that takes any subtype of IntSet and returns something of
that same type, the interface could be something like this:

```scala  
    def assertAllPos(r: IntSet): IntSet = ...
```

But this isn't very precise.  Instead, we could specify that the return type is
the same as follows:

```scala  
    def assertAllPos[S <: IntSet](r: S): S = ... 
```

Here, "<: IntSet" is an upper bound on the type parameter S.  It means S can be
instantiated only to types that conform to IntSet.  I believe this means that
once we are passed the parameter r of a specific type S, then the return type
must also be of type S.  (It's not clear whether this allows return type
to be a subtype of type S.  We should check this.)

Generally, the notation

```scala  
    S <: T // means S is a subtype of T
	S >: T // means S is a supertype of T
```

With the >: operation we can be even more precise:

```scala  
    def assertAllPos[S >: NonEmpty <: IntSet](r: S): S = ...
```

would restrict S to be of a type between NonEmpty and IntSet.

Question: How do we specify that S must be of a specific type and not of a
subtype?  Perhaps as follows?

```scala  
    def assertAllPos[S >: IntSet <: IntSet](r: S): S = ...
```

**Important:** Arrays are not covariant in Scala, unlike in Java, *because they
  are mutable*.  (Lists in Scala are immutable, so they are covariant.) For example,
  in Java, one would have

```scala  
        NonEmpty[] <: IntSet[]
```

This causes problems and leads to runtime errors.  (See Lecture 4.4 on *variance*
for more details.)

**Liskov Substitution Principle**
If A <: B, and if q(x) is a property provable for objects x:B,
then q(y) should be provable for objects y:A.

### Lecture 4.2 - Objects Everywhere
*This is an important lecture.*

After explaining how to implement Boolean as a class instead of a primitive type
(see also page 37 of Scala by Example), Odersky explains how to implement the
type Nat (the Peano numbers) in Scala.


### Lecture 4.4 - Variance

### Lecture 4.5 - Decomposition

Suppose we want to write a small interpreter for arithmetic expressions.  Let's
restrict to just numbers and sums of numbers.  We will have an expression class
Expr with two subclasses, Number and Sum.  We could have, outside our Expr
class, an eval method that tests whether the input is a number or a sum and then
evaluates it.  First solution, use type tests and type casts.  This is low
level and potentailly unsafe.  Here's a better, object oriented solution:

```scala  
    trait Expr {
		def eval: Int
	}
		
	class Number(n: Int) extends Expr {
		def eval: Int = n
	}

	class Sum(e1: Expr, e2: Expr) extends Expr {
		def eval: Int = e1.eval + e2.eval
	}
```

But what if we decide later to have other subclasses?  Then we need
to implement an eval method for each. It is tedious to have to modify all the
subclasses of Expr.  Also, what if we now want a show method to print out the
string representation of Expr subclass objects.  Worse than that, what if we
want to simplify expressions?  A given expression might be a composition of sums
and products and it's not clear how to implement a simplify method.  The
solution is pattern matching, which we take up in the next lecture.

### Lecture 4.6 - Pattern Matching
(See page 43 of Scala by Example.)

Pattern matching allows us to find a general and convenient way to access
objects in an extensible class hierarchy.

The three solutions we have seen all have shortcomings.  They were:

+ Classification and access methods: quadratic explosion.
+ Type tests and casts: unsafe, low-level.
+ Object oriented decomposition: does not always work, need to touch all classes
  to implement a new method. (Doesn't work for non-local stuff.)

**Case Classes** the sole purpose of test and accessor functions is to reverse
  the construction process.  This is automated by pattern matching.

```scala  
    trait Expr
	case class Number(n: Int) extends Expr
	case class Sum(e1: Expr, e2: Expr) extends Expr
```

We get added functionality by adding case.  The compiler implicitly adds
companion objects:

```scala  
    object Number {
		def apply(n: Int) = new Number(n)
	}

	object Sum {
		def apply(e1: Expr, e2: Expr) = new Sum(e1, e2)
	}
```

We saw earlier that you can manually do this.  Put a `def apply` method in your
class and then you can instantiate the class without the new keyword, as in
`Number(2)` instead of `new Number(2)`.

Pattern matching is a generalization of switch from C or Java. It is expressed
in Scala using the keyword match.  For example,

```scala  
    def eval(e: Expr): Int = e match {
		case Number(n) => n
		case Sum(e1, e2) => eval(e1) + eval(e2)
	}
```

Patterns are constructed from:

+ constructors; e.g., Number, Sum
+ variables; e.g., n, e1, e2
+ wildcard patters _
+ constants; e.g. 1, true

Note: *variables always begin with a lowercase letter; constants begin
with a capital letter* (except for reserved words like null, true, false).

As an alternative to the above implementation of eval, we could make eval a
member method of the Expr trait:

```scala  
    trait Expr {
		def eval: Int = this match {
			case Number(n) => n
			case Sum(e1, e2) => e1.eval + e2.eval
		}
	}
```


-------------------------------------------------------

## Week 5: Lists

### Lecture 5.1 - More Functions on Lists

### Lecture 5.2 - Pairs and Tuples

### Lecture 5.3 - Implicit Parameters

### Lecture 5.4 - Higher-Order List Functions

### Lecture 5.5 - Reduction of Lists

**Fold and reduce combinators**
(_*_) stands for ((x,y) => x*y)


### Lecture 5.6 - Reasoning About Concat

### Lecture 5.7 - A Larger Equational Proof on Lists

-------------------------------------------------------

## Week 6: Collections

### Lecture 6.1 - Other Collections

**Vector**

This lecture has some crucial tips on when to use `List` and when to use
`Vector`.  `Vector` has more evenly balanced access patterns than `List`.  So,
why would you ever want to use `List.`  The `List` type is most useful in
recursive algorithms where you are repeatedly acting on the head (a constant
time access), and then passing the tail to the recursion.  With `Vector`,
accessing the leading element might require going down a few levels in the (albeit shallow)
tree, and splitting off the "tail" of a vector is not as clean as with a list.

```scala  
    val nums = Vector(1, 2, 3, -88)
	val people = Vector("Bob", "Jim")
```

This type supports the same operations as `List` except concat ::.  Instead of
`x :: xs`, there is `x +: xs` and 'xs :+ x`.

A common base class of `List` and `Vector` is `Seq`, which (along with `Set`
and `Map` types) is a subclass of `Iterable`. `Array` and `String` are
also sequence like classes.  The usual operations on sequences like `map` and
`filter` and `take while` and `fold` can be applied to all of these types.

### Lecture 6.2 - Combinatorial Search and For-Expressions

### Lecture 6.3 - Combinatorial Search Example

### Lecture 6.4 - Queries with For

### Lecture 6.5 - Translation of For

### Lecture 6.6 - Maps

### Lecture 6.7 - Putting the Pieces Together

-------------------------------------------------------

## Week 7: Lazy Evaluation

### Lecture 7.1 - Structural Induction on Trees

### Lecture 7.2 - Streams

### Lecture 7.3 - Lazy Evaluation

### Lecture 7.4 - Computing with Infinite Sequences

### Lecture 7.5 - Case Study: the Water Pouring Problem

### Lecture 7.6 - Course Conclusion

