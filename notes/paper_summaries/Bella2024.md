# Paper Summary: Bella2024

-   **BibTeX Key**: Bella2024
-   **Title**: An efficient intrusion detection system for IoT security using CNN decision forest
-   **Authors**: Kamal Bella, Azidine Guezzaz, Said Benkirane, Mourade Azrour, Yasser Fouad, Mbadiwe S. Benyeogor, and Nisreen Innab
-   **Year**: 2024
-   **Publication Venue**: PeerJ Computer Science

---

## Research Objective
To present a novel intrusion detection approach, the Deep Neural Decision Forest-based IDS (DNDF-IDS), aimed at enhancing network anomaly detection in IoT ecosystems. The study focuses on achieving high accuracy, reducing computational resources, and expediting prediction times by using significantly fewer features while maintaining interpretability.

## Problem Addressed
The widespread adoption and integration of IoT devices make them prime targets for malicious attacks, making IoT security a crucial research area. Highly accurate IDS models often rely on an extensive number of features, leading to high resource consumption and prolonged prediction times, which are problematic for real-time applications in resource-constrained IoT environments. Furthermore, the integration of neural networks and decision trees for structured data classification is underexplored, and traditional CNNs are not optimized for structured data.

## Methodology
The study proposes a **DNDF-IDS model** with five core components: Data Source, Preprocessing Module, Feature Reduction Module, Decision Module, and Response Module.
*   **Data Source**: Labeled network traffic records (safe or threats).
*   **Preprocessing**: Interquartile Range (IQR) method for outlier identification and removal to enhance data quality. Data preparation, cleaning, and encoding.
*   **Feature Reduction (Feature Selection)**: Four distinct feature selection methods are applied separately to retain only the **top 10 performing features**.
    *   **Principal Component Analysis (PCA)**: Reduces dimensionality by transforming features into orthogonal components based on variance.
    *   **SelectKBest**: Selects top K features based on statistical tests (e.g., ANOVA, Chi-squared).
    *   **LASSO Regression (LR)**: L1 regularization that forces some coefficients to zero, effectively selecting features and promoting sparsity.
    *   **Random Forest Feature Importance (RFFI)**: Measures feature importance based on impurity reduction in Random Forest decision trees.
*   **Classification Model**: **Deep Neural Decision Forest (DNDF)**.
    *   Combines classification trees and Convolutional Neural Networks (CNNs). It replaces the softmax layer of a typical CNN with decision forests (an ensemble of decision trees).
    *   **Architecture**: Shares fully-connected and convolutional layers with CNNs. Decision tree nodes utilize feature representations learned from the fully-connected layer.
    *   **Decision Tree Parameters**: Depth: 5 (allowing 32 leaf nodes), Used features rate: 1 (100% of features used randomly per tree).
    *   **Decision Forest Parameters**: Number of trees: 50 (in the ensemble).
    *   **Training Parameters**: Learning rate: 0.03, Batch size: 128, Number of epochs: 20.
*   **Experimental Environment**: Google Colab (1 vCPU AMD EPYC 7B12 @ 2.2 GHz, 12.7 RAM, Linux 5.15.120+), Python v3.10.12.
*   **Evaluation**: The model was evaluated on three diverse benchmark datasets (NSL-KDD, CICIDS2017, UNSW-NB15) and compared against other recent Random Forest and CNN-based models.

## ML Models Used
*   **Deep Neural Decision Forest (DNDF)**: Hybrid of CNN and Decision Forests.
*   **Feature Selection Methods**: Principal Component Analysis (PCA), LASSO Regression (LR), SelectKBest, Random Forest Feature Importance (RFFI).
*   **Comparison Models**: Random Forest, CNN.

## Datasets Used
*   **NSL-KDD**: Balanced and improved version of KDD Cup 99, with 41 features and various attacks (DoS, Probe, R2L, U2R).
*   **CICIDS2017**: Comprehensive and modern benchmark unbalanced dataset, over 2.8 million records with over 80 features, diverse attacks (DoS, DDoS, Probe, U2R).
*   **UNSW-NB15**: Unbalanced dataset with over 2.5 million instances and 47 features, representing benign and malicious activities.

## Preprocessing
*   **Outlier Removal**: Interquartile Range (IQR) method.
*   **Data Cleaning and Encoding**: General data preparation to improve quality.
*   **Feature Selection**: Reduction to the 10 best-performing features using PCA, SelectKBest, LR, and RFFI.

## Evaluation Metrics
*   Accuracy (ACC)
*   Precision (PR)
*   True Positive Rate (TPR)
*   False Positive Rate (FPR)
*   F1 Score
*   Prediction Time (s for entire test set, ms per record)

## Results
*   **High Accuracy with Minimal Features**: DNDF-IDS achieved impressive ACC values:
    *   NSL-KDD: 94.26% to 98.38% (PCA best).
    *   CICIDS2017: 94.09% to 98.84% (PCA best).
    *   UNSW-NB15: 97.10% to 98.23% (PCA best).
    *   All results achieved using **only the top 10 features**.
*   **Fast Prediction Time**: The model achieved an average prediction time of approximately **0.1 ms per record**, demonstrating high efficiency.
*   **PCA's Effectiveness**: PCA consistently yielded the highest accuracy across two out of three datasets (NSL-KDD, CICIDS2017) and was second best for UNSW-NB15 by a small margin, emphasizing its importance in dimensionality reduction.
*   **DNDF Superiority**: Ablation experiments showed that DNDF with 10 features and IQR preprocessing achieved an optimal balance of high accuracy (98.38% for NSL-KDD) and computational efficiency (6.27s prediction time for entire NSL-KDD test set). DNDF outperformed standalone Random Forest and CNN models in accuracy and interpretability.
*   **Resource Efficiency**: The model effectively reduced computational burden by focusing on the most informative features, outperforming some existing models that relied on all features.

## Limitations
*   Theoretical limitations related to model design assumptions or simplifications in the base algorithms are acknowledged.
*   Practical limitations could include constraints related to computational resources or dataset attributes in real-world scenarios.
*   Scalability and adaptability to a wider range of network environments and evolving threat landscapes still require further examination.

## Future Work
*   Refine and enhance the solution to further improve detection capabilities and reduce computational costs.
*   Examine the scalability and adaptability of the method to various network environments and evolving threat landscapes for broader real-world applicability.

## Research Gaps Identified
*   Underexplored integration of neural networks and decision tree-based models for structured data classification.
*   The problem of highly accurate models relying on extensive features, leading to high resource usage and extended prediction times, especially for real-time IoT applications.
*   Lack of empirical evaluations and optimization studies for neural decision forests on structured data.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper proposes an efficient and lightweight IDS (DNDF-IDS) that achieves high accuracy with a significantly reduced number of features (top 10) and extremely fast prediction times (0.1 ms per record). These characteristics are paramount for AgriIoT environments, which are typically resource-constrained, require real-time threat detection, and often deal with structured sensor data. The comprehensive evaluation across multiple benchmark datasets, including CICIDS2017, and the detailed comparison of various feature selection methods (PCA, LR, SelectKBest, RFFI) provide direct and valuable insights for designing and optimizing AgriIoT IDS, particularly in balancing performance with resource efficiency.
