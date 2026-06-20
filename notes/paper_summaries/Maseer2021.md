# Paper Summary: Maseer2021

-   **BibTeX Key**: Maseer2021
-   **Title**: Benchmarking of Machine Learning for Anomaly Based Intrusion Detection Systems in the CICIDS2017 Dataset
-   **Authors**: Ziadoon Kamil Maseer, Robiah Yusof, Nazrulazhar Bahaman, Salama A. Mostafa, and Cik Feresa Mohd Foozy
-   **Year**: 2021
-   **Publication Venue**: IEEE Access

---

## Research Objective
To comprehensively benchmark 10 popular supervised and unsupervised Machine Learning (ML) algorithms for Anomaly-based Intrusion Detection Systems (AIDS) using the CICIDS2017 dataset. The primary goal is to identify effective and efficient ML-AIDS algorithms, suitable parameters, and testing criteria, while also considering training and testing time as crucial performance efficiency factors.

## Problem Addressed
Previous AIDS literature often suffers from issues such as the randomness in the selection of algorithms, parameters, and testing criteria, the frequent use of old, unrepresentative datasets, and shallow analyses or validations of results. Many studies rely solely on accuracy, which is misleading for highly imbalanced datasets. There is a lack of comprehensive benchmarking that addresses multi-class classification, evaluates efficiency (training/testing time), and provides a standard methodology for comparing AIDS models.

## Methodology
The study proposes and implements a benchmarking methodology for ML-AIDS models, specifically utilizing the CICIDS2017 dataset.
*   **Dataset Selection**: CICIDS2017 dataset was chosen for its recency, realistic nature, and inclusion of up-to-date attacks, addressing the issue of outdated datasets.
*   **Preprocessing**:
    *   Used the `MachineLearning.CSV` part of the CICIDS2017 dataset.
    *   **Numericalization**: Noise values (null or infinity symbols) were replaced with zeros or mean values.
    *   **Normalization**: Attributes were normalized to the `[-3, 3]` interval using z-score standardization followed by clipping. This process resulted in a set of 38 features. This range was selected to improve data distribution and training outcomes.
*   **Training Strategy**: `k-folds cross-validation` was used, with various splits (e.g., 40-60%, 50-50%, 60-40% for training-testing). Hyperparameters were tuned for each algorithm through iterative examination.
*   **Testing**: 10 ML algorithms (7 supervised, 3 unsupervised) were applied.
    *   **Supervised**: ANN, DT, k-NN, NB, RF, SVM, CNN.
    *   **Unsupervised**: EM, k-means, SOM.
*   **Evaluation**: The performance of 31 ML-AIDS models (from the 10 algorithms) was evaluated.

## ML Models Used
*   **Supervised Learning Algorithms**:
    *   Artificial Neural Network (ANN)
    *   Decision Tree (DT)
    *   k-Nearest Neighbor (k-NN)
    *   Naive Bayes (NB)
    *   Random Forest (RF)
    *   Support Vector Machine (SVM)
    *   Convolutional Neural Network (CNN)
*   **Unsupervised Learning Algorithms**:
    *   Expectation-Maximization (EM)
    *   k-means clustering
    *   Self-Organizing Maps (SOM)

