# Paper Summary: Panigrahi

-   **BibTeX Key**: Panigrahi
-   **Title**: A detailed analysis of CICIDS2017 dataset for designing Intrusion Detection Systems
-   **Authors**: Ranjit Panigrahi and Samarjeet Borah
-   **Year**: 2024 (Inferred from prompt)
-   **Publication Venue**: International Journal of Engineering & Technology

---

## Research Objective
To provide a detailed analysis of the CICIDS2017 dataset, identify its inherent shortcomings that can bias the detection engine of typical Intrusion Detection Systems (IDS), and propose effective solutions to mitigate these issues for improved classification and detection performance in future IDS designs.

## Problem Addressed
While many IDS models claim high accuracy, few are adopted by industries, often due to issues with training and testing datasets. The CICIDS2017 dataset, despite being modern and comprehensive, contains several major shortcomings (scattered presence across multiple files, huge data volume, missing values, and high class imbalance) that can negatively impact the reliability and effectiveness of IDS models trained upon it. These issues hinder its full potential as a benchmark for true intrusion detection.

## Methodology
The study conducted a detailed examination and analysis of the CICIDS2017 dataset.
1.  **Dataset Acquisition and Merging**: The CICIDS2017 dataset, originally scattered across eight files (representing five days of traffic data), was merged into a single comprehensive dataset. This merged dataset initially contained 3,119,345 instances and 83 features, with 15 class labels (1 normal + 14 attack labels).
2.  **Missing Value Handling**: Instances with missing class labels (288,602 records) and other missing information (203 records) were identified and removed. This resulted in a combined dataset of 2,830,540 unique instances.
3.  **Redundancy Check**: After removing missing values, the dataset was queried for possible redundant instances, and surprisingly, none were found.
4.  **Shortcoming Identification**: Based on this initial processing, four key shortcomings were identified:
    *   **Scattered Presence**: Data distributed across multiple files.
    *   **Huge Volume of Data**: Large dataset size, consuming overhead for loading and processing.
    *   **Missing Values**: Significant number of instances with missing information.
    *   **High Class Imbalance**: Dominance of the benign class over various minority attack classes.
5.  **Proposed Solutions**:
    *   **Addressing Scattered Presence**: Achieved by merging the eight files into a single dataset.
    *   **Addressing Missing Values**: Achieved by removing the identified instances with missing information.
    *   **Addressing Huge Volume**: Suggested this can be overcome by judicious sampling, but emphasized that class imbalance must be addressed *before* sampling.
    *   **Addressing High Class Imbalance**: Proposed a **relabeling strategy**. This involved merging several minority attack classes that shared similar characteristics and behaviors to form new, broader attack classes. This improves the prevalence ratio of minority classes.
        *   **New Labels**: Normal, Botnet, Brute Force, Dos/DDos, Infiltration, PortScan, Web Attack.
        *   For example, 'DoS Hulk', 'DoS GoldenEye', 'DoS Slowhttptest', 'DoS slowloris', and 'Heartbleed' were merged into a single 'Dos/DDos' class.

## ML Models Used
Not applicable. This paper is a dataset analysis and preprocessing study, not an evaluation of machine learning models.

## Datasets Used
**CICIDS2017 dataset**: The core of this analysis. The study uses its full, combined form of 2,830,540 instances and 83 features.
*   **Original 15 Class Labels**: BENIGN, DoS Hulk, PortScan, DDoS, DoS GoldenEye, FTP-Patator, SSH-Patator, DoS slowloris, DoS Slowhttptest, Bot, Web Attack – Brute Force, Web Attack – XSS, Infiltration, Web Attack – Sql Injection, Heartbleed.
*   **Proposed 7 New Labels**: Normal, Botnet, Brute Force, Dos/DDos, Infiltration, PortScan, Web Attack.

## Preprocessing
*   **Merging Files**: Combined eight `.csv` files into one.
*   **Missing Value Removal**: Filtered out instances with missing class labels or information.
*   **Relabeling**: Merged minority attack classes to reduce class imbalance.

## Evaluation Metrics
Not applicable to model performance. The paper uses prevalence ratios and percentages to describe class distribution and imbalance.

## Results
*   **Original Shortcomings**: Confirmed scattered data, huge volume, missing values, and severe class imbalance in CICIDS2017.
*   **Class Imbalance (Original)**: The benign class constituted 83.344% of the dataset, while minority classes like Heartbleed were as low as 0.00039%. This significant imbalance can bias detectors towards the majority class.
*   **Relabeling Effectiveness**: The proposed relabeling strategy significantly improved the prevalence ratio of all attack labels, thereby reducing the class imbalance. For example, the lowest minority class prevalence improved from 0.00039% to 0.001% (relative to total instances).
*   **Improved Dataset Characteristics**: The new labels (Normal, Botnet, Brute Force, Dos/DDos, Infiltration, PortScan, Web Attack) better represent the attack categories and mitigate the imbalance problem.

## Limitations
*   The study focuses exclusively on the analysis and preprocessing of the CICIDS2017 dataset, not on the performance of specific machine learning models.
*   The relabeling strategy, while improving balance, still results in some degree of class imbalance; it does not achieve perfect balance.
*   The paper does not provide empirical results of IDS models trained on the relabeled dataset.

## Future Work
The authors suggest that the relabeled dataset can be class-wise resampled to generate separate training and testing sample sets for further use by the research community.

## Research Gaps Identified
*   The lack of perfectly clean, unified, and balanced benchmark datasets for IDS research.
*   The inherent issues (scattered data, missing values, severe class imbalance) in widely used benchmark datasets like CICIDS2017 that can significantly bias ML models.
*   The need for effective strategies to manage and mitigate class imbalance in IDS datasets.

## Relevance to Agricultural IoT IDS
**Crucially relevant**. This paper provides a foundational understanding of the **CICIDS2017 dataset's inherent characteristics and flaws**, which is the primary dataset used in our project. The detailed analysis of issues like scattered data, missing values, and especially **high class imbalance**, directly informs the preprocessing steps and interpretation of results for any ML model trained on CICIDS2017. The proposed **relabeling strategy** to combat class imbalance is a vital methodological contribution, particularly for AgriIoT IDS, where attack data is inherently rare and highly imbalanced. This paper's insights are essential for ensuring that ML models for AgriIoT are trained on appropriately prepared data and that their performance is correctly evaluated, preventing bias towards benign traffic.
