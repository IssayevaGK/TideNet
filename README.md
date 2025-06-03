# TideNet

# The code for TideNet

This repo contains the source code for the TideNet model.

## programming language

Python and Pytorch with 3.9.0 or later

## Required libraries

```
python>=3.11.3
pytorch>=2.6.0+cu124
transformers==4.51.3
```

## Datasets info

Please download the T-drive dataset [here](https://hub.marinecadastre.gov/), and then extract it in `data` folder.

## Data preprocessing

Since the raw AIS data contains multiple types of noise, inconsistencies, and redundant points, we design a multi-stage data cleaning and preprocessing pipeline to ensure the high quality of input trajectories for downstream model training.

First, initial data cleaning is performed following domain-specific rules (implemented in DataClean.py). Invalid records are filtered by checking MMSI length, inconsistent vessel identifiers (IMO), insufficient data density, unrealistic vessel dimensions, and out-of-bound geographic or speed values. To further eliminate noisy samples, a dynamic sliding window method is applied to detect and remove duplicate or highly similar AIS records within the same trajectory segments based on feature similarity thresholds.

Next, we transform the cleaned AIS records into grid-based spatial representation using meshing (meshing.py). The maritime region is divided into uniform spatial grids based on the UTM projection, and grid identifiers are assigned to each AIS record. Sparse grids with insufficient data density are excluded to ensure spatial consistency.

Finally, the cleaned and meshed data is further processed into structured trajectory sequences through several modules:

   Trip segmentation and filtering (trip_count.py, trip2trips.py) — splits continuous AIS streams into individual trips based on time intervals, minimum duration constraints, and generates compact encoded sequences.

   Grid index normalization (trips2new.py) — reassigns grid identifiers into consecutive indices to optimize the input format.

   Sparse mask generation and tagging (trips_drop.py) — simulates missing data scenarios by probabilistically dropping certain portions of each trip while recording deletion masks for supervised recovery tasks.

   Train-validation-test splitting (trips_split.py) — partitions the resulting dataset into training, validation, and test sets

The entire preprocessing pipeline ensures that high-quality, spatially consistent, and controlled sparse trajectory sequences are generated for model training and evaluation.

## Evaluate Model

We release the pretrained models for both stages in the model directory. The models can be directly evaluated on the test set by executing:
```
cd recovery_stage
python test_TERI.py
```

## Train Model

To train TideNet, change to the `recovery_stage` or `detection_stage` folder for the stage you are interested and run following command: 

```
python train.py --batch_size=128 --num_epochs=150 --segment_duration_hours=n --num_time_segments=z --time_step=5

num_time_segments = 24 / segment_duration_hours

```
## References

[1]	Y. Chen, G. Cong, and C. Anda, “TERI: An effective framework for trajectory recovery with irregular time intervals,” Proc. VLDB Endowment, vol. 17, no. 3, pp. 414–426, 2024, doi: 10.14778/3632093.3632105.