## Datasets Used
**CICIDS2017 dataset**: A recent and highly unbalanced multi-class dataset involving real-world network attacks. It contains a diverse range of attack types (classified into C1: BENIGN, C2: Brute Force, C3: XSS, C4: SQL Injection for the study's specific context). The dataset originally has 78 features, but was preprocessed down to 38 features.

## Preprocessing
*   **Numericalization**: Replaced null/infinity with 0s or mean.
*   **Normalization**: Z-score standardization followed by clipping to `[-3, 3]` for 38 features.

## Evaluation Metrics
*   **Accuracy**
*   **Precision**
*   **Sensitivity (Recall)**
*   **F1-Score**
*   **Training Time (T1)**
*   **Testing Time (T2)**
*   Confusion Matrix terms (TP, TN, FP, FN) were used for calculation.

## Results
*   **Overall Performance Trend**: Supervised learning algorithms generally **outperformed** unsupervised ones.
*   **Best Supervised Performers**:
    *   **DT**: Achieved 99.49% Acc, 99.49% P, 99.49% R, 99.49% F1 (1.23s T1, 1.12s T2).
    *   **RF**: Achieved 99.54% Acc, 99.56% P, 99.54% R, 99.55% F1 (9.38s T1, 6.76s T2).
    *   **k-NN**: Achieved 99.49% Acc, 99.5% P, 99.49% R, 99.49% F1 (11.13s T1, 7.92s T2).
    *   **NB**: Achieved 98.86% Acc, 99.01% P, 98.86% R, 98.85% F1 (1.07s T1, 0.15s T2).
    *   **CNN**: Achieved 99.50% Acc, 99.46% P, 99.50% R, 99.47% F1 (261.8s T1, 1.73s T2).
    *   **ANN**: Achieved 99.31% Acc, 99.50% P, 99.31% R, 99.22% F1 (53.78s T1, 48.03s T2).
    *   **SVM**: Achieved 96.72% Acc, 99.27% P, 96.72% R, 97.89% F1 (343.56s T1, 33.17s T2).
*   **Best Unsupervised Performer**: EM (60.06% Acc, 86.88% P, 60.06% R, 74.11% F1) was the best among the unsupervised.
*   **Poor Unsupervised Performers**: k-means (23.41% Acc) and SOM (59.06% Acc) showed poor classification performance.
*   **Detection of Web Attacks**: k-NN-AIDS, DT-AIDS, and NB-AIDS models obtained the best results and showed greater capability in detecting web attacks.
*   **Class Imbalance Impact**: Most algorithms achieved high detection rates for C1 (BENIGN) and C2 (Brute Force) attacks, moderate for C3 (XSS), and low for C4 (SQL Injection). All CNN and SOM models failed to detect C4 attacks, illustrating the effect of class imbalance.
*   **Time Efficiency**: DT, RF, NB, k-means, and EM had much shorter model building durations compared to CNN, SVM, SOM, and ANN. DT and k-NN were highlighted for their efficiency.

## Limitations
*   The CICIDS2017 dataset is highly unbalanced, which biases models towards majority classes and affects detection of minority attacks.
*   Reliance solely on accuracy as an evaluation metric can be misleading for imbalanced datasets.
*   "No single ML algorithm can detect all types of web attacks."
*   The study focuses on web attacks specifically for some results, which might not generalize to all attack types.

## Future Work
*   Measure the impact of feature selection on AIDS performance.
*   Consider new methodological steps for developing deep learning CNN-AIDS models.

## Research Gaps Identified
*   Randomness in selection of algorithms, parameters, and testing criteria in previous AIDS literature.
*   Frequent use of old datasets not representative of modern attacks.
*   Shallow analyses and validations in existing AIDS.
*   Lack of a clear benchmarking methodology, especially for multi-class classification and considering efficiency (time).
*   The need for more robust evaluations for highly imbalanced multi-class datasets.

## Relevance to AgriIoT IDS
**Highly relevant and foundational**. This paper provides a comprehensive benchmarking study using the **CICIDS2017 dataset**, which is central to our project. The direct comparison of numerous supervised and unsupervised ML/DL models, including our project's Random Forest and Autoencoder, offers invaluable empirical data. The findings explicitly highlight the superior performance of supervised models (like DT, RF, k-NN) over unsupervised (k-means, EM, SOM) when labeled data is available, confirming a key argument of our project. The detailed performance metrics (accuracy, F1, precision, recall, and crucially, training/testing time) are essential for selecting and optimizing lightweight IDS for resource-constrained AgriIoT environments. The paper also strongly emphasizes the challenges of class imbalance and the need for multi-criteria evaluation, which are critical considerations for real-world AgriIoT deployments.
