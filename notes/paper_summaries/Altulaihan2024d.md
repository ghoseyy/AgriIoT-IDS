# Paper Summary: Altulaihan2024d

-   **BibTeX Key**: Altulaihan2024d
-   **Title**: Anomaly Detection IDS for Detecting DoS Attacks in IoT Networks Based on Machine Learning Algorithms
-   **Authors**: Esra Altulaihan, Mohammed Amin Almaiah, and Ahmed Aljughaiman
-   **Year**: 2024
-   **Publication Venue**: Sensors

---

## Research Objective
To propose and evaluate an Intrusion Detection System (IDS) based on anomaly detection and machine learning (ML) techniques specifically designed to improve the security of IoT networks against Denial of Service (DoS) attacks. The study aims to select the most relevant features and identify the optimal ML classifier model for detecting DoS traffic.

## Problem Addressed
Internet of Things (IoT) systems are highly vulnerable to widespread and increasing cybersecurity attacks, with Denial of Service (DoS) attacks being among the most devastating. IoT devices are self-configuring and open, making them susceptible to insider and outsider attacks. Existing IDS frameworks often have limitations, such as reliance on traditional techniques or lack of strict security requirements, and few studies employ ML for explicit DoS detection in IoT networks. Securing IoT systems is a significant and growing concern.

## Methodology
The study proposes an **anomaly detection-based IDS** with a clear experimental workflow:
1.  **Dataset Selection**: IoTID20 dataset, chosen for its recency, variety of IoT attacks, and real-time traffic collection.
2.  **Data Preprocessing**:
    *   **Cleaning**: Verified no null values were present.
    *   **Feature Removal**: Removed `Src IP`, `Flow ID`, `Sub Cat`, `Dst IP`, `Timestamp`, and `Label` (total of 6 features removed from an initial 86 features, leaving 80 features). These were considered irrelevant or unhelpful for generalization.
    *   **Encoding**: Binary encoding for the target variable: 'DoS' mapped to 1, 'Normal' mapped to 0.
    *   Scaling and noise removal were deemed unnecessary due to the dataset's characteristics (mostly integers, no outliers, no inherent noise).
3.  **Feature Selection**: Two feature selection algorithms were utilized and compared:
    *   **Genetic Algorithm (GA)**: Selected 13 out of 80 features.
    *   **Correlation-based Feature Selection (CFS)**: Also selected the top 13 features for fair comparison with GA.
4.  **Data Splitting**: The dataset was divided into 67% for training and 33% for testing (66,640 training data points, 32,824 testing data points).
5.  **Classification Algorithms**: Four supervised ML classifiers were used:
    *   Decision Tree (DT)
    *   Random Forest (RF)
    *   K-Nearest Neighbor (kNN)
    *   Support Vector Machine (SVM)
    *   Each classifier was trained in three ways: with all features (80 features), with GA-selected features (13 features), and with CFS-selected features (13 features).
6.  **Performance Evaluation**: Utilized a confusion matrix and derived standard metrics.

## ML Models Used
*   **Classification**: Decision Tree (DT), Random Forest (RF), K-Nearest Neighbor (kNN), Support Vector Machine (SVM).
*   **Feature Selection**: Genetic Algorithm (GA), Correlation-based Feature Selection (CFS).

## Datasets Used
**IoTID20 dataset**: A recent (2020) and high-quality dataset containing various IoT attacks (DDoS, DoS, Mirai, ARP Spoofing) and normal traffic collected in real-time from smart home IoT ecosystems (SKTNGU, EZVIZ, laptops, smartphones, tablets, Wi-Fi). It originally contained 86 features and had 585,710 anomaly instances and 40,073 normal instances (total ~625k). The experiments focused on DoS and Normal traffic.

## Preprocessing
*   **Cleaning**: Null values checked and confirmed absent.
*   **Feature Removal**: `Src IP`, `Flow ID`, `Sub Cat`, `Dst IP`, `Timestamp`, `Label` were removed.
*   **Encoding**: DoS -> 1, Normal -> 0.
*   No scaling or noise removal applied.

## Evaluation Metrics
*   **Accuracy**
*   **Precision**
*   **Recall**
*   **F1 Score**
*   **Training Time (s)**
*   **Testing Time (s)**
*   Confusion Matrix (TP, TN, FP, FN) for detailed analysis.

## Results
*   **Optimal Performance**: **Decision Tree (DT) and Random Forest (RF) classifiers, when trained with GA-selected features (13 features), achieved 100% across Accuracy, Precision, Recall, and F1 score.**
*   **Training/Testing Time**:
    *   DT consistently provided the fastest training and testing times across all feature selection scenarios (e.g., GA-selected features: 0.0644s training, 0.0099s testing).
    *   RF was also fast but slightly slower than DT.
    *   kNN had fast training but considerably slower testing times.
    *   SVM had the slowest training times, particularly with CFS features (45.0077s).
*   **Feature Selection Impact**: GA proved highly effective in selecting optimal features that led to 100% performance for DT and RF. CFS also provided good feature subsets.
*   **SVM Limitations**: SVM performed poorly, especially with GA-selected features (88.29% Acc, 83.73% Precision). This is attributed to SVM's difficulty in handling large datasets with strong feature correlations.
*   **Confusion Matrix Analysis**: High TP and TN, low FP and FN for DT and RF with GA-selected features.
*   **Best Model**: DT classifier with GA-selected features was identified as the overall best model due to 100% performance and optimal time efficiency.

## Limitations
*   The claimed 100% performance results are specific to the chosen dataset (IoTID20) and attack type (DoS). The authors acknowledge the need for comprehensive validation in real IoT environments and different datasets to ensure generalizability.
*   The study focuses exclusively on DoS attacks.
*   SVM's performance issues with large, correlated datasets are noted.

## Future Work
*   Experiment with selecting fewer features and exploring other feature selection algorithms.
*   Test the proposed model by downloading it to a Raspberry Pi microcontroller board.
*   Conduct experiments and evaluate performance using other datasets (e.g., CIPMAIDS2023-1) or by building custom datasets from real-world IoT environments.
*   Implement and test other types of classifier algorithms, such as deep learning.

## Research Gaps Identified
*   Need for robust IDS mechanisms to counter widespread DoS attacks in IoT.
*   Lack of ML techniques explicitly optimized for DoS detection in IoT networks.
*   The need for lightweight and resource-efficient IDS suitable for IoT devices.
*   The challenge of finding suitable, up-to-date, and diverse IoT datasets for training and testing.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper directly addresses the development of lightweight and efficient IDS for IoT networks against a critical attack type (DoS), a scenario highly pertinent to AgriIoT. The focus on feature selection (GA, CFS) to achieve optimal performance with reduced features is essential for resource-constrained AgriIoT devices. The empirical comparison of ML classifiers (DT, RF, SVM, kNN) and the detailed analysis of training/testing times provide practical insights for selecting appropriate models for AgriIoT deployment. The use of a modern IoT dataset (IoTID20) also ensures the findings are relevant to contemporary IoT traffic patterns. The paper also explicitly states testing on Raspberry Pi in future work, which is valuable for AgriIoT hardware.
