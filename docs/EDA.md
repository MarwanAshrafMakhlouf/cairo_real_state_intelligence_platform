# Cairo Real Estate Intelligence Platform — EDA Documentation
**Author:** Marwan Ashraf
**Last Updated:** May 2026
**Dataset:** 74,789 listings | 38 columns | 4 market segments
---

## Overview

This document records the findings from the Exploratory Data Analysis phase of the Cairo Real Estate Intelligence Platform project. The goal of this phase was to understand the structure, distributions, and pricing dynamics of the Cairo real estate market before moving into feature engineering and modeling. The analysis covers geographic patterns, price behavior, feature relationships, outlier handling, and feature selection decisions.

The dataset was split into four segments throughout the analysis: apartments for sale, apartments for rent, villas for sale, and villas for rent. This segmentation is intentional — each combination has fundamentally different pricing behavior, and treating them as one population would obscure more than it reveals.

---

## 1. Geographic Distribution

The district variable was the first point of analysis. Listing counts vary enormously across districts, with New Cairo accounting for the largest share by a significant margin. However, listing volume and median price do not move in the same direction.

Districts with fewer listings like Zamalek and New Heliopolis show higher median prices than New Cairo. This is not a paradox — it reflects selection bias in what gets listed there. Only premium properties reach the market in those areas, which pulls the median up, while New Cairo's massive volume includes every price tier from affordable to ultra-luxury, which pulls its median down toward the midpoint of the full distribution.

The geographic hierarchy in the data runs three levels deep: district, area, and neighborhood or compound name. Some areas have enough granularity at the neighborhood level to be useful features; others do not. Neighborhoods within districts like Rehab City had sparse listing counts that were addressed during the scraping phase, not the EDA phase.

A stacked bar chart by district confirmed that villas are geographically concentrated. New Heliopolis and Shorouk City carry the highest villa proportion relative to their total listings. Apartments dominate in virtually every other district.

---

## 2. Property Area Distribution

The area variable (measured in square meters) is strongly right-skewed across the full dataset. Most listings cluster in the 150–200 m² range, and the median remains stable even when extreme values are included, which confirms that the bulk of the market is in a predictable size range.

When split by property type, the distributions diverge meaningfully. Apartments approximate a normal distribution with a relatively tight IQR of 135–185 m². Villas are heavily right-skewed, with a long tail stretching toward 1000 m² and beyond. There is a notable overlap zone between 150 and 300 m² where both types coexist, which means area alone is not a clean separator between apartments and villas in that range.

One important correction was made during this section. A villa listing with a recorded area of 160,000 m² was identified as a data entry error after manual inspection of the original source. The correct value was 160 m², and it was corrected in the dataset at index 57738.

The apartment outlier investigation revealed that large apartments at the top 2% threshold are not data errors. Duplexes, penthouses, and full-floor apartments in Heliopolis, Maadi, and Zamalek are genuinely that large, and dropping them would remove real and important market segments. The property_subtype variable is what actually differentiates these within the apartments category, and it carries pricing implications that area alone does not.

---

## 3. Price Distribution

Price is right-skewed across all four segments, which is expected in any real estate market where a small number of high-value properties create a long upper tail.

The key findings by segment are as follows.

Apartments for sale have a slight right skew with a median around 7.5 million EGP. A meaningful tail of luxury apartments stretches toward 25 million EGP, driven by penthouses and hotel apartments in premium locations.

Villas for sale are highly right-skewed with very high variance. The distribution ranges from roughly 6 million EGP at the lower end to well above 100 million EGP, and the shape of the curve confirms that villa pricing cannot be modeled reliably without strong location and subtype features.

Apartments for rent are unimodal and relatively concentrated around a median of 40,000 EGP per month. The distribution is predictable for most of the market, with a visible right tail of higher-end furnished rentals in premium districts pulling it right.

Villa rentals have a completely different shape — flat, wide, and heavily right-skewed with a median of 120,000 EGP per month. That is three times the apartment rental median, and the tail extends well past 400,000 EGP. These are two fundamentally different rental markets that must be modeled separately.

---

## 4. Outlier Investigation and Manual Review

The top 2% of prices by segment were investigated individually rather than dropped automatically. The goal was to distinguish genuine high-value listings from data entry errors and scraping artifacts.

The findings broke into three categories.

First, confirmed data entry errors that were removed. A villa rental listed at 90 million EGP per month was confirmed as a data entry error from the seller's side and removed. A single apartment rental priced at nearly 1 million EGP per month was also removed after manual inspection. Three extreme sale listings in Downtown Cairo, Al Manial, and Maadi had mean-to-median ratios above 100x, traced back to a single 130 million EGP three-bedroom apartment listing that was clearly a data entry error in each case; these were dropped.

