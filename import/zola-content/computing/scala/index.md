+++
template = "pagenofoot.html"
title = "Scala for algebra research"
date = 2020-09-27
+++

## Contents

- [Setting up](#setting-up)
- [Scala REPL with UACalc objects](#scala-repl-with-uacalc-objects)
- [The LUAU Library](#the-luau-library)
- [Constructing general algebras with Scala](#constructing-general-algebras-with-scala)
- [EXAMPLE: a unary operation defined from a (Scala) function.](#example-a-unary-operation-defined-from-a-scala-function)
- [Computing Congruences for Quantumn Physicists](#computing-congruences-for-quantumn-physicists)
- [More Learning Resources](#more-learning-resources)
- [Contributions Welcome](#contributions-welcome)


-----------------------------------------------

## Setting up

[Scala](http://www.scala-lang.org/) is a (non-pure) functional language that supports object oriented programming. It runs on the [Java virtual machine (jvm)](https://en.wikipedia.org/wiki/Java_virtual_machine), and because of this it is possible to import UACalc Java packages into Scala programs (just [like we do in Jython](../../pl/uacalc/command-line-examples/).

1. **Install [Java][]** if you don't already have it.  
   Ubuntu users can follow [these instructions](https://williamdemeo.gitlab.io/pl/uacalc/#install-java) for installing (even multiple versions of) Java.

2. **[Download and Install Scala](http://www.scala-lang.org/download/)** following the instructions given on [the download page](http://www.scala-lang.org/download/).  

   **Ubuntu** users can download the file [scala-2.13.3.tgz](https://downloads.lightbend.com/scala/2.13.3/scala-2.13.3.tgz), unpack it and put a link to the `scala-2.13.3/bin` directory in your `PATH`, OR put a symbolic link to the `scala-2.13.3/bin/scala` file your `$HOME/bin` directory (assuming the latter is in your path). For example, I did the following:

   ```shell
   cd ~/opt/SCALA             # (where I downloaded scala-2.13.3.tgz)
   tar xvzf scala-2.13.3.tgz
   ln $HOME/opt/SCALA/scala-2.13.3/bin/scala $HOME/bin/scala
   source ~/.bash_profile
   ```

3. **Download the [uacalc.jar](http://uacalc.org/lib/uacalc.jar) file** from [uacalc.org/lib/uacalc.jar](http://uacalc.org/lib/uacalc.jar)  
   
-------------------------------------------------

## Scala REPL with UACalc objects

4. **Start the Scala REPL** with UACalc dependencies.  
   In a terminal window, change to the directory containing the jar files you downloaded above and do
   ```shell
   scala -classpath uacalc.jar
   ```
   You should see something like the following

   ```shell
   Welcome to Scala 2.13.3 (Java HotSpot(TM) 64-Bit Server VM, Java 15).
   Type in expressions for evaluation. Or try :help.

   scala> 
   ```

5. Import UACalc classes and make some objects.

   ```scala
   scala> import org.uacalc.alg.conlat.BasicPartition

   scala> val a = new BasicPartition("|0,1|2,3|")
   a: org.uacalc.alg.conlat.BasicPartition = |0,1|2,3|

   scala> val b = new BasicPartition("|0|1,2|3|")
   b: org.uacalc.alg.conlat.BasicPartition = |0|1,2|3|

   scala> a.compose(b)
   blocks: [[0,1],[2,3]]
   val res1: org.uacalc.alg.conlat.BinaryRelation = 
     [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], 
     [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]
   ```

---------------------------------------------

## The LUAU Library

This section gives an example use of the [Lazy Universe Algebra Utilities][] (aka [Lūʻau][]) Scala library.

[ScalaLūʻau][] is a Scala library providing some tools that facilitate computational algebra research and, in particular, importing and using Java packages from the [Universal Algebra Calculator][] in Scala programs. 

### Constructing general algebras with Scala

We first describe how to construct an algebra that we can compute with.

The file [UACalcAlgebraFactory.scala][] in the [basic_algebra][] package of [ScalaLūʻau][] makes it easy to build operation tables from Scala functions, lists, or arrays.

Some examples are given in the Scala worksheet called [AlgebraFactory.sc][], which is well documented with comments and self-explanatory. Nonetheless, we describe the first of those examples here.

### EXAMPLE: a unary operation defined from a (Scala) function.

In this example, we define a typical function in Scala, then we use that function to construct some UACalc operations and, finally, we construct a UACalc `BasicAlgebra` with these operations.

The required imports for this example are

```scala
import org.uacalc.alg.BasicAlgebra
import basic_algebra.UACalcAlgebraFactory._
import scala.jdk.javaapi.CollectionConverters.asJava
```

First, we define a Scala function by specifying what the function does at each point.

```scala
val plusMod5: List[Int] => Int = l.sum % 5
```

It should be clear that this function takes a list of Ints and outputs their sum modulo 5. The type signature of this function, `List[Int] => Int`, is optional in this context since it can be inferred by the Scala type checker; nonetheless, we make the types explicit for clarity.
   
Next we use the `plusMod5` function to construct a couple of UACalc operations using the method `UACalcOpFromFun` (defined in the [basic_algebra][] package).

```scala
val op1: UACalcOperation = UACalcOpFromFun(plusMod5, "binaryMod5", 2, 5)
val op2: UACalcOperation = UACalcOpFromFun(plusMod5, "ternaryMod5", 3, 5)
```

In order to use these operations as input to UACalc's `BasicAlgebra` constructor, we need to put them into a Java list.

```scala
val my_ops = asJava(List(op1, op2))
```

Finally, we are ready to build our algebra using the `BasicAlgebra` constructor (imported above).

```scala
val myAlg: BasicAlgebra = new BasicAlgebra("My 1st Alg", 5, my_ops)
```

We can now apply any of the UACalc methods available for BasicAlgebra instances, e.g., 

```scala
myAlg.getName()
myAlg.universe()
myAlg.con().getUniverseList
```

These method calls produce the following output:

```scala
res10: String = My 1st Alg
res11: java.util.Set[_] = [0, 1, 2, 3, 4]
res12: java.util.List[org.uacalc.alg.conlat.Partition] = [|0|1|2|3|4|, |0,1,2,3,4|]
```
revealing that the algebra we constructed is called "My 1st Alg", has universe {0, 1, ..., 4}, and is simple.

Finally, we can write the algebra to a UACalc .ua (xml) file by invoking

```scala
AlgebraIO.writeAlgebraFile(myAlg, "~/UACalcAlgebraFromScalaFunctions.ua")
```
The resulting file could then be opened in the [UACalc][] GUI.

---------------------------------------------

## Computing Congruences for Quantumn Physicists

Here are some highlights from the file [TumaExample.scala][], which we used to find congruences of cellular automata for quantum physics.  This was for joint work with Jiri Tu̇ma.

First we created a class called Tuma and defined (in the file [Tuma.scala][]) as follows.

```scala
package basic_algebra
import algebra_util._
class Tuma (n: Int, m: Int) {
  private val N = Math.pow(2, m).toInt
  def cardinality: Int = N

  /** Process state
    * @param inputstate
    * @param t a String representing an Int in base 2
    * @param iters an Int number of iterations
    */
  def processState(inputstate: String, t: String, iters: Int): String = {
    @scala.annotation.tailrec
    def proc_state_aux(state: String, indx: Int): String = {
      if (indx == 0) state else {
        def newstate(k: Int): Int =
          strAt(t,Integer.parseInt(strAt(state,k-1)+strAt(state, k)+strAt(state,k+1),2)).toInt
        val newstatestr: String = fun2str(newstate, 1 until (state.length-1))
        proc_state_aux(newstatestr, indx - 1)
      }
    }
    proc_state_aux(inputstate, iters)
  }

  def state_list(x: Int, y: Int, z: Int): String =
    int2bin((N * (N * x + y)) + z, 3 * m)

  val t : String = int2bin(n, 8).reverse

  def op: (Int, Int, Int) => Int = (x, y, z) =>
    Integer.parseInt(processState(state_list(x, y, z), t, m), 2)
}
```

Next we construct an instance of the Tuma class for parameters `n = 110` and `m = 7`.

```scala
val n = 110; val m = 7
val tuma = new Tuma(n, m)
val N = tuma.cardinality
def t_def(args: List[Int]): Int = tuma.op(args(0), args(1), args(2))
```

Notice that in the last line above we converted the type of `tuma.op` from `Int × Int × Int => Int` to `List[Int] => Int`.  This is so we can pass the resulting function, `t_def`, into `UACalcOpFromFun` and construct UACalc operation.

```scala
val t_op: UACalcOperation = UACalcOpFromFun(t_def, "t", 3, N)

// make a singleton Java list containing the operation
val t_uacalc_op = asJava(List(t_op))

// construct the basic algebra
val t_Alg: BasicAlgebra = new BasicAlgebra("Jiri's Alg" + "(" + n + "," + m + ")", N, t_uacalc_op)
```

Next we write the algebraic structure to a UACalc algebra file so we can inspect the algebra in the UACalc GUI if desired.

```scala
val A = AlgebraIO.writeAlgebraFile(t_Alg, algebra_dir + "/Tuma-" + n + "-" + m + ".ua")
```

Most of the congruences of the algebra will have the same block structure and will be "obvious" or uninteresting.  These tend to have small blocks and, after some experimentation, we realized that they are generated by values in the following list.

```scala
val smblocks = List(10,18,20,21,34,36,37,40,41,42,43,74,82,84,85,106)
```

Finally, for each `a` and `b` *not* in the `smblocks` list, we compute and print out the congruence generated by `(a, b)` as follows.

```scala
for (a <- (0 until N-1).filterNot(smblocks.contains))
  for (b <- (a+1 until N).filterNot(smblocks.contains)) {

    val cab = t_Alg.con().Cg(a,b, null)

    if (cab.numberOfBlocks() > 17)
      println("Cg(" + a + "," + b + ") = " + cab + "  NUM BLOCKS = " + cab.numberOfBlocks())
```

(The `if` conditional limits the printed output to only interesting congruences.)

------------------------------------------------------------

## More Learning Resources

### The Best Scala Books

+ [FP in Scala](https://www.amazon.com/gp/product/1617290653/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1617290653&linkCode=as2&tag=typefunc-20&linkId=54a91efb12cb54dd18310361c5899551) and 
[its companion](https://www.amazon.com/gp/product/1508537569/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1508537569&linkCode=as2&tag=typefunc-20&linkId=ef3d7aa7fb5a06ed92f1b9e2e0747f0b)
+ [The Type Astronaut's Guide to Shapeless](https://www.amazon.com/gp/product/1365613526/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1365613526&linkCode=as2&tag=typefunc-20&linkId=05b0464ef74f4cef93004dd8cd4ea838)
+ [Scala with Cats](https://scalawithcats.com/)

<a target="_blank"  href="https://www.amazon.com/gp/product/1617290653/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1617290653&linkCode=as2&tag=typefunc-20&linkId=54a91efb12cb54dd18310361c5899551"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=1617290653&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL110_&tag=typefunc-20"></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=typefunc-20&l=am2&o=1&a=1617290653" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;"/><!-- Compation to FP in Scala --> <a target="_blank"  href="https://www.amazon.com/gp/product/1508537569/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1508537569&linkCode=as2&tag=typefunc-20&linkId=ef3d7aa7fb5a06ed92f1b9e2e0747f0b"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=1508537569&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL110_&tag=typefunc-20"></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=typefunc-20&l=am2&o=1&a=1508537569" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;"/><!-- Shapeless --> <a target="_blank"  href="https://www.amazon.com/gp/product/1365613526/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1365613526&linkCode=as2&tag=typefunc-20&linkId=05b0464ef74f4cef93004dd8cd4ea838"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=1365613526&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL110_&tag=typefunc-20"></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=typefunc-20&l=am2&o=1&a=1365613526" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" /> [<img src="https://underscore.io/images/books/scala-with-cats.png" width="75"/>](https://scalawithcats.com/)

(Please support this site by using the links above to order the books.)

--------------------------------------

### The Best Scala Courses

[Martin Odersky](http://en.wikipedia.org/wiki/Martin_Odersky), creator of Scala, (along with some colleagues) offers an excellent sequence of online courses on the [Coursera platform](https://www.coursera.org).  They are listed below.

  1. [Functional Programming Principles in Scala](https://www.coursera.org/learn/progfun1/home)
  2. [Functional Program Design in Scala](https://www.coursera.org/learn/progfun2/home)
  3. [Parallel Programming in Scala](https://www.coursera.org/learn/parprog1)
  4. [Big Data Analysis with Scala and Spark](https://www.coursera.org/learn/scala-spark-big-data/home/welcome)

<!-- The pages [progfun](./pl/scala/progfun.md) and [reactive](./pl/scala/reactive.md) collect some of my own notes about -->
<!-- these courses, and are intended merely for my own future reference. -->

<!-- [Verified Certificate](https://www.coursera.org/account/accomplishments/records/CKWD8PLCPW4E) earned 17 Nov 2016 (grade: 100%) -->
<!-- [Verified Certificate](https://www.coursera.org/account/accomplishments/records/2WE2UZSR5AAZ) earned 6 Aug 2016 (grade: 100%) -->
<!--    [Verified Certificate](https://www.coursera.org/account/accomplishments/records/3XV34H6BTTHC) earned 27 Jun 2016 (grade: 100%) -->
<!--    [Verified Certificate](https://www.coursera.org/account/accomplishments/records/93DVEX3QH86L) earned 24 Nov 2017 (grade: 93.4%) -->

----------------------

## Contributions Welcome

This page was created by volunteers. Help grow it into a more useful resource. If you have any comments, suggestions, or other contributions, please [create a new gitlab issue](https://gitlab.com/scalaspark/lazy-universal-algebra-utilities/-/issues/new) or [email williamdemeo at gmail](mailto:williamdemeo@gmail.com).

------------------------------------

[AlgebraFactory.sc]: https://gitlab.com/scalaspark/lazy-universal-algebra-utilities/-/blob/master/src/test/scala/AlgebraFactory.sc
[basic_algebra]: https://gitlab.com/scalaspark/lazy-universal-algebra/-/blob/master/src/main/scala/basic_algebra
[UACalcAlgebraFactory.scala]: https://gitlab.com/scalaspark/lazy-universal-algebra/-/blob/master/src/main/scala/basic_algebra/UACalcAlgebraFactory.scala
[Universal Algebra Calculator]: http://uacalc.org
[UACalc]: http://uacalc.org
[lazy universe algebra utilities]: https://gitlab.com/scalaspark/lazy-universal-algebra
[Lazy Universe Algebra Utilities]: https://gitlab.com/scalaspark/lazy-universal-algebra
[ScalaLūʻau]: https://gitlab.com/scalaspark/lazy-universal-algebra
[Lūʻau]: https://gitlab.com/scalaspark/lazy-universal-algebra
[LUAU]: https://gitlab.com/scalaspark/lazy-universal-algebra
[SCALALUAU]: https://gitlab.com/scalaspark/lazy-universal-algebra
[TumaExample.scala]: https://gitlab.com/scalaspark/lazy-universal-algebra-utilities/-/blob/master/src/test/scala/TumaExample.scala
[Tuma.scala]: https://gitlab.com/scalaspark/lazy-universal-algebra-utilities/-/blob/master/src/main/scala/basic_algebra/Tuma.scala
[Java]: https://www.oracle.com/java/technologies/javase-downloads.html
[scala-with-cats]: https://underscore.io/images/books/scala-with-cats.png "Scala with Cats"
