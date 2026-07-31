+++
title = "Linear Algebra in Sage: Lab 2"
date = 2019-02-01
+++

## Part 1 Summary

To complete this part, you must login to your account on the Math Department Sage server and demonstrate that you know how to input a matrix, augment a matrix with a vector, and compute the echelon form of an (augmented) matrix.

Completing Part 1 is worth 1 point. If you are not interested in completing Part 2 of the assignment, you may turn in your paper and leave the lab after completing Part 1.

**Make sure your name is on your paper and it was signed by the instructor.**

## Part 2 Summary 

To complete Part 2, you must first download the Sage worksheet file Math317-Lab2.sws from either Blackboard or GitHub, load this worksheet into your Sage session and follow the    instructions provided. You must then save your completed Sage worksheet to a file and upload the resulting sws file to Blackboard.

## Finishing

When you have finished working or it is 2pm (whichever comes first):

1. **stop your Sage worksheet** (Action $\rightarrow$ Save and quit worksheet; or use Stop button),

2. **sign out of Sage**,

3. **logout of your computer**,

4. **write your name on your paper**,

5. **hand it in to the instructor**.

---

## Part 1 Details

In Homework 3, we proved that the vector ${{\mathbf{b}}}= (1, -1, 1, -1)$ is as a linear combination of the vectors ${{\mathbf{v}}}_1 = (1 , 0 , 1 , -2)$, ${{\mathbf{v}}}_2 = (0 , -1 , 0 , 1)$, and
${{\mathbf{v}}}_3 = (1, -2 , 1 , 0)$. 

Do you remember how we did this? 

That's right! We recognized that if the matrix $A$ has first column ${{\mathbf{v}}}_1$, second column ${{\mathbf{v}}}_2$, and third column ${{\mathbf{v}}}_3$, then writing ${{\mathbf{b}}}$ as a linear combination of the given vectors is the same as solving the system $A{{\mathbf{x}}}= {{\mathbf{b}}}$. That is, if we find
${{\mathbf{x}}}= (x_1, x_2, x_3)$ that solves this system, then ${{\mathbf{b}}}= x_1{{\mathbf{v}}}_1+x_2{{\mathbf{v}}}_2+x_3{{\mathbf{v}}}_3$ is the desired linear combination.

In this first part of this lab assignment, we will simply re-solve the above problem, but this time we will make Sage do the tedious work. Carry out the following steps:

1. Login to any machine in Carver 449, open up a browser (preferably Chrome) and navigate to [https://sage.math.iastate.edu/](https://sage.math.iastate.edu/)

   Login to your account on the Math Department Sage server using the login information you were given for Lab 1. Once you are logged in, create a new worksheet and name it Lab2.

2. In the Lab2 worksheet, click the first cell and type the following:

   ```python
   b = vector([1, -1, 1, -1]); print b
   ```

   Then type `Shift`+`Enter` or click `evaluate`. 

   Did Sage print what you expect? If so, move on to number 3. 

   If not, try again and/or ask the instructor for help.

3. Click somewhere inside the next cell and enter the following expression:

   ```python
    A = matrix(4, 3, [1, 0, 1, 0, -1, -2, 1, 0, 1, -2, 1, 0]) print A
    ```

    What did Sage print? 

    Is it a matrix with three columns, $\mathbf{v}_1$, $\mathbf{v}_2$, $\mathbf{v}_3$?  If not, try again and/or your neighbor for help. 

    Can you decipher the syntax we used to input this matrix $A \in \mathbb{R}^{4\times 3}$? If so, move on to number 4.

    If not, think a litter harder and/or discuss it with your neighbor.

4. Next, have Sage augment the matrix $A$ with the vector $b$ by entering the following into the next worksheet cell:

   ```python
   Ab = A.augment(b, subdivide=True) print Ab
   ```

5. Ask Sage to put your augmented matrix in reduced-row echelon form:

   ```python
   Ab.rref()
   ```

   You should now see two pivots (both equal to 1). Let the free variable $x_3 = s$ and write the vector $\mathbf{b}$ as a linear combination of the vectors $\mathbf{v}_1$, $\mathbf{v}_2$, $\mathbf{v}_3$ involving $s$.

   $$\mathbf{b}= \begin{bmatrix} 1 \\\\ -1 \\\\ 1 \\\\ -1\end{bmatrix}= \underline{\phantom{XXX}}\mathbf{v}_1 + \underline{\phantom{XXX}} \mathbf{v}_2+ \underline{\phantom{XXX}} \mathbf{v}_3.$$ 
   
   If you want to stop here, ask the instructor to check your work and sign below then save and quit. Otherwise, move on to Part 2\
   \
   \
   Instructor signature: (1 point)


## Part 2 Details

Load the [Math317-Lab2.sws](/sage/lab2/Math317-Lab2.sws) file into your Sage session and complete the exercises.