Second, verified real listings that were retained. Properties in Katameya Heights Compound at 150 million EGP+ were confirmed as legitimate ultra-luxury listings after cross-referencing the original source. These remain in the dataset and are handled through the price tier system described in Section 6.

Third, structural market observations. New Cairo dominates listing count but shows a consistently higher mean than median across districts, confirming that a small number of luxury listings inflate the average. Mokattam and Zamalek show the next highest mean-to-median distortion at 4x and 2x respectively, but these are real luxury markets, not errors.

---

## 5. Price vs. Area, Bedrooms, and Bathrooms

The relationship between price and physical size features was examined through scatter plots with regression lines and box plots segmented by bedroom count.

The area-price relationship exists but is weak across all four segments. The most striking illustration of this is the villa sale scatter plot, where a 200 m² villa can cost the same as an 800 m² one. Property subtype and compound name are doing most of the pricing work in that segment, not size. The regression line technically fits but describes very little of the actual variance.

The rental villa segment is the exception — it shows the strongest and most linear area-price relationship of the four, suggesting that villa rentals follow size more predictably than villa sales.

Bedrooms and bathrooms follow the same pattern as area: price increases with bedroom count, but the spread widens significantly at higher counts. Two properties with the same bedroom count can have completely different prices depending on location and finishing. More importantly, bedrooms and bathrooms are capturing the same signal as area. All three are proxies for physical size, and feature selection in the modeling phase will likely drop one or more of them.

---

## 6. Price Tier Engineering

Rather than dropping extreme-value listings as outliers, a price tier feature was engineered to preserve legitimate high-end properties while giving the model a way to treat them differently.

The tiers are defined per segment using within-segment quantiles. Anything below the 90th percentile is labeled standard. The 90th to 95th percentile range is premium. The 95th to 99th percentile range is luxury. Anything above the 99th percentile is ultra_luxury. This means the thresholds differ between, for example, villa sales and apartment rentals, which is correct — a luxury apartment rental and a luxury villa sale represent very different price points in absolute terms.

This approach avoids the information loss of dropping high-value listings while also preventing extreme values from dominating the loss function during regression. The price_tier column will be used as a feature in the model alongside the raw price target.

---

## 7. Price vs. District and Location

The district variable is the dominant price driver in this dataset. After running median price analysis by district and overlaying listing counts, the finding is clear: location explains more price variance than size alone, and this holds across all four segments.

The mean-to-median ratio analysis by district was particularly useful. A ratio close to 1 means the district has a relatively symmetric price distribution. A high ratio means a small number of expensive listings are inflating the mean well above the typical listing price. Outside the few districts with confirmed data errors (cleaned as described in Section 4), the ratio is in the 1 to 4x range for most of the dataset, which is normal for a right-skewed real estate market.

The floor level analysis within apartments added a nuanced finding. For sale apartments, floor level has almost no consistent effect on price — the one spike visible in the chart comes from a single listing at floor 18 and is statistically meaningless. For rental apartments, however, ground floor commands the highest median rent, there is a gradual decline through mid-level floors, and top floor jumps back up with a sample size large enough (n=328) to be reliable. This reflects the Cairo rental market preference for ground floor access and private gardens, and top floor views and privacy, with middle floors being the undifferentiated standard.

---

## 8. Price vs. Property Subtype

Property subtype is the second most important price driver after district, and the KDE analysis by subtype makes this concrete.

For apartment sales, Studio and Roof subtypes cluster around a median of 4 million EGP, regular Apartment sits at 7.3 million, and Penthouse and Hotel Apartment are clearly in a different league at 11 to 12 million EGP. There is heavy overlap between Apartment and Duplex, but Penthouse is well separated enough to be treated as its own segment. The width of each subtype's distribution also carries information — Studio has a tall narrow peak indicating a standardized product, while Penthouse and Hotel Apartment have wide flat distributions indicating that two listings with the same subtype can be priced very differently depending on location.

For apartment rentals, Hotel Apartment is the outlier in the opposite direction — its low median of 6,000 EGP per month reflects short-term furnished unit pricing, which is a completely different product from a standard rental. Studio shows a bimodal distribution with two distinct humps, almost certainly separating cheap unfurnished studios from expensive furnished ones in premium locations. The model will need furnishing status and district to properly separate these two groups.

For villa sales, iVilla is the cheapest and most standardized subtype with a tight peak at a median of 14.75 million EGP. Stand Alone Villa, by contrast, has the widest and flattest distribution of any subtype in the analysis, stretching from mid-tier all the way to 100 million EGP. The contrast between these two curves is the clearest signal in the entire subtype analysis that the same subtype label can represent very different pricing realities.

