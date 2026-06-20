# Paper Summary: Stoian

-   **BibTeX Key**: Stoian
-   **Title**: Machine Learning for Anomaly Detection in IoT Networks: Malware analysis on the IoT-23 Data set
-   **Authors**: Nicolas-Alin Stoian
-   **Year**: UNKNOWN_YEAR
-   **Publication Venue**: UNKNOWN_VENUE (University of Twente)

---

## Research Objective
To develop and test Machine Learning (ML) algorithms for network-based anomaly detection in Internet of Things (IoT) devices, focusing on malware analysis using the IoT-23 dataset. The paper also aims to compare the performance of these algorithms and the research findings with other similar studies.

## Problem Addressed
The security aspect is a major concern for potential IoT users. While passive security measures (e.g., passwords, encryption) exist, there's growing interest in active measures like using ML for attack detection and classification. ML algorithms require large datasets, which IoT systems can provide, and can handle the sheer number and manifestations of attacks that human operators find impossible. The portability of algorithms and the bypassing of security layers by exploiting other weaknesses in IoT networks present difficulties.

## Methodology
The study follows an empirical approach:
1.  **Dataset Preparation**: The IoT-23 dataset is visualized, analyzed, and fitted to the study's purpose.
    *   **Data Selection**: Utilized `conn.log.labeled` files from the IoT-23 dataset, discarding `.pcap` files due to unnecessary difficulty in working with them in Python.
    *   **Data Formatting**: `.txt` files (implicitly representing `conn.log.labeled` text output) converted to `.csv` format for Python compatibility.
    *   **Feature Engineering**: 'label' and 'detailed_label' columns were merged into one and then numerically encoded.
    *   **Feature Selection**: Statistical correlation was run on features, and only data with no statistical correlation to the column to be predicted was eliminated.
    *   **Data Splitting**: Random 80-20 split, with 80% designated as testing data and 20% as training data (this is an unusual split, typically it's the reverse).
2.  **Algorithm Implementation and Testing**: Five ML algorithms were implemented and tested on the prepared IoT-23 dataset.
3.  **Result Analysis and Comparison**: Final results were discussed and compared to similar studies.

## ML Models Used
*   **Random Forest (RF)**: Ensemble of decision trees.
*   **Naïve Bayes (NB)**: Probabilistic classifier assuming feature independence.
*   **Multi Layer Perceptron (MLP)**: A variant of Artificial Neural Network (ANN).
*   **Support Vector Machine (SVM)**
*   **AdaBoost (ADA)**: Ensemble classifier that focuses on misclassified instances.

## Datasets Used
**IoT-23 dataset** [@Parmisano2018]: A labeled dataset of Malware and Benign IoT Traffic, created by Avast AIC laboratory in partnership with the Czech Technical University. It contains 20 malware captures from various IoT devices and 3 benign captures, collected between 2018 and 2019.
*   **Total Captures**: 325,307,990 (294,449,255 malicious).
*   **Attack Types**: Generic Attack, Benign, C&C, C&C-File-Download, C&C-Mirai, C&C-Torii, DDoS, C&C-HeartBeat (and variants), C&C-PartOfAHorizontalPortScan, Okiru (and variants), PartOfAHorizontalPortScan (and variants).
*   **Features**: 23 columns including `ts` (Unix time), `uid`, `id_orig.h`, `id_orig.p`, `proto`, `service`, `duration`, `orig_bytes`, `resp_bytes`, `conn_state`, `label`, `detailed_label`, etc. (Zeek-specific features). Missing values marked with "-" or "::" for IPs.

## Preprocessing
*   **Data Conversion**: `.txt` to `.csv`.
*   **Label Merging**: 'label' and 'detailed_label' into a single target variable, numerically encoded.
*   **Feature Selection**: Elimination of features with no statistical correlation to the predicted target.
*   **Data Splitting**: 80% for testing, 20% for training.

## Evaluation Metrics
*   **Accuracy**
*   **F1-score**
*   **Recall score**
*   **Support score** (number of occurrences of a class)
*   Confusion Matrix for visualization.
*   Basic concepts of TP, TN, FP, FN were defined.

## Results
*   **Best Algorithm**: Random Forest (RF) achieved the best results across all metrics, with an accuracy of **99.5%** and a precision of **0.995%**.
*   **Comparison to Other Studies**: The results are consistent with other similar works that found RF or Naïve Bayes to be strong performers in anomaly detection (e.g., Shafiq et al. [17] (Bot-IoT, NB 99% Precision), Hasan et al. [9] (DS2OS, RF 99.4% Acc), Anthi et al. [2] (Custom, NB 97.7% Acc), Revathi and Malathi [14] (NSL-KDD, RF 99.8% Acc)).
*   **MLP (ANN)**: Achieved 99.1% accuracy but showed a bias towards categories with the largest number of occurrences.
*   **SVM**: Showed the worst performance with only 60% accuracy, never predicting benign behavior. It was better at predicting larger malware categories.
*   **Naïve Bayes (NB)**: Performed poorly, likely due to violations of its independence assumption in the dataset.
*   **Small Class Detection Issues**: None of the algorithms could identify rare attacks like Mirai (16 occurrences) or Torii botnet effectively, highlighting the problem of class imbalance for minority attack classes.

## Limitations
*   **Technical Constraints**: The dataset had to be split into smaller parts, and labels needed to be encoded with fewer categories to avoid computational problems, suggesting potential compromises in data representation.
*   Statistical correlation was run on each file, which might skew results.
*   Only features without statistical correlation to the predicted column were eliminated, potentially leaving other irrelevant features.
*   The reversed train-test split (80% test, 20% train) is unusual and could affect model generalization insights.
*   Poor detection of minority attack classes due to imbalance.

## Future Work
*   Redo the experiment using the full dataset with original label formats to overcome computational limitations.
*   Investigate the minimum amount of data from the IoT-23 dataset required for accurate models.
*   Further investigate the cause of high accuracy in Decision Tree classifiers (as part of RF).
*   Explore more advanced types of Artificial Neural Networks.

## Research Gaps Identified
*   The portability of ML algorithms in IoT networks.
*   Computational challenges in processing large IoT datasets with complex, numerous labels.
*   Effective handling of class imbalance for detecting rare attack types.
*   The security implications of bypassing security layers through other weaknesses in IoT networks.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper empirically validates Random Forest as a strong candidate for anomaly detection and malware analysis in IoT networks using the IoT-23 dataset. This directly supports our project's findings regarding Random Forest's high performance for AgriIoT IDS. It highlights crucial challenges relevant to AgriIoT, such as the computational complexity of handling large IoT datasets, the impact of class imbalance on detecting rare attack types (which can be critical in security), and the need for efficient algorithms. The comparative analysis against other ML models and the discussion of limitations (e.g., computational needs for full dataset processing) provide valuable insights for designing and deploying AgriIoT IDS in resource-constrained environments.
