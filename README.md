# NFB Studio 
*NFB Studio* allows you to design and execute experiments in real-time EEG/MEG paradigm. Built on top of [NFB Lab](https://github.com/andreasxp/nfb), this application allows for a more intuitive experiment design.

## Installation
Prerequisites: [python](https://www.python.org/), [git](https://git-scm.com/), optionally [conda](https://docs.conda.io/en/latest/miniconda.html).  
**Warning**: NFB Studio requires you install some outdated versions of packages. Consider installing it in a virtual enviroment, using tools such as venv or conda. For example, if using conda, create and activate a new environment by running these commands first:
```
conda create -n nfb_studio python pip
conda activate nfb_studio
```

Regardless of whether you are using a virtual environment, clone this repository and install the package in editable mode by running:
```
git clone https://github.com/bioelectric-interfaces/nfb_studio
cd nfb_studio
pip install -e .
```

## Running the experiment designer
After installation, NFB Studio can be run by using the following command:
```
nfb-studio
```
NFB Studio will also open an experiment right away if you specify the path in the command line:
```
nfb-studio experiment-file.nfbex
```
If you are experiencing sudden crashes, you may want to run NFB Studio in debug mode:
```
# Either one works
nfb-studio-d
python -m nfb_studio
```
