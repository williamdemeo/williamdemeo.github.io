williamdemeo.github.io
======================

## main weblog repository

This repository is build and maintained with [Octopress](http://octopress.org/).

I found the following posts helpful when creating it:

+ [Get RedCloth installed properly on Ubuntu](http://stackoverflow.com/questions/14245822/cannot-install-redcloth)   
+ [Setup Octopress, pick a theme, maintain with rake](http://paulsturgess.co.uk/blog/2013/04/24/hello-octopress-and-github-pages/)
+ [Maintain Octopress repo on multiple machines](http://blog.zerosharp.com/clone-your-octopress-to-blog-from-two-places/)  
+ [Get MathJax working](http://www.idryman.org/blog/2012/03/10/writing-math-equations-on-octopress/)
+ [Select a nice theme](https://github.com/imathis/octopress/wiki/3rd-Party-Octopress-Themes)
+ [Troubleshoot UTF-8 locale](http://stackoverflow.com/questions/17031651/invalid-byte-sequence-in-us-ascii-argument-error-when-i-run-rake-dbseed-in-ra)
+ [Changing fonts and colors](http://blog.bigdinosaur.org/changing-octopresss-header/)

Carl Boettiger has an amazing [open notebook](http://carlboettiger.info/index.html).


## Setting up existing Octopress repo on Ubuntu.

1.  Get the source:

        git clone -b source git@github.com:uwilliamdemeo/williamdemeo.github.io.git octopress
        cd octopress
        git clone git@github.com:williamdemeo/williamdemeo.github.io.git _deploy 
   
2.  Make sure ruby1.9.1-dev is installd:

        sudo apt-get install ruby1.9.1-dev

3.  Run rake installer to configure:

        gem install bundler
        rbenv rehash
        bundle install
        rake setup_github_pages
     
## Workflow

1.  Make some changes, e.g., create a new post:

        rake new_post["title"]

	  
2.  Posts live in `source/_posts`.  Edit one and push the changes to source branch.
   
        rake generate
        git add .
        git commit -am "Some comment here." 
        git push origin source  # update the remote source branch 

3. Now preview the changes: `rake preview` then point a browser to `http://localhost:4000`.

4. When satisfied, `rake deploy`.