For villa rentals, iVilla again behaves as a standardized product. Town House, Twin House, and Stand Alone Villa distributions overlap heavily in the 100 to 200 thousand EGP range, meaning subtype alone will not cleanly separate them in the rental market. Geographic features will need to carry most of the weight there.

---

## 9. Correlation Matrix and Feature Leakage

The numerical feature correlation matrix confirmed several expected and one critical finding.

Deposit and insurance are the highest-correlated features with price at 0.83 and 0.79 respectively. However, both are calculated as a fraction of the property price after it is set — they are derived from the target variable, not independent of it. Including them in the feature matrix would be data leakage. Both will be dropped entirely before modeling.

Area, bedrooms, and bathrooms are all legitimately correlated with price in the 0.52 to 0.69 range, which confirms they are valid features. However, bedrooms and bathrooms correlate with each other at 0.81, and all three correlate heavily with area. All three are proxies for property size, and feature selection will determine whether one or more can be dropped without meaningful loss of information.

---

## 10. Missing Value Analysis

Missing values were examined at the segment level rather than globally, because several columns are missing by design rather than at random.

Rental_frequency is only meaningful for rental listings. Payment_option and completion_status are only meaningful for sale listings. Evaluating their global missingness rates makes them look severely incomplete, but within their relevant segments the rates are acceptable and follow a structural logic tied to the property type.

The handling plan for each column is as follows. Deposit and insurance will be dropped entirely — data leakage and 95% missing, with nothing to salvage. Furnished and ownership have genuine missingness of 16 to 20% within their relevant segments and will be filled with an unknown category during preprocessing. Delivery_term will be converted to a binary is_offplan feature, since its missingness itself carries the signal — a null means the property is not off-plan.

The floor level (level_clean) column has high missingness for villas, which is expected since floor level is a meaningful concept almost exclusively for apartments. The district-level breakdown of level_clean missingness for apartments showed that some districts report floor level reliably while others rarely do, which will inform how the feature is handled during preprocessing.

Maids room and elevator will be dropped. Both show near-zero or near-100% distributions across all segments, which means they carry almost no discriminative signal for the model.

---

## 11. Categorical Amenity Analysis

A binary amenity heatmap across all four segments revealed which features carry useful variation and which do not.

Pets allowed, balcony, and private garden show the strongest variation across segments and are worth including as features. Notably, pets allowed drops to 33% for rental apartments — significantly lower than other segments — likely reflecting landlord restrictions rather than tenant preferences. Private garden skews toward villas at 65 to 67% compared to 44 to 48% for apartments, which is consistent with the physical reality of villa properties.

Maids room, elevator, and pool show near-zero or heavily one-sided distributions across all segments, meaning they carry almost no signal for distinguishing one property from another. These will be dropped during preprocessing.

---

## 12. Feature Engineering and Preprocessing Decisions

The following decisions were made during or as a result of the EDA, and will be implemented in the preprocessing phase before modeling.

Columns to drop: deposit, insurance (data leakage), maids room, elevator (near-zero variance).

Columns to engineer: delivery_term will become a binary is_offplan flag. Price tiers (standard, premium, luxury, ultra_luxury) will be retained as a derived feature computed per segment using within-segment quantiles.

Missing value strategy: segment-aware imputation for furnished, ownership, and similar columns. Unknown category fill where genuine missingness exists. Structural nulls treated as a feature value, not as missing data.

Model architecture: four separate models split by property_type and sale_or_rent. This is justified by the distinct pricing behavior, different relevant features, and different distributional shapes observed across each segment throughout the EDA.

---

## Summary of Key Findings

The dataset contains 74,789 listings split across four segments, each with distinct pricing behavior that justifies the planned four-model architecture.

District is the dominant price driver across all segments, explaining more price variance than physical size alone. New Cairo dominates listing volume but Zamalek and New Heliopolis command higher median prices because of the selective nature of what gets listed there.

Property subtype is the second most important driver within each property type. The contrast between iVilla (standardized, predictable) and Stand Alone Villa (highly variable, location-dependent) is the clearest example of how much pricing information is encoded in this variable.

Area, bedrooms, and bathrooms are valid features but highly inter-correlated. All three are proxies for physical size, and one or more may be dropped during feature selection without meaningful performance loss.

Sale prices are strongly right-skewed across both property types. Rental prices are similarly skewed, with villa rentals showing three times the median price and far greater variance than apartment rentals. Price tiers were engineered to preserve legitimate high-value listings without allowing extreme values to dominate the model.

Deposit and insurance will be dropped as data leakage. Missing values in rental_frequency, payment_option, completion_status, and delivery_term are structural and by design, not random — each will be handled appropriately in the preprocessing phase using segment-aware logic.