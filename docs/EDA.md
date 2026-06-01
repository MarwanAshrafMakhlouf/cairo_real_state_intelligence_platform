# Cairo Real Estate Dataset - Exploratory Data Analysis Documentation

## Overview

This document summarizes the exploratory data analysis performed on the Cairo real estate dataset. The objective was to understand data quality, distribution characteristics, pricing behavior, geographic patterns, feature relationships, and implications for downstream modeling.

## Objectives

- Assess dataset structure and completeness.
- Understand geographic distribution of listings.
- Analyze property attributes and their distributions.
- Investigate pricing behavior across sale and rental markets.
- Identify and review extreme values and outliers.
- Evaluate feature relationships with price.
- Assess missing data impact.
- Identify features suitable for modeling and features that should be removed.

## Dataset Preparation

### Initial Validation

The dataset was loaded from a cleaned parquet source and inspected using:

- Dataset structure review.
- Data type validation.
- Column inventory review.

## Geographic Distribution Analysis

### District Distribution

Listing counts were analyzed across districts to understand market representation.

Key observations:

- Listing volume is highly concentrated in a small number of districts.
- New Cairo represents a substantial portion of the dataset.
- Several districts have relatively limited representation.
- Distribution imbalance should be considered during modeling and evaluation.

## Interactive Attribute Exploration

Interactive exploration was performed for categorical and numerical attributes to understand:

- Distribution patterns.
- Category frequency.
- Potential data quality issues.
- Feature variability.

## Area Distribution Analysis

### Overall Distribution

Property area exhibits strong right-skewness.

Key findings:

- Most properties fall within a moderate size range.
- A small number of properties have extremely large areas.
- Large properties create a long upper tail.

### Property Type Comparison

Area distributions were reviewed by property subtype.

Key findings:

- Apartments generally occupy smaller area ranges.
- Villas occupy substantially larger ranges.
- Property subtype strongly influences area distribution.

### Data Corrections

Manual review identified at least one extreme area value caused by a source-entry error.

Actions taken:

- Source verification was performed.
- Incorrect values were corrected before further analysis.

## Price Distribution Analysis

### Overall Price Distribution

Price distributions are strongly right-skewed.

Key findings:

- Most listings are concentrated in lower and middle price ranges.
- A small number of premium properties create long upper tails.
- Mean values are significantly influenced by extreme observations.

### Sale and Rental Markets

The dataset contains both sale and rental listings.

Key findings:

- The two markets exhibit distinct pricing behavior.
- Combined analysis introduces multimodal distributions.
- Segment-specific analysis is required for accurate interpretation.

## Outlier Investigation

### Extreme Price Review

A detailed review of the most extreme observations was performed.

Objectives:

- Determine whether extreme values are valid.
- Identify data-entry issues.
- Decide on appropriate treatment strategies.

### Findings

The investigation identified multiple scenarios:

- Legitimate luxury properties.
- Potential listing errors.
- Unusual rental listings.
- Market-specific extreme cases.

### Outcome

Outliers were not removed blindly.

Each case was evaluated individually before making treatment decisions.

## Price Tier Engineering

Price segmentation was introduced to improve interpretability.

### Approach

Separate price tiers were created for relevant price categories.

Purpose:

- Reduce sensitivity to extreme values.
- Improve comparative analysis.
- Support future modeling and business reporting.

## Price Versus Area Analysis

Scatter plot analysis was conducted to evaluate the relationship between area and price.

Key findings:

- Larger properties generally command higher prices.
- Variance increases as area increases.
- Area alone is insufficient to explain pricing behavior.
- Location and property type remain major pricing drivers.

## Price Versus Bedroom Count

Bedroom count was evaluated against price.

Key findings:

- Price generally increases with bedroom count.
- Dispersion grows at higher bedroom counts.
- Bedroom count contributes useful information but is not a dominant standalone predictor.

## Price Versus Location

District-level pricing comparisons were performed.

Key findings:

- Significant geographic pricing differences exist.
- New Cairo consistently appears among the higher-priced markets.
- Mean prices often exceed medians, indicating high-end market influence.

## Price Versus Property Subtype

Pricing behavior was analyzed by property subtype.

Key findings:

- Property subtype is a major determinant of price.
- Apartments and villas exhibit substantially different price structures.
- Separate treatment may be beneficial during modeling.

## Correlation Analysis

A correlation matrix was used to identify relationships among numerical variables.

### Findings

- Deposit and insurance variables showed very high correlation with price.
- These variables represent information derived from pricing and create leakage risk.
- Strong correlations should not automatically be interpreted as predictive value.

### Decision

Leakage-prone variables should be excluded from predictive modeling.

## Missing Value Analysis

Missingness was evaluated for all major features.

### Findings

- Some variables contain extremely high missing rates.
- Missingness patterns vary significantly across features.
- Certain features provide limited practical value due to sparse coverage.

### Decisions

Features with excessive missingness or leakage concerns should be removed from modeling pipelines.

Examples include:

- Deposit.
- Insurance.

## Floor-Level Analysis

Floor level was evaluated as a potential price driver.

Key findings:

- Limited consistent pricing impact was observed.
- Most floor levels show similar median pricing behavior.
- Predictive value appears relatively weak.

## Categorical Feature Analysis

Categorical variables were reviewed individually.

### Findings

Several features showed minimal variation or weak relationship with price.

Examples:

- Maid's room.
- Elevator.
- Pool.

### Decision

Features with minimal signal or highly skewed distributions should be considered for removal.

## Final Recommendations

### Retain

Features likely to provide modeling value:

- Price.
- Area.
- District.
- Property subtype.
- Bedroom count.
- Other high-coverage structural property attributes.

### Remove

Features identified as problematic:

- Deposit.
- Insurance.
- Features exhibiting severe missingness.
- Features demonstrating data leakage.
- Features with near-zero informational value.

### Modeling Considerations

- Separate sale and rental markets where appropriate.
- Use robust methods for handling skewed distributions.
- Apply outlier-aware modeling approaches.
- Consider location-based feature engineering.
- Evaluate interaction effects between area, location, and property subtype.

## Conclusion

The analysis confirms that Cairo real estate prices are primarily driven by location, property subtype, and property size. The dataset contains significant skewness, localized market behavior, and a small number of extreme observations that require careful treatment. Several variables introduce leakage or provide limited predictive value and should be excluded from downstream modeling efforts.
