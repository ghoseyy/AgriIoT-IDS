# Paper Summary: Verma2020

-   **BibTeX Key**: Verma2020
-   **Title**: Machine Learning Based Intrusion Detection Systems for IoT Applications
-   **Authors**: Abhishek Verma and Virender Ranga
-   **Year**: 2020
-   **Publication Venue**: Wireless Personal Communications

---

## Research Objective
To investigate the prospects of using machine learning (ML) classification algorithms for securing IoT against Denial of Service (DoS) attacks. The study aims to carry out a comprehensive assessment of classifiers for anomaly-based Intrusion Detection Systems (IDSs), including statistical analysis of classifier performance and evaluation of response time on IoT-specific hardware (Raspberry Pi).

## Problem Addressed
The self-configuring and open nature of IoT makes it vulnerable to various insider and outsider attacks, with DoS being a catastrophic threat leading to monetary losses and service disruption in smart applications like smart homes and smart agriculture. Traditional IDS (signature/specification-based) are often inadequate for new attacks or suffer from high false alarm rates. There is a lack of work statistically analyzing classifier performance or realizing their execution on real IoT hardware for intrusion detection.

## Methodology
The study conducts a comprehensive performance assessment of various ML classifiers:
*   **Classifiers Evaluated**:
    *   **Ensemble Classifiers**: Random Forest (RF), AdaBoost (AB), Gradient Boosted Machine (GBM), Extreme Gradient Boosting (XGB), and Extremely Randomized Trees (ETC).
    *   **Single Classifiers**: Classification and Regression Trees (CART), and Multi-layer Perceptron (MLP).
*   **Hyperparameter Tuning**: Optimal parameters for classifiers were obtained using a **random search algorithm** (`RandomizedSearchCV` in scikit-learn).
*   **Validation Methods**:
    *   **Repeated Hold-out Validation**: Dataset split 60% training, 40% testing, repeated 100 rounds.
    *   **Repeated k-fold Cross-validation**: 10-fold cross-validation, repeated 100 rounds.
*   **Statistical Significance Tests**:
    *   **Friedman Test**: Non-parametric test to determine if there is a significant performance difference among classifiers.
    *   **Nemenyi Post-hoc Test**: For pairwise multiple comparisons to identify where significant differences lie.
*   **Hardware Evaluation**: Average response time (time to classify a single instance) was measured by executing classifiers on a **Raspberry Pi 3 Model B+**.
*   **Experimental Environment**: Python 3.6.1, scikit-learn. Performance assessment on 64-bit Windows 10 Pro (Intel i7-7700 CPU, 12GB RAM). Hyper-tuning on PARAM Shavak system (Ubuntu 14.04, Intel Xeon Gold 6132 CPU, 96GB RAM).

## ML Models Used
*   **Random Forest (RF)**
*   **AdaBoost (AB)**
*   **Gradient Boosted Machine (GBM)**
*   **Extreme Gradient Boosting (XGB)**
*   **Extremely Randomized Trees (ETC)**
*   **Classification and Regression Trees (CART)**
*   **Multi-layer Perceptron (MLP)**

## Datasets Used
Three datasets were used for benchmarking:
*   **CIDDS-001**: Recently released, ~32 million records (100,000 instances extracted for experiments: 80,000 normal, 20,000 DoS attacks). 12 features.
*   **UNSW-NB15**: Recently publicly available, 49 features, ~2 million records. Train set (175,341 instances), Test set (82,332 instances).
*   **NSL-KDD**: Refined KDD Cup’99, 41 features. KDDTrain+ (25,192 instances), KDDTest+ (22,544 instances).

## Preprocessing
A general AI-based NIDS methodology was discussed in the paper, involving a data preprocessing phase that typically includes:
*   **Encoding**
*   **Normalization**
*   **Cleaning**: Removing entries with missing data and duplicate entries.
Specific preprocessing for each dataset in the experiments was not explicitly detailed in the abstract, but the process generally ensures data is suitable for algorithms.

## Evaluation Metrics
*   **Accuracy**
*   **Specificity (True Negative Rate)**
*   **Sensitivity (True Positive Rate/Recall)**
*   **False Positive Rate (FPR)**
*   **Area Under the Receiver Operating Characteristic Curve (AUC)**
*   **Model Building Time (MBT)**
*   **Average Response Time** (on Raspberry Pi).

## Results
*   **Hold-out Validation Performance**:
    *   RF: best accuracy (94.94%), best specificity (91.6%).
    *   GBM: best sensitivity (99.53%).
    *   XGB: best AUC (98.76%).
    *   MLP: worst accuracy (82.76%). AB: worst specificity (86.72%), sensitivity (97.94%). CART: lowest AUC (94.01%).
    *   RF: best FPR (8.89%). AB: worst FPR (13.26%).
*   **10-fold Cross-Validation Performance**:
    *   Performance of all classifiers improved compared to hold-out validation.
    *   CART: best accuracy (96.74%).
    *   AB: highest average specificity (97.5%).
    *   RF and XGB: best sensitivity (97.31%).
    *   XGB: best AUC (98.77%).
    *   CART: best FPR (3.78%). RF: worst FPR (21.85%).
*   **Statistical Analysis**: Friedman and Nemenyi tests confirmed statistically significant performance differences among classifiers for most metrics in hold-out validation, and for AUC in 10-fold validation.
*   **Average Response Time (on Raspberry Pi)**:
    *   CART achieved the minimum time to classify an instance.
    *   RF and XGB showed almost similar quick response times.
    *   ETC took maximum time for some datasets. GBM was worst for KDDTrain+.
*   **Optimal Choice**: CART and XGB show the best trade-off between prominent metrics and response time, making them suitable for IoT-specific anomaly-based IDS.

## Limitations
*   The study used only supervised learning-based ML classifiers. Unsupervised learning methods were not evaluated, but mentioned as future work.
*   Identified problem of low detection accuracy for low-frequency attack classes due to dataset imbalance, which needs further attention.
*   Acknowledged that older datasets like NSL-KDD may not reflect modern network attacks.

## Future Work
*   Conduct performance assessment of unsupervised ML algorithms for intrusion detection in IoT.
*   Design an IDS for defending routing attacks in IoT networks.

## Research Gaps Identified
*   Lack of statistical analysis of classifier performance for IoT-based intrusion detection.
*   Absence of execution and evaluation of classifiers on real IoT hardware.
*   Problem of class imbalance leading to lower detection accuracy for minority attack classes.
*   Need for up-to-date datasets reflecting modern attacks.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper provides critical insights into selecting appropriate ML classifiers for IoT-specific anomaly-based IDS, particularly for DoS attacks. Its rigorous methodology, including statistical analysis and direct evaluation on Raspberry Pi (a common IoT hardware platform), is invaluable for AgriIoT, which features resource-constrained devices and demands efficient, real-time threat detection. The comparison of various supervised ML models and their performance trade-offs in terms of accuracy, false positive rate, and response time directly informs the design choices for lightweight AgriIoT IDS. It also highlights the importance of using modern, realistic datasets.
