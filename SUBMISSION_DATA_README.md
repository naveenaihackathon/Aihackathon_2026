# RepSense AI Hackathon Sample Data Bundle

This bundle contains separate sample input and output folders for submission.

## Folder Structure

```text
input/
└── pharma-data_sample.csv                 # 1,000 representative sales transactions

output/
├── AI_rep_management_output_sample.csv    # Main territory risk output
├── rep_master_hr_sample.csv               # Representative and vacancy data
├── crm_activity_detail_sample.csv         # CRM activity data
├── promotional_activity_sample.csv        # Promotional activity data
├── executive_dashboard_sample.csv        # Executive summary output
└── critical_territories_sample.csv        # Critical territory filter
```

## Input Sample

`input/pharma-data_sample.csv` is a representative 1,000-row sample extracted from the source `pharma-data.csv` file. It preserves the original 18-column transaction schema:

- Distributor and customer
- City, country, latitude, and longitude
- Channel and sub-channel
- Product and product class
- Quantity, price, and sales
- Month and year
- Sales representative, manager, and sales team

## Output Sample

`output/AI_rep_management_output_sample.csv` is the generated main output. It contains territory-level risk analysis with:

- Sales and trend metrics
- CRM activity and HCP coverage
- Current, required, and vacant representatives
- Isolation Forest score
- Local Outlier Factor score
- Ensemble anomaly score
- Business-rule risk scores
- Final risk score from 0 to 100
- Severity classification
- Risk reasons
- AI recommendation

## Supporting Outputs

The additional files demonstrate the operational data layers and summary outputs used by the dashboard:

- `rep_master_hr_sample.csv`: HR and staffing information
- `crm_activity_detail_sample.csv`: CRM calls, visits, and activity metrics
- `promotional_activity_sample.csv`: promotions and observed sales uplift
- `executive_dashboard_sample.csv`: aggregate management KPIs
- `critical_territories_sample.csv`: filtered Critical territory records

## Important Note

The HR, CRM, and promotional files are reproducible demonstration layers generated with random seed 42. The main output currently contains eight territory-date records because the current demo processing path has one effective analysis date. In production, these files should be replaced with connected enterprise data sources and a complete multi-period history.

## Run the Full Project

```powershell
cd c:\Users\shalini.raj\Downloads\pharma-data.csv
pip install -r requirements.txt
python pipeline.py
streamlit run app.py
```
