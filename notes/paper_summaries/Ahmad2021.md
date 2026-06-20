# Paper Summary: Ahmad2021

-   **BibTeX Key**: Ahmad2021
-   **Title**: Network Intrusion Detection System: A Systematic Study of Machine Learning and Deep Learning Approaches
-   **Authors**: Zeeshan Ahmad, Adnan Shahid Khan, Cheah Wai Shiang, Johari Abdullah, and Farhan Ahmad
-   **Year**: 2021
-   **Publication Venue**: Transactions on Emerging Telecommunications Technologies

---

## Research Objective
To provide a broad overview of the recent trends and advancements in Machine Learning (ML) and Deep Learning (DL)-based solutions for Network Intrusion Detection Systems (NIDS). The study aims to clarify IDS concepts, present a taxonomy of ML/DL techniques, comprehensively review recent NIDS articles, discuss their strengths, limitations, and recent trends, and highlight future research challenges and scopes.

## Problem Addressed
The rapid advances in internet and communication technologies have led to a huge increase in network size and data, generating many novel attacks. Network security faces challenges in accurately detecting intrusions, improving detection accuracy, reducing false alarm rates (FAR), and detecting novel (zero-day) intrusions. Existing IDSs often show inefficiency in these areas.

## Methodology
This study conducts a **systematic literature review** of journal articles published between 2017 and April 2020.
*   **Phase 1 (Article Identification)**:
    *   Search engine: Scopus.
    *   Keywords: "intrusion detection system", "network anomaly detection", "signature-based network intrusion detection" combined with "machine learning" or "deep learning".
    *   Filter: Journal articles published between 2017 and 2020.
*   **Phase 2 (Article Selection and Analysis)**:
    *   Criteria: English language, proposed a new AI-based idea (excluding other reviews/surveys).
    *   Analysis of selected articles: Proposed ML- or DL-based methodology, advantages, disadvantages, most frequently used datasets, and evaluation metrics.
*   **Structure**: The paper outlines IDS concepts and classifications (deployment and detection methods), explains common ML and DL algorithms used for NIDS, details evaluation metrics, and lists benchmark public datasets.

## ML Models Used
The survey discusses various ML algorithms used for NIDS, categorized as "Shallow Learning":
*   **Decision Tree (DT)**
*   **K-Nearest Neighbor (KNN)**
*   **Artificial Neural Network (ANN)**
*   **Support Vector Machine (SVM)**
*   **K-Mean Clustering** (unsupervised)
*   **Fast Learning Network (FLN)**
*   **Ensemble Methods**: Random Forest (RF), AdaBoost (AB), Gradient Boosted Machine (GBM), Extreme Gradient Boosting (XGB), Extremely Randomized Trees (ETC).

## DL Models Used
The survey discusses various DL algorithms used for NIDS, categorized as "Deep Learning":
*   **Recurrent Neural Networks (RNN)**: Long Short-Term Memory (LSTM), Gated Recurrent Unit (GRU).
*   **AutoEncoder (AE)**: Stacked AE, Sparse AE, Variational AE (VAE).
*   **Deep Neural Network (DNN)**: Generic multi-layer structure.
*   **Deep Belief Network (DBN)**: Stacking Restricted Boltzmann Machines (RBM).
*   **Convolutional Neural Network (CNN)**
*   **Few-shot Learning (FSL)**

## Datasets Used
The paper summarizes popular public benchmark datasets used for testing NIDS:
*   **KDD Cup’99** (1998): Old, 41 features, 4 attack types (DoS, Probe, R2L, U2R).
*   **Kyoto 2006+** (2006): Honeypot data, 24 statistical features.
*   **NSL-KDD** (2009): Refined KDD Cup’99, 41 features.
*   **UNSW-NB15** (2015): 49 features, 9 attack types (Worms, Shellcode, Reconnaissance, Port Scans, Generic, Backdoor, DoS, Exploits, Fuzzers).
*   **CIC-IDS2017** (2017): Real-world attacks, 7 attack scenarios (Brute Force, HeartBleed, Botnet, DoS, DDoS, Web, Infiltration).
*   **CSE-CIC-IDS2018** (2018): Combined with user profiles, 7 attack scenarios.

