# SHEEP - Show Human Expression - Example Package
The SHEEP package generates images that compare expression levels of
given genes in a range of human cell lines.


## Table of Contents
- [SHEEP - Show Human Expression - Example Package](#sheep---show-human-expression---example-package)
  - [Table of Contents](#table-of-contents)
  - [General Information](#general-information)
  - [Features](#features)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Project Status](#project-status)
  - [Room for Improvement](#room-for-improvement)
  - [Acknowledgements](#acknowledgements)
  - [Contact](#contact)
  - [License](#license)


## General Information
This example package interacts directly with the API of the Human
Protein Atlas to retrieve expression levels of a given genes in the
specified cell lines and provides the results as an image.
It requires internet connection and relies on the matplotlib and pandas
packages.


## Features
The features already available are:
- Generation of images comparing gene expression across cell lines
- Optional addition of a background level


## Setup
The requirements are provided in a `requirements.txt` file.

SHEEP can be installed via pip:

``` bash
pip install --index-url https://test.pypi.org/simple/ sheep-example
```

Alternatively, it can be installed by downloading this repository and
then installing with pip (possibly in interactive mode):

``` bash
git clone https://github.com/ladislav-hovan/sheep.git
cd sheep
pip install -e .
```


## Usage
The main function that should be used is called `generate_gene_image`.
By default, it looks at all pancreatic cell lines in the Human Protein
Atlas, but this can be adjusted to another type of cell lines or cell
lines can be specified directly.
Proper usage requires matching the THPA naming conventions precisely.

``` python
# Import the package
import sheep
# Look at the function documentation
help (sheep.generate_gene_image)
# Generate an image
fig,ax = sheep.generate_gene_image('ERBB2')
# Choose breast cancer cell lines instead
fig,ax = sheep.generate_gene_image('ERBB2', 'cell_RNA_breast_cancer')
# Select cell lines, save directly into a file
fig,ax = sheep.generate_gene_image('ERBB2', 'cell_RNA_breast_cancer',
    cell_lines=['HCC1419', 'MX-1'], save_to='ERBB2_expression.png')
```


## Project Status
The project is: _in progress_.


## Room for Improvement
Room for improvement:
- Refactoring
- Command line script

To do:
- Unit tests
- CI/CD
- Dockerfile


## Acknowledgements
Many thanks to the members of the
[Kuijjer group](https://www.kuijjerlab.org/)
at NCMM for their feedback and support.

This README is based on a template made by
[@flynerdpl](https://www.flynerd.pl/).


## Contact
Created by Ladislav Hovan (ladislav.hovan@ncmm.uio.no).
Feel free to contact me!


## License
This project is open source and available under the
[MIT License](LICENSE).