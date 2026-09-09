# Patient Health Analytics System

## Project Overview

The Patient Health Analytics System is a Python-based application developed to analyse patient health data and provide useful insights from a healthcare dataset.

The system allows users to load patient data, perform statistical analysis, run different health-related queries, filter patient records, view results through a graphical user interface, and export results to CSV files.

## Features

- Load patient health data from a CSV file
- Perform descriptive statistical analysis
- Calculate mean, median, mode, standard deviation, minimum, maximum, variance, and range
- Perform different patient health-related queries
- Filter patient records based on selected conditions
- Analyse relationships between health conditions and lifestyle factors
- Analyse stroke-related health information
- Display results using a Tkinter graphical user interface
- Handle invalid inputs using exception handling
- Export query results to CSV files

## Technologies Used

- Python
- Pandas
- NumPy
- Tkinter
- CSV
- Object-Oriented Programming (OOP)
- Exception Handling
- Visual Studio Code

## Project Structure

```text
Patient-Health-Analytics-System/
│
├── data.csv
├── load_dataset_module.py
├── main.py
├── query_module.py
├── statistics_module.py
├── user_interface_module.py
└── README.md

How to Run
1. Clone the repository
git clone https://github.com/GilkapallyRithika/Patient-Health-Analytics-System.git
2. Open the project folder
cd Patient-Health-Analytics-System
3. Install the required libraries
pip install pandas numpy
4. Run the application
python main.py
