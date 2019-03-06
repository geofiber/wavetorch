# wavetorch

## Overview

This package is for solving and optimizing (learning) on the two-dimensional (2D) scalar wave equation. Vowel data from [Prof. James Hillenbrand](https://homepages.wmich.edu/~hillenbr/voweldata.html) is in `data/`, study scripts are in `study/`, and the package itself is in `wavetorch/`. This package uses `pytorch` to perform the optimization and gradient calculations.

The best entry points to this package are the study scripts which are described below.

## Implementation

 - [ ] Describe the finite difference formulations
 - [ ] Describe how convolutions are used to implement the spatial FDs
 - [ ] Describe the adiabatic absorber formulation
 - [ ] Describe `WaveCell()`
 - [ ] Describe data loading and batching

## Usage

This package has been reorganized from the previous study scripts to use a common entry point. Now, the module has a training and inference mode. As an example, issuing the following command via ipython will train the model for 5 epochs:
```
%run -m wavetorch train --N_epochs 5 --batch_size 3 --train_size 12 --test_size 12
```
Alternatively, training can be performed directly from the command line by issuing the command
```
python -m wavetorch train --N_epochs 5 --batch_size 3 --train_size 12 --test_size 12
```
Many additional options are available for training and these will be printed to the screen when the `-h` or `--help` flags are issued:
```
usage: __main__.py train [-h] [--name NAME] [--num_threads NUM_THREADS]
                         [--use-cuda] [--sr SR] [--gender GENDER]
                         [--vowels [VOWELS [VOWELS ...]]] [--binarized]
                         [--design_region] [--init_rand] [--c0 C0] [--c1 C1]
                         [--Nx NX] [--Ny NY] [--dt DT] [--px [PX [PX ...]]]
                         [--py [PY [PY ...]]] [--pd PD] [--src_x SRC_X]
                         [--src_y SRC_Y] [--pml_N PML_N] [--pml_p PML_P]
                         [--pml_max PML_MAX] [--N_epochs N_EPOCHS] [--lr LR]
                         [--batch_size BATCH_SIZE] [--train_size TRAIN_SIZE]
                         [--test_size TEST_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           Name to use when saving or loading the model file
  --num_threads NUM_THREADS
                        Number of threads to use
  --use-cuda            Use CUDA to perform computations
  --sr SR               Sampling rate to use for vowel data
  --gender GENDER       Which gender to use for vowel data. Options are:
                        women, men, or both
  --vowels [VOWELS [VOWELS ...]]
                        Which vowel classes to run on
  --binarized           Binarize the distribution of wave speed between --c0
                        and --c1
  --design_region       Set design region
  --init_rand           Use a random initialization for c
  --c0 C0               Background wave speed
  --c1 C1               Second wave speed value used with --c0 when
                        --binarized
  --Nx NX               Number of grid cells in x-dimension of simulation
                        domain
  --Ny NY               Number of grid cells in y-dimension of simulation
                        domain
  --dt DT               Time step (spatial step size is determined
                        automatically)
  --px [PX [PX ...]]    Probe x-coordinates in grid cells
  --py [PY [PY ...]]    Probe y-coordinates in grid cells
  --pd PD               Spacing, in number grid cells, between probe points
  --src_x SRC_X         Source x-coordinate in grid cells
  --src_y SRC_Y         Source y-coordinate in grid cells
  --pml_N PML_N         PML thickness in grid cells
  --pml_p PML_P         PML polynomial order
  --pml_max PML_MAX     PML max dampening
  --N_epochs N_EPOCHS   Number of training epochs
  --lr LR               Optimizer learning rate
  --batch_size BATCH_SIZE
                        Batch size used during training and testing
  --train_size TRAIN_SIZE
                        Size of randomly selected training set
  --test_size TEST_SIZE
                        Size of randomly selected testing set
```

**WARNING:** depending on the batch size and the sample rate for the vowel data, determined by the `--sr` option, the gradient computation may require significant amounts of memory. Using too large of a value for either of these parameters may cause your computer to lock up.
**Note:** The model trained in this example will not perform very well because we used very few training examples.

After issuing the above command, the model will be optimized and the progress will be printed to the screen. After training, the model will be saved to a file, along with the training history and all of the input arguments.

The following command can be issued to load a previously saved model file:
```
%run ./study/inference.py --model <PATH_TO_MODEL>
```
Additionally, several options can be passed to this script to view various results.

The `--show` option will display the distribution of the wave speed, like so:
![](../master/img/c.png)

The `--hist` option will display the training history, if it was saved with the model, like so:
![](../master/img/hist.png)

The `--cm` option will display a confusion matrix, computed over the entire dataset, like so:
![](../master/img/cm.png)

The `--fields` option will display an integrated field distribution for the vowel classes, along with spectral information for the time series data, like so:
![](../master/img/fields.png)

## Requirements

This package has the following dependencies:

* `pytorch`
* `sklearn`
* `librosa`
* `seaborn`
* `matplotlib`
* `numpy`
