# Contributing

The Distant Reader consists of two general parts: a text processing workflow designed to run on HPC clusters, and a web-based user interface.
The parts communicate through a shared-file space containing _study carrels_.
A study carrel collects a specific pile of documents with its analysis, and
each study carrel takes the form of a directory.

## Web Interface

You can run the web interface locally with Docker.
(However, note that Docker isn't used for the production deploy).

    make web-run
    
And then you can view the website at http://localhost:8000