## Preprocessing
The paper outlines a general AI-based NIDS methodology that includes a **Data Preprocessing phase**. This phase typically involves:
*   **Encoding**: Converting categorical data into numerical format.
*   **Normalization**: Scaling features to a standard range.
*   **Cleaning**: Removing entries with missing data and duplicate entries.

## Evaluation Metrics
The paper explains commonly used evaluation metrics for ML/DL-based IDS, all derived from the Confusion Matrix (True Positive (TP), False Negative (FN), False Positive (FP), True Negative (TN)):
*   **Precision**
*   **Recall (Detection Rate)**
*   **False Alarm Rate (FPR)**
*   **True Negative Rate (TNR)**
*   **Accuracy** (useful for balanced datasets)
*   **F-Measure (F1-score)** (harmonic mean of Precision and Recall)

## Results
*   **Dominance of DL**: Recent trends show a preference for DL-based NIDS (60% of solutions) over purely ML methods (20%) or hybrid (20%), due to their efficiency in learning from large, raw datasets and the advent of GPUs.
*   **Most Frequent Algorithms**: AE, DNN, CNN, and RNN are the most frequently used DL algorithms. RF and SVM are the most used ML algorithms, often in hybrid designs.
*   **Key DL Application**: Autoencoders (AE) are highly utilized for feature extraction and reduction, often combined with ML-based classifiers. This reduces model complexity and training time.
*   **Outdated Datasets**: A significant observation is that 60% of studies still use older datasets like KDD Cup’99 and NSL-KDD, which are not representative of modern network attacks. This limits real-world performance.
*   **Class Imbalance**: Many methodologies show lower detection accuracy for attack types with fewer samples, highlighting the class imbalance problem.
*   **Computational Complexity**: Complex DL models require extensive computational resources and time, posing a trade-off with model complexity.

## Limitations
*   Lack of up-to-date datasets that reflect new attacks for modern networks (e.g., IoT).
*   Lower detection accuracy for low-frequency attack types due to imbalanced datasets.
*   Low performance in real-world environments, as most methods are tested only in labs.
*   High resource consumption by complex models, leading to processing overhead.
*   Many reviewed methodologies struggle with detecting R2L and U2R attacks due to data scarcity.

## Future Work
*   **Efficient NIDS Framework**: Develop frameworks for modern networks (e.g., IoT) that can handle zero-day attacks, frequently update datasets, and continuously train models.
*   **Solutions for Complex Models**: Explore efficient feature engineering to reduce model complexity and resource consumption, or leverage high-performance computing (GPUs, cloud platforms).
*   **Expand DL Algorithm Use**: Investigate less-explored DL algorithms (e.g., deep reinforcement learning, Hidden Markov Models) and hybrid DL for feature extraction with ML for classification.
*   **Efficient NIDS for Cyber-Physical Systems**: Research DL-based NIDS for SCADA networks and UAV-enabled networks.

## Research Gaps Identified
*   Unavailability of systematic, up-to-date, and balanced datasets.
*   Challenges in improving detection accuracy for minority attack classes in imbalanced datasets.
*   Gap between lab-tested performance and real-world deployment efficacy.
*   High computational and resource demands of complex ML/DL models.
*   **Crucial Gap**: Need for lightweight IDS models specifically for resource-constrained IoT environments.

## Relevance to Agricultural IoT IDS
**Foundational and highly relevant**. This systematic review provides an indispensable overview of the state-of-the-art in ML and DL for NIDS, directly informing the context and strategic choices for AgriIoT IDS. It highlights critical challenges (outdated datasets, class imbalance, complexity vs. resources, real-world performance) that are acutely relevant to AgriIoT. The discussion of various ML/DL models (including Random Forest and Autoencoders, which are central to our project) provides a strong foundation. Most importantly, it explicitly identifies the need for **lightweight IDS for IoT** as a major research challenge, reinforcing a core objective of AgriIoT security.
