// Generated from cv.yml by scripts/python/gen_cv.py.
// Do not edit: `make cv` regenerates it.  See ADR-003, ADR-010.
//
// Data only.  cv/template.typ is the layout, and is written by hand.
//
// `built` is the date this file was generated, and is what the footer
// prints.  It is here rather than taken from the clock at compile time so
// that the PDF is a function of files in the repository: `gen_cv.py
// --check --pdf` recompiles with this date and compares the bytes, which
// it could not do against a date that changed on every build.

#import "template.typ": cv-document, render-sections
#import "publications.typ": publications

#let built = datetime(year: 2026, month: 8, day: 4)

#show: cv-document.with(
  name: "William DeMeo",
  title: "Curriculum Vitae",
  email: "williamdemeo@gmail.com",
  url: "https://williamdemeo.org",
  built: built,
)

#let sections = (
  (
    title: "Research interests",
    kind: "prose",
    entries: (
      (
        body: (
          (("Interactive theorem proving and formalization of mathematics (Agda, Lean); formal methods for production systems; AI tooling for proof assistants and machine reasoning over verifiable domains; universal algebra, lattice theory, and the algebraic approach to computational complexity.", none, none),),
        ),
      ),
      (
        body: (
          (("Theory", "strong", none), (". Universal algebra, logic, lattice theory, proof theory, category theory, type theory, complexity theory, algorithmic complexity, machine learning.", none, none)),
        ),
      ),
      (
        body: (
          (("Practice", "strong", none), (". Proof mechanization in Agda and Lean, computer-aided mathematics, formal verification, functional programming for AI, ML and Big Data in Scala/Spark.", none, none)),
        ),
      ),
    ),
  ),
  (
    title: "Education",
    kind: "timeline",
    entries: (
      (
        term: "2012",
        head: (("Doctor of Philosophy in Mathematics", "strong", none), (" — ", none, none), ("University of Hawaii", none, "https://math.hawaii.edu/wordpress/"), (", Honolulu", none, none)),
        body: (
          (("Thesis: ", none, none), ("Congruence lattices of finite algebras", none, "https://arxiv.org/abs/1204.4305"), (".", none, none)),
          (("Advisor: ", none, none), ("Ralph Freese", none, "http://math.hawaii.edu/~ralph/"), (".", none, none)),
        ),
      ),
      (
        term: "–",
        head: (("Master of Science in Mathematics", "strong", none), (" — ", none, none), ("Courant Institute of Mathematical Sciences, NYU", none, "https://cims.nyu.edu/"), (", New York", none, none)),
        body: (
          (("Thesis: ", none, none), ("Approximating eigenvalues of large stochastic matrices", none, "https://williamdemeo.github.io/MSThesis/"), (".", none, none)),
          (("Advisor: ", none, none), ("Jonathan Goodman", none, "https://www.math.nyu.edu/faculty/goodman/index.html"), (".", none, none)),
        ),
      ),
      (
        term: "–",
        head: (("Bachelor of Arts in Economics", "strong", none), (" — ", none, none), ("University of Virginia", none, "https://www.virginia.edu/"), (", Charlottesville", none, none)),
      ),
    ),
  ),
  (
    title: "Appointments",
    kind: "timeline",
    entries: (
      (
        term: "2023–",
        head: (("Formal Verification Engineer", "strong", none), (", Formal Methods Team", none, none), (" — ", none, none), ("IO", none, "https://iohk.io/"), (", Boulder", none, none)),
        body: (
          (("Formal verification of the Cardano blockchain ledger specification in Agda.  2 years.", none, none),),
          (("Project", none, "https://github.com/IntersectMBO/formal-ledger-specifications"),),
        ),
      ),
      (
        term: "2022–2023",
        head: (("Senior University Lecturer", "strong", none), (", Computer Science Dept.", none, none), (" — ", none, none), ("New Jersey Inst. of Technology", none, "https://cs.njit.edu/"), (", Newark", none, none)),
        body: (
          (("Taught courses in foundations of computing, big data, and artificial intelligence.  18 months.", none, none),),
        ),
      ),
      (
        term: "2022–2023",
        head: (("Software Engineer", "strong", none), (", Library Team", none, none), (" — ", none, none), ("RelationalAI", none, "https://relational.ai/"), (", New York", none, none)),
        body: (
          (("Developed the Standard Library of the Rel declarative programming language.  9 months.", none, none),),
        ),
      ),
      (
        term: "2019–2021",
        head: (("Postdoctoral Research Fellow", "strong", none), (", Algebra Dept.", none, none), (" — ", none, none), ("Charles University", none, "https://ka.karlin.mff.cuni.cz/"), (", Prague", none, none)),
      ),
      (
        term: "2017–2019",
        head: (("Burnett Meyer Instructor", "strong", none), (", Mathematics Dept.", none, none), (" — ", none, none), ("University of Colorado", none, "https://www.colorado.edu/math/"), (", Boulder", none, none)),
      ),
      (
        term: "2016–2017",
        head: (("Visiting Assistant Professor", "strong", none), (", Mathematics Dept.", none, none), (" — ", none, none), ("University of Hawaii", none, "https://math.hawaii.edu/wordpress/"), (", Honolulu", none, none)),
      ),
      (
        term: "2014–2016",
        head: (("Postdoctoral Associate", "strong", none), (", Mathematics Dept.", none, none), (" — ", none, none), ("Iowa State University", none, "https://math.iastate.edu/"), (", Ames", none, none)),
      ),
      (
        term: "2012–2014",
        head: (("Visiting Assistant Professor", "strong", none), (", Mathematics Dept.", none, none), (" — ", none, none), ("Univ South Carolina", none, "https://sc.edu/study/colleges_schools/artsandsciences/mathematics/index.php"), (", Columbia", none, none)),
      ),
      (
        term: "2001–2006",
        head: (("Senior Research Scientist", "strong", none), (", Imaging Research Dept.", none, none), (" — ", none, none), ("Textron Systems Corp.", none, "https://www.textronsystems.com/"), (", Maui", none, none)),
        body: (
          (("Worked full-time on AFOSR contracts developing new algorithms and parallel (smp and mpi) programs for processing images acquired by the Haleakala Observatories, including Multi-frame Blind Deconvolution for removing the distorting effects of Earth's atmosphere from images of satellites and other NEOs; executed our programs on the MHPCC supercomputer.", none, none),),
          (("AFOSR", none, "https://www.afrl.af.mil/AFOSR/"), (" · ", none, none), ("Haleakala Observatories", none, "https://about.ifa.hawaii.edu/facility/haleakala-observatories/"), (" · ", none, none), ("MHPCC", none, "http://www.mhpcc.hpc.mil/")),
        ),
      ),
    ),
  ),
  (
    title: "Grants and awards",
    kind: "timeline",
    entries: (
      (
        term: "2015–2018",
        head: (("NSF Research Grant", "strong", none), (" no. 1500218", none, none)),
        body: (
          (("Algebras and algorithms, structure and complexity theory", "em", none), (".", none, none)),
          (("Postdoctoral research fellow on a team with 6 senior scientists and 3 postdocs.", none, none),),
          (("3-yr collaborative research on algebraic approaches to constraint satisfaction problems.", none, none),),
        ),
      ),
      (
        term: "2013–2014",
        head: (("Magellan Scholar Grant", "strong", none),),
        body: (
          (("What does a nonabelian group sound like?", "em", "http://soundmath.github.io/GroupSound/"), (".", none, none)),
          (("Faculty mentor for undergraduate research.", none, none),),
        ),
      ),
      (
        term: "2011",
        head: (("ARCS Sarah Ann Martin Award", "strong", none), (" for Outstanding Research in Mathematics", none, none), (", Honolulu", none, none)),
      ),
      (
        term: "2004",
        head: (("Best Paper Award", "strong", none), (", International Symposium on Musical Acoustics", none, none), (", Nara, Japan", none, none)),
      ),
    ),
  ),
  (
    title: "Selected publications",
    kind: "publications",
    publications: publications,
    note: (("The complete record, with abstracts, is on the ", none, none), ("publications page", none, "https://williamdemeo.org/publications/"), (".", none, none)),
    entries: (
    ),
  ),
  (
    title: "Projects",
    kind: "list",
    entries: (
      (
        head: (("Category Theory: a concise course", "strong", "https://categorytheory.gitlab.io"),),
        body: (
          (("With Charlotte Aten and Venanzio Capretta.", none, none),),
          (("Work in progress.", none, none),),
        ),
      ),
      (
        head: (("The Agda Universal Algebra Library", "strong", "https://ualib.org"),),
        body: (
          (("With Jacques Carette.", none, none),),
          (("Work in progress.", none, none),),
        ),
      ),
      (
        head: (("Complex Analysis Exams", "strong", "http://complexanalysis.gitlab.io"),),
        body: (
          (("Work in progress.", none, none),),
        ),
      ),
      (
        head: (("Real Analysis Exams", "strong", "http://realanalysis.gitlab.io"),),
        body: (
          (("Work in progress.", none, none),),
        ),
      ),
    ),
  ),
  (
    title: "Teaching",
    kind: "groups",
    entries: (
      (
        head: (("New Jersey Institute of Technology", "strong", none), (" — Senior University Lecturer", none, none)),
        items: (
          (
            head: (("DS 644", "strong", "https://github.com/williamdemeo/ds644-spring2023"), (" Introduction to Big Data", none, none), (" — graduate course, Spring 2023", none, none)),
          ),
          (
            head: (("CS 644", "strong", none), (" Introduction to Big Data", none, none), (" — graduate course, Fall 2022", none, none)),
          ),
          (
            head: (("CS 370", "strong", "https://github.com/williamdemeo/cs370-fall2022"), (" Introduction to Artificial Intelligence", none, none), (" — Fall 2022", none, none)),
          ),
          (
            head: (("CS 370", "strong", "https://github.com/williamdemeo/cs370-spring2022"), (" Introduction to Artificial Intelligence", none, none), (" — Spring 2022", none, none)),
          ),
          (
            head: (("CS 241", "strong", "https://github.com/williamdemeo/cs241-spring2022"), (" Foundations of Computer Science I", none, none), (" — Spring 2022", none, none)),
          ),
        ),
      ),
      (
        head: (("Charles University in Prague", "strong", none), (" — Postdoctoral Research Fellow", none, none)),
        items: (
          (
            head: (("NMAG 405", "strong", "https://gitlab.com/universalalgebra/charlesuniversity/nmag405"), (" Universal Algebra", none, none), (" — Winter 2020", none, none)),
          ),
        ),
      ),
      (
        head: (("University of Colorado, Boulder", "strong", none), (" — Burnett Meyer Instructor", none, none)),
        items: (
          (
            head: (("Math 2001", "strong", "https://github.com/williamdemeo/math2001-spring2019"), (" Discrete Mathematics", none, none), (" — with Lean prover component, Spring 2019", none, none)),
          ),
          (
            head: (("Math 2001", "strong", none), (" Discrete Mathematics", none, none), (" — with Lean prover component, Fall 2018", none, none)),
          ),
          (
            head: (("Math 3140", "strong", "https://github.com/williamdemeo/math3140-fall2018"), (" Abstract Algebra", none, none), (" — Fall 2018", none, none)),
          ),
          (
            head: (("Math 6000", "strong", "https://github.com/williamdemeo/math6000-spring2018"), (" Model Theory", none, none), (" — graduate course, Spring 2018", none, none)),
          ),
          (
            head: (("Math 2130", "strong", "https://github.com/williamdemeo/math2130-spring2018"), (" Linear Algebra", none, none), (" — Spring 2018", none, none)),
          ),
          (
            head: (("Math 2130", "strong", none), (" Linear Algebra", none, none), (" — Fall 2017", none, none)),
          ),
        ),
      ),
      (
        head: (("University of Hawaii", "strong", none), (" — Visiting Assistant Professor", none, none)),
        items: (
          (
            head: (("Math 215", "strong", none), (" Applied Calculus", none, none), (" — Spring 2017", none, none)),
          ),
          (
            head: (("Math 480", "strong", none), (" Senior Seminar", none, none), (" — Spring 2017", none, none)),
          ),
          (
            head: (("Math 244", "strong", "https://github.com/williamdemeo/math244-fall2016"), (" Calculus IV", none, none), (" — Fall 2016", none, none)),
          ),
          (
            head: (("Math 321", "strong", "https://github.com/williamdemeo/math321-fall2016"), (" Introduction to Advanced Math", none, none), (" — Fall 2016", none, none)),
          ),
        ),
      ),
      (
        head: (("Iowa State University", "strong", none), (" — Postdoctoral Associate", none, none)),
        items: (
          (
            head: (("Math 317", "strong", "https://github.com/williamdemeo/Math317-Spring2016"), (" Linear Algebra", none, none), (" — Spring 2016", none, none)),
          ),
          (
            head: (("Math 317", "strong", none), (" Linear Algebra", none, none), (" — Fall 2015", none, none)),
          ),
          (
            head: (("Math 160", "strong", "https://github.com/williamdemeo/Math160-Fall2015"), (" Survey of Calculus", none, none), (" — Fall 2015", none, none)),
          ),
          (
            head: (("Math 207", "strong", "https://github.com/williamdemeo/Math207-Spring2015"), (" Elementary Linear Algebra", none, none), (" — Spring 2015", none, none)),
          ),
          (
            head: (("Math 165", "strong", "https://github.com/williamdemeo/Math165-Spring2015"), (" Calculus I", none, none), (" — Spring 2015", none, none)),
          ),
          (
            head: (("Math 301", "strong", none), (" Abstract Algebra", none, none), (" — Fall 2014", none, none)),
          ),
          (
            head: (("Math 165", "strong", none), (" Calculus I", none, none), (" — Fall 2014", none, none)),
          ),
        ),
      ),
      (
        head: (("University of South Carolina", "strong", none), (" — Visiting Assistant Professor", none, none)),
        items: (
          (
            head: (("Math 700", "strong", "https://github.com/williamdemeo/Math700Spring2014"), (" Linear Algebra", none, none), (" — graduate course, Spring 2014", none, none)),
          ),
          (
            head: (("Math 141", "strong", "https://github.com/williamdemeo/Math141Spring2014"), (" Calculus I", none, none), (" — Spring 2014", none, none)),
          ),
          (
            head: (("Math 374", "strong", none), (" Discrete Structures", none, none), (" — Fall 2013", none, none)),
          ),
          (
            head: (("Math 122", "strong", none), (" Calculus for Business and Social Sciences", none, none), (" — Fall 2013", none, none)),
          ),
          (
            head: (("Math 374", "strong", none), (" Discrete Structures", none, none), (" — Spring 2013", none, none)),
          ),
          (
            head: (("Math 122", "strong", none), (" Calculus for Business and Social Sciences", none, none), (" — Spring 2013", none, none)),
          ),
          (
            head: (("Math 241", "strong", none), (" Vector Calculus", none, none), (" — Fall 2012", none, none)),
          ),
          (
            head: (("Math 122", "strong", none), (" Calculus for Business and Social Sciences", none, none), (" — Fall 2012", none, none)),
          ),
        ),
      ),
      (
        head: (("University of Hawaii", "strong", none), (" — Graduate Student Instructor", none, none)),
        items: (
          (
            head: (("Math 371", "strong", none), (" Probability Theory", none, none), (" — Summer 2011", none, none)),
          ),
          (
            head: (("Math 100", "strong", none), (" Mathematical Reasoning", none, none), (" — Summer 2010", none, none)),
          ),
          (
            head: (("Math 215", "strong", none), (" Applied Calculus I", none, none), (" — Summer 2009", none, none)),
          ),
        ),
      ),
    ),
  ),
  (
    title: "Talks",
    kind: "talks",
    entries: (
      (
        head: (("Birkhoff's Theorem in Dependent Type Theory", "strong", "https://types21.liacs.nl/timetable/event/proof-assistants-applications/"),),
        body: (
          (("TYPES 2021, Online, 2021", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/2101.10166"),),
        ),
      ),
      (
        head: (("Complexity of the Homomorphism Problem for Boolean Models", "strong", "https://csp-seminar.org/talks/william-demeo"),),
        body: (
          (("European virtual CSP seminar, Online, 2020", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/2010.04958"),),
        ),
      ),
      (
        head: (("Computational Tools for Universal Algebra Research", "strong", "https://williamdemeo.gitlab.io/talks/vols/"),),
        body: (
          (("CSP World Congress 2020, Vols am Schlern, Italy, 2020", none, none),),
        ),
      ),
      (
        head: (("Formalizing Universal Algebra with Dependent and Inductive Types", "strong", "https://williamdemeo.gitlab.io/agda-ualib/index.html"),),
        body: (
          (("AMS Joint Mathematics Meetings; Special Session: Algebras and Algorithms, Denver, CO, 2020", none, none),),
          (("Docs", none, "https://ualib.org"),),
        ),
      ),
      (
        head: (("Computing Difference Term Operations in Polynomial Time", "strong", none),),
        body: (
          (("BLAST Conference, University of Denver, Denver, CO, 2018", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/2011.07879"),),
        ),
      ),
      (
        head: (("Why Universal Algebra Needs Inductive, Dependent Types", "strong", none),),
        body: (
          (("Oregon Programming Languages Summer School, Eugene, OR, 2018", none, none),),
        ),
      ),
      (
        head: (("A Tutorial Introduction to the Lean Prover", "strong", none),),
        body: (
          (("University of Colorado Logic Seminar, Boulder, CO, 2018", none, none),),
        ),
      ),
      (
        head: (("The Lambda Calculus and Dependent Type Theory", "strong", none),),
        body: (
          (("University of Colorado Logic Seminar, Boulder, CO, 2018", none, none),),
        ),
      ),
      (
        head: (("Representing Finite Lattices as Congruence Lattices", "strong", none),),
        body: (
          (("Colorado State University Algebra Seminar, Fort Collins, CO, 2017", none, none),),
        ),
      ),
      (
        head: (("A Polynomial-time Test for Difference Terms in Idempotent Varieties", "strong", none),),
        body: (
          (("BLAST Conference, Vanderbilt University, Nashville, TN, 2017", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/2011.07879"),),
        ),
      ),
      (
        head: (("Algebraic approach to complexity of constraint satisfaction", "strong", "https://github.com/williamdemeo/Talks/blob/master/UH/LogicSeminar/UH-logic-seminar-2016.pdf"),),
        body: (
          (("University of Hawaii Logic and Analysis Seminar, Honolulu, HI, 2017", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/1611.02867"),),
        ),
      ),
      (
        head: (("Universal Algebraic Methods for Constraint Satisfaction Problems", "strong", none),),
        body: (
          (("AMS Fall Western Sectional Meeting: Special Session in Algebraic Logic, Denver, CO, 2016", none, none),),
          (("Preprint", none, "https://arxiv.org/abs/1611.02867"),),
        ),
      ),
      (
        head: (("The Rectangularity Theorem of Barto and Kozik", "strong", "https://github.com/williamdemeo/Talks/tree/master/Boulder/slides"),),
        body: (
          (("Algebras and Algorithms: Structure and Complexity Theory, Boulder, CO, 2016", none, none),),
        ),
      ),
      (
        head: (("Constraint Satisfaction Problems and Universal Algebra", "strong", "https://github.com/williamdemeo/Talks/tree/master/MGS/2016"),),
        body: (
          (("Midlands Graduate School in the Foundation of Computing Science, Birmingham, England, 2016", none, none),),
        ),
      ),
      (
        head: (("Permutability in Diamonds", "strong", "https://github.com/williamdemeo/Talks/tree/master/ISU/AlgComSem"),),
        body: (
          (("Iowa State Algebra and Combinatorics Seminar, Ames, IA, 2016", none, none),),
        ),
      ),
      (
        head: (("Which Commutative Idempotent Binars are Tractable?", "strong", "http://www.math.vanderbilt.edu/~moorm10/shanks/talks/demeo-slides.pdf"),),
        body: (
          (("Vanderbilt Shanks workshop: Open Problems in Universal Algebra, Nashville, TN, 2015", none, none),),
        ),
      ),
      (
        head: (("Some Small Finite Algebras Yielding Tractable CSP Templates", "strong", none),),
        body: (
          (("Iowa State Algebra and Combinatorics Seminar, Ames, IA, 2015", none, none),),
        ),
      ),
      (
        head: (("Algebraic CSP and Tractability of Commutative Idempotent Binars", "strong", "https://github.com/williamdemeo/Talks/tree/master/BLAST/BLAST2015"),),
        body: (
          (("BLAST Conference, University of North Texas, Denton, TX, 2015", none, none),),
        ),
      ),
      (
        head: (("Isotopic Algebras", "strong", none),),
        body: (
          (("Iowa State Algebra and Combinatorics Seminar, Ames, IA, 2015", none, none),),
        ),
      ),
      (
        head: (("What Does a Nonabelian Group Sound Like?", "strong", none),),
        body: (
          (("MAA Special Session: At the Intersection of Mathematics and the Arts, Baltimore, MD, 2014", none, none),),
          (("Abstract", none, "https://jointmathematicsmeetings.org/amsmtgs/2160_abstracts/1096-c5-2578.pdf"),),
        ),
      ),
      (
        head: (("Interval Enforceable Properties of Finite Groups", "strong", "https://github.com/williamdemeo/Talks/tree/master/AMS/Louisville2013"),),
        body: (
          (("AMS Special Session on Finite Universal Algebra, Louisville, KY, 2013", none, none),),
        ),
      ),
      (
        head: (("Tutorial: UACalc at the command line and in the cloud", "strong", none),),
        body: (
          (("Workshop on Computational Universal Algebra, Louisville, KY, 2013", none, none),),
        ),
      ),
      (
        head: (("Approximating Eigenvalues of Large Stochastic Matrices", "strong", none),),
        body: (
          (("University of South Carolina Combinatorics Seminar, Columbia, SC, 2013", none, none),),
        ),
      ),
      (
        head: (("Congruence Lattices of Finite Algebras", "strong", "https://github.com/williamdemeo/Talks/tree/master/BLAST/BLAST2013"),),
        body: (
          (("BLAST Conference, Chapman University, Orange, CA, 2013", none, none), (" · plenary lecture", none, none)),
        ),
      ),
      (
        head: (("Transposition Principles for Subgroups and Equivalence Relations", "strong", "https://github.com/williamdemeo/Talks/tree/master/Zassenhaus/WCU-2013"),),
        body: (
          (("Zassenhaus Group Theory Conference, Asheville, NC, 2013", none, none),),
        ),
      ),
      (
        head: (("Isotopic Algebras with Nonisomorphic Congruence Lattices", "strong", "https://github.com/williamdemeo/Talks/tree/master/AMS/Boulder2013"),),
        body: (
          (("AMS Special Session on Algebras, Lattices, and Varieties, Boulder, CO, 2013", none, none),),
        ),
      ),
      (
        head: (("Synchronizing Automata and the Cerny Conjecture", "strong", "https://williamdemeo.files.wordpress.com/2012/12/cugradalgebraseminar.pdf"),),
        body: (
          (("Graduate Algebra Seminar, University of Colorado, Boulder, CO, 2013", none, none),),
        ),
      ),
      (
        head: (("The Finite Lattice Representation Problem in Four Parts", "strong", none),),
        body: (
          (("University of South Carolina Algebra and Logic Seminar, Columbia, SC, 2012", none, none),),
        ),
      ),
      (
        head: (("Interval Sublattice Enforceable Properties of Finite Groups", "strong", "https://github.com/williamdemeo/Talks/tree/master/Zassenhaus/OSU-2012"),),
        body: (
          (("The 31st Ohio State-Denison Mathematics Conference, Columbus, OH, 2012", none, none),),
        ),
      ),
      (
        head: (("Expansions of Finite Algebras and their Congruence Lattices", "strong", "https://github.com/williamdemeo/Talks/tree/master/AMS/Honolulu2012"),),
        body: (
          (("American Mathematical Society sectional meeting, Honolulu, HI, 2012", none, none),),
        ),
      ),
      (
        head: (("Intervals in Subgroup Lattices and Permutation Representations", "strong", none),),
        body: (
          (("Western Carolina University Group Theory Seminar, Cullowhee, NC, 2012", none, none),),
        ),
      ),
      (
        head: (("Recent Progress on the Finite Lattice Representation Problem", "strong", none),),
        body: (
          (("Achievement Rewards for College Scientists: Scholar Presentations, Honolulu, HI, 2011", none, none),),
        ),
      ),
      (
        head: (("The Finite Lattice Representation Problem", "strong", none),),
        body: (
          (("First Joint Meeting of the Korean and American Mathematical Societies, Seoul, KOR, 2009", none, none),),
        ),
      ),
      (
        head: (("Object reconstruction from multiple views", "strong", none),),
        body: (
          (("Air Force Office of Scientific Research AMOS Program Review, Maui, 2004", none, none),),
        ),
      ),
      (
        head: (("Approximating eigenvalues of large stochastic matrices", "strong", none),),
        body: (
          (("8th Copper Mt. Conference on Iterative Methods, Colorado, 1998", none, none),),
        ),
      ),
    ),
  ),
  (
    title: "Service",
    kind: "list",
    entries: (
      (
        head: (("Organizer", "strong", none), (", ", none, none), ("BLAST 2019 Conference", none, "https://math.colorado.edu/blast/2019/index.html"), (", Boulder, 2019", none, none)),
      ),
      (
        head: (("Organizer", "strong", none), (", ", none, none), ("Algebras and Lattices in Hawaii Conference", none, "https://universalalgebra.github.io/ALH-2018/"), (", to honor Freese, Lampe & Nation", none, none), (", Honolulu, 2018", none, none)),
      ),
      (
        head: (("Organizer", "strong", none), (", ", none, none), ("Workshop on Computational Universal Algebra", none, "http://universalalgebra.wordpress.com/meetings/2013-workshop-on-computational-universal-algebra/"), (", Louisville, 2013", none, none)),
      ),
      (
        head: (("Editor", "strong", none), (", ", none, none), ("Algebra Universalis", none, none), (", 2018–", none, none)),
      ),
      (
        head: (("Referee", "strong", none), (", ", none, none), ("Algebra Universalis, Order, and J. Logic & Analysis", none, none), (", 2012–", none, none)),
      ),
      (
        head: (("Graduate Student Representative", "strong", none), (", ", none, none), ("Working Group on Graduate Education", none, none), (" — University of Hawaii", none, none)),
        body: (
          (("Graduate Student Representative on a committee of deans and department heads; helped draft a resolution for the Committee on Research and Graduate Education.", none, none),),
        ),
      ),
      (
        head: (("Faculty Senate Student Rep., Academic Committee Chair, Math Department Rep.", "strong", none), (", ", none, none), ("Graduate Student Organization", none, none), (" — University of Hawaii", none, none)),
      ),
      (
        head: (("Mentor for Undergraduate Research", "strong", none), (", ", none, none), ("Mathematical Biology Program", none, none), (" — University of Hawaii", none, none)),
        body: (
          (("Mentored students in math and dsp for classifying marine life audio signals.", none, none),),
        ),
      ),
    ),
  ),
  (
    title: "Advising and mentoring",
    kind: "list",
    entries: (
      (
        head: (("University of Colorado, Boulder", "strong", none),),
        body: (
          (("Served on the doctoral candidacy exam committee for the following ph.d. students: Jordan DuBeau, Ali Lotfi, Athena Sparks, Michael Wheeler. Served on the dissertation defense committee for Jeffrey Shriner.", none, none),),
        ),
      ),
      (
        head: (("Iowa State University", "strong", none),),
        body: (
          (("REU mentor for Charlotte Aten (mathematics major, University of Rochester); honors thesis advisor for Joshua Thompson (mathematics major, honors program); Putnam Exam mentor at weekly exam practice meetings; Undergraduate Tea cohost of weekly undergraduate student gatherings; Iowa 4-H Youth Conference volunteer mentor.", none, none),),
          (("Link", none, "https://math.iastate.edu/2015/10/28/4-h-dared-to-discover-the-math-of-juggling/"),),
        ),
      ),
      (
        head: (("University of South Carolina", "strong", none),),
        body: (
          (("Honors thesis mentor for Matthew Corley (computer science major, honors program); South Carolina High School Math Contest exam design committee; Faculty mentor for Pi Mu Epsilon (math honors society).", none, none),),
        ),
      ),
    ),
  ),
  (
    title: "Certifications",
    kind: "list",
    entries: (
      (
        head: (("Smart Contracts", "strong", none),),
        body: (
          (("SUNY at Buffalo, 4-week Coursera course, 96.4%, 5 Sep 2021", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/verify/UTGLFVHW79WV")),
        ),
      ),
      (
        head: (("Blockchain Basics", "strong", none),),
        body: (
          (("SUNY at Buffalo, 4-week Coursera course, 100%, 6 Aug 2021", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/verify/4NP2MX787UAG")),
        ),
      ),
      (
        head: (("Big Data Analysis with Scala and Spark", "strong", none),),
        body: (
          (("Ecole Polytechnique Federale de Lausanne, 4-week Coursera course, 93.4%, 24 Nov 2017", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/records/93DVEX3QH86L")),
        ),
      ),
      (
        head: (("Functional Programming Principles in Scala", "strong", none),),
        body: (
          (("Ecole Polytechnique Federale de Lausanne, 6-week Coursera course, 100%, 17 Nov 2016", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/records/CKWD8PLCPW4E")),
        ),
      ),
      (
        head: (("Functional Program Design in Scala", "strong", none),),
        body: (
          (("Ecole Polytechnique Federale de Lausanne, 4-week Coursera course, 100%, 6 Aug 2016", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/records/2WE2UZSR5AAZ")),
        ),
      ),
      (
        head: (("Parallel Programming in Scala", "strong", none),),
        body: (
          (("Ecole Polytechnique Federale de Lausanne, 4-week Coursera course, 100%, 27 Jun 2016", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/account/accomplishments/records/3XV34H6BTTHC")),
        ),
      ),
      (
        head: (("Startup Engineering", "strong", none),),
        body: (
          (("Stanford University, 12-week Coursera course, 99.3%, 23 Sep 2013", none, none), (" · ", none, none), ("Certificate", none, "https://www.coursera.org/maestro/api/certificate/get_certificate?course_id=970374")),
        ),
      ),
    ),
  ),
  (
    title: "Summer schools and short courses",
    kind: "list",
    entries: (
      (
        head: (("Agda Implementors' Meeting XXXIX", "strong", "https://wiki.portal.chalmers.se/agda/Main/AIMXXXIX"),),
        body: (
          (("Chalmers University, 25–30 Nov 2024", none, none),),
        ),
      ),
      (
        head: (("Agda Implementors' Meeting XXXVIII", "strong", "https://wiki.portal.chalmers.se/agda/Main/AIMXXXVIII"),),
        body: (
          (("University of Swansea, 13–18 May 2024", none, none),),
        ),
      ),
      (
        head: (("Midlands Graduate School in the Foundations of Computing Science", "strong", "http://www.cs.nott.ac.uk/MGS/"),),
        body: (
          (("Lambda calculus, simply typed lambda calculus, domain theory, denotational semantics, type theory, univalent type theory in Agda, homotopy type theory, category theory, proof theory, univalent foundations.", none, none),),
        ),
        items: (
          (
            head: (("Univ. of Sheffield, virtual, April 12–16, 2021", none, "https://staffwww.dcs.shef.ac.uk/people/G.Struth/mgs21.html"),),
          ),
          (
            head: (("Univ. of Birmingham, April 14–18, 2019", none, "http://events.cs.bham.ac.uk/mgs2019/"),),
          ),
          (
            head: (("University of Birmingham, April 11–15, 2016", none, "http://www.cs.bham.ac.uk/~pbl/mgs2016/"),),
          ),
          (
            head: (("University of Nottingham, April 22–26, 2014", none, "http://www.cs.nott.ac.uk/~psztxa/mgs.2014/"),),
          ),
        ),
      ),
      (
        head: (("Oregon Programming Languages Summer School", "strong", "https://www.cs.uoregon.edu/research/summerschool/"),),
        body: (
          (("University of Oregon", none, none),),
          (("Type theory, logic, semantics, verification, parallelism and concurrency, dependent, gradual, substructural type systems.", none, none),),
        ),
        items: (
          (
            head: (("July 3–21, 2018", none, "https://www.cs.uoregon.edu/research/summerschool/summer18/topics.php"),),
          ),
          (
            head: (("June 26–July 8, 2017", none, "https://www.cs.uoregon.edu/research/summerschool/summer17"),),
          ),
          (
            head: (("June 16–28, 2014", none, "https://www.cs.uoregon.edu/research/summerschool/summer14/curriculum.html"),),
          ),
        ),
      ),
      (
        head: (("Computer-aided Mathematical Proof", "strong", "https://www.newton.ac.uk/event/bprw01"),),
        body: (
          (("Cambridge University, July 10–14, 2017", none, none),),
          (("Bringing proof technology into mainstream mathematics.", none, none),),
        ),
      ),
      (
        head: (("LMS/EPSRC Short Course in Computational Group Theory", "strong", "http://www-circa.mcs.st-and.ac.uk/cgt2013/"),),
        body: (
          (("University of St. Andrews, Jul 29–Aug 2, 2013", none, none),),
          (("Permutation & finitely presented groups, constructive recognition.", none, none),),
        ),
      ),
      (
        head: (("NATO ASI on Computational Noncommutative Algebra", "strong", none),),
        body: (
          (("Il Ciocco, Italy, 2003", none, none),),
        ),
      ),
    ),
  ),
  (
    title: "References",
    kind: "list",
    entries: (
      (
        head: (("Clifford Bergman", "strong", none), (", Professor of Mathematics, Iowa State University", none, none), (" (teaching reference)", none, none)),
      ),
      (
        head: (("Venanzio Capretta", "strong", none), (", Assistant Professor of Computer Science, University of Nottingham", none, none)),
      ),
      (
        head: (("Ralph Freese", "strong", none), (", Professor of Mathematics, University of Hawaii", none, none)),
      ),
      (
        head: (("Peter Jipsen", "strong", none), (", Professor of Mathematics, Chapman University", none, none)),
      ),
      (
        head: (("George McNulty", "strong", none), (", Professor of Mathematics, University of South Carolina", none, none)),
      ),
      (
        head: (("Peter Mayr", "strong", none), (", Assistant Professor of Mathematics, University of Colorado, Boulder", none, none), (" (teaching reference)", none, none)),
      ),
      (
        head: (("J.B. Nation", "strong", none), (", Emeritus Professor of Mathematics, University of Hawaii", none, none)),
      ),
    ),
  ),
)

#render-sections(sections)
