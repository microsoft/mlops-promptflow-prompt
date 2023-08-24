
# How to create a conda environment

Create a new conda environment using the following commands:

```cli
conda create -n pf Python=3.9
conda activate pf
```

(Optional) If you would like to do experimentation in Jupyter, use the following commands to extend just created environment:

```cli
conda install ipykernel
python -m ipykernel install --user --name pf --display-name "Python (pf)"
conda install jupyter
```

Install required packages:

```cli
pip install -r requirements.txt
```
