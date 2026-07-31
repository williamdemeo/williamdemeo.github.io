+++
title="Converting old Sage .sws worksheets to .ipynb (jupyter) format"
date = 2019-02-17
template="page.html"
+++

This post describes how I converted my old .sws Sage worksheets to the new .ipynb (jupyter) format.

1. **Install** the required software.

   ```sh
   sage -i beautifulsoup
   sage -pip install git+https://github.com/vbraun/ExportSageNB.git
   sudo apt install python3-sagenb-export 
   sage -i rst2ipynb
   ```

   (I had first tried `pip install git+https://github.com/vbraun/ExportSageNB.git` in place of the second command above, but it didn't work.)

2. **Export** the `experiments.sws` file in two steps (sws -> rst -> ipynb)

   ```sh
   sage -sws2rst experiments.sws experiments.rst
   sage -rst2ipynb experiments.rst experiments.ipynb
   ```

   Alternatively, I think this would have worked:

   ```sh
   sage -sws2rst experiments.sws experiments.rst
   sagenb-export --list
   sagenb-export --ipynb=experiments.ipynb admin:0
   ```

   (where `admin:0` is the unique handle to experiments.rst that showed up in the list).

3. **Load** the experiments notebook in the new format.

   Launch Sage while loading the experiments notebook as follows:

   ```sh
   sage --notebook=jupyter experiments.ipynb
   ```

---

## Another example

1. **Install** the required software (as above).

2. **Export** the `MAA-DeMeo-DeMo.sws` file in two steps (sws -> rst -> ipynb)

   ```sh
   sage -sws2rst MAA-DeMeo-DeMo.sws MAA-DeMeo-DeMo.rst
   sage -rst2ipynb MAA-DeMeo-DeMo.rst MAA-DeMeo-DeMo.ipynb
   ```

3. **Load** the MAA-DeMeo-DeMo notebook in the new format

   Launch Sage while loading the MAA-DeMeo-DeMo notebook as follows:

   ```sh
   sage -n jupyter MAA-DeMeo-DeMo.ipynb 
   ```
