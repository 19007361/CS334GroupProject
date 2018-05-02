# Basic file structure is as follows:

* Web/
  * run.py
  * WhoKnows/
    * \_\_init__.py
    * models.py
    * views.py
    * static/
      * (CSS files)
      * (JS files)
      * (Any other non-changing files)
    * templates/
      * index.html
      * layout.html
      * profile.html

# Hardcoded files
Please place Hardcoded files in a new folder in the _web_ directory with the page's name.

# How to run the site
1. Install (python 3) flask, py2neo, passlib, bcrypt
2. Download and install neo4j
3. Create a database with name Database and password password
4. Run that database
5. Navigate to /Web folder in terminal
6. Run the run.py file
