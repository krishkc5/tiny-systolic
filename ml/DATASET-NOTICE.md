# Dataset attribution

The digit inputs and labels in fixtures/digits_int4.json are a transformed subset of the Optical Recognition of Handwritten Digits dataset by E. Alpaydin and C. Kaynak (1998), obtained through scikit-learn's load_digits. Source: https://doi.org/10.24432/C50P49 (UCI Machine Learning Repository).

UCI identifies the dataset license as Creative Commons Attribution 4.0 International: https://creativecommons.org/licenses/by/4.0/ . This dataset-derived content retains that license; the repository's code license does not replace it.

Changes: selected a fixed stratified 360-example holdout from scikit-learn's 1,797 examples, mapped pixels from 0..16 to 0..7 with rounding, and added learned model parameters and generated reference outputs. Attribution does not imply endorsement by the dataset creators.

The experiment is a new train/test split of scikit-learn's subset, not the original UCI full-dataset benchmark split.
