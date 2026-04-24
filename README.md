# HR Workforce Analytics

![CI](https://github.com/Djones-qa/hr-workforce-analytics/actions/workflows/hr-tests.yml/badge.svg)

Comprehensive HR workforce analytics framework using Python, Pandas, Scikit-learn, Matplotlib, and SQLite. Covers employee attrition analysis, salary equity, performance metrics, workforce diversity, attrition risk prediction, and SQL HR investigation queries.

## Why HR Analytics Matters
People data drives strategic business decisions:
- Attrition prediction saves thousands in replacement costs
- Salary equity analysis ensures fair compensation practices
- Performance metrics identify high performers and gaps
- Diversity metrics support inclusive workforce strategies
- Risk scoring enables proactive retention interventions

## Tech Stack
- Python 3.x
- Pandas — data manipulation and workforce analysis
- NumPy — numerical calculations
- Matplotlib + Seaborn — HR dashboard visualizations
- Scikit-learn — attrition risk scoring
- SQLite — SQL HR investigation queries
- Pytest — test execution and fixtures
- GitHub Actions CI

## Project Structure
`
hr-workforce-analytics/
├── scripts/
│   ├── data_generator.py    # Employee, review, training data generation
│   ├── analytics.py         # Attrition, equity, performance, diversity
│   └── visualizations.py    # HR dashboard charts
├── tests/
│   ├── test_data_generation.py  # Data quality tests
│   ├── test_analytics.py        # Analytics accuracy tests
│   └── test_visualizations.py   # Chart generation tests
├── data/                    # Generated CSV and SQLite datasets
├── visuals/                 # Generated PNG dashboard charts
├── conftest.py
├── pytest.ini
├── requirements.txt
└── .github/workflows/
    └── hr-tests.yml
`

## Analytics Covered

### Attrition Analysis
- Overall attrition rate
- Attrition by department, job level
- Attrition reasons breakdown
- Tenure analysis for attrited vs retained

### Salary Equity
- Salary by gender and job level
- Department salary gap analysis
- Min, max, average by demographic

### Performance Metrics
- Average performance by department
- Satisfaction vs performance correlation
- Training hours and effectiveness
- Absenteeism and overtime analysis

### Workforce Diversity
- Gender distribution overall and in leadership
- Race and ethnicity breakdown
- Education level distribution
- Remote work adoption rate

### Attrition Risk Prediction
- Composite risk score per employee
- Risk factors — satisfaction, performance, absences, overtime
- Risk levels — Low, Medium, High

## SQL Investigation Queries
- Attrition rate by department with avg salary
- Salary by gender and job level
- Top 20 performers
- Attrition reasons with avg tenure
- Remote work impact on satisfaction and attrition
- Training effectiveness by department

## Charts Generated
1. Attrition Rate by Department
2. Salary Distribution by Gender and Job Level
3. Performance Score Heatmap
4. Attrition Reasons
5. Tenure Distribution — Stayed vs Attrited
6. Satisfaction vs Performance Scatter
7. Workforce Diversity Breakdown
8. Attrition Risk Distribution

## Run Tests
`ash
pip install -r requirements.txt
python -m pytest tests/ -v
`

## Author
Darrius Jones - github.com/Djones-qa