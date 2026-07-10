# Insights Summary

This summary is based on the PostgreSQL load checked on 2026-07-02.

## Data Coverage

- Demand data: 2024-01-01 to 2026-06-30
- Generation data: 2024-01-01 to 2026-06-30
- DA-OZP price data: 2026-04-02 to 2026-06-30
- Demand rows loaded: 21,887
- Generation rows loaded: 142,248
- Price rows loaded: 2,160

One demand hour is missing in the raw IESO demand file: 2025-05-01 HE 1. I did not fill it because this project should not invent source data.

## Main Findings

1. Average Ontario demand in the loaded period is about 16,384 MW. Peak demand is 24,862 MW on 2025-06-24 at HE 19.

2. The highest average demand months are winter and summer months. January 2026 has the highest average monthly demand in the loaded period, and July 2025 is also very high.

3. Demand is highest in evening hours. The top average demand hours are HE 18, HE 19, HE 20, and HE 17.

4. Average generation is about 18,382 MW. Renewable share is about 32.9%, non-emitting share is about 82.1%, and gas share is about 17.8%.

5. For the available DA-OZP price period, average price is $38.62/MWh and price volatility is 21.17. The max price is $233.14/MWh on 2026-06-30 HE 20.

6. During the available DA-OZP price period, price has a strong positive correlation with demand, about 0.775. Price also has a positive correlation with gas share, about 0.681, and a negative correlation with renewable share, about -0.428.

7. The highest market stress hours are mostly around late June 2026, especially 2026-06-30 evening hours. These combine high demand, high price, high gas share, and lower renewable share.

## Dashboard Story

The dashboard should tell a simple story:

- Ontario demand has clear seasonal and hourly patterns.
- Supply mix is mostly non-emitting, with gas becoming more important during some high-demand periods.
- The available DA-OZP price data shows price is associated with demand and gas share.
- Market stress hours are not official IESO events, but the exploratory score is useful for ranking hours that need attention.














