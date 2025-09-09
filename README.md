AI-DRIVEN TRAIN INDUCTION PLANNING & SCHEDULING FOR KOCHI METRO RAIL LIMITED (KMRL)




  KMRL Induction Planner – AI-Based Scheduling and Optimization Tool

The AI-Driven Dynamic Induction Scheduler is a prototype AI-based tool designed to optimize induction schedules for new KMRL employees. It leverages constraint-based optimization to generate efficient, conflict-free schedules while considering employee availability, training sessions, and other logistical constraints.

🚀 Features

Automated Schedule Generation: Create optimized induction schedules quickly.

Custom Constraints: Supports scheduling based on session duration, availability, and capacity.

Interactive Dashboard: Visualize schedules and planning data (frontend prototype).

Sample Data Support: Test the system with provided sample datasets.

API Access: Backend provides endpoints to ingest data and run optimizations.

🧩 Problem Statement

Managing induction sessions for KMRL employees is challenging due to multiple constraints like training session overlap, employee availability, and resource allocation. Manual planning is time-consuming and prone to errors. The AI-Driven Dynamic Induction Scheduler automates this process using AI-driven optimization to generate feasible and efficient schedules.

🛠️ Technology Stack

Backend: Python, FastAPI

Frontend: React (dashboard prototype)

Optimization Engine: Python-based constraint solver

Data: CSV/JSON input files for employee & session details

⚙️ Setup & Installation

Clone the repository:

git clone https://github.com/<your-username>/kmrl-induction-planner.git
cd kmrl-induction-planner


Create a virtual environment and activate it:

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Run the backend server:

uvicorn backend.main:app --reload


Open the frontend dashboard (if applicable) to interact with the schedules.

📁 Project Structure
kmrl-induction-planner/
├── backend/           # FastAPI backend code
├── dashboard/         # Frontend React dashboard prototype
├── data_samples/      # Sample datasets for testing
├── gen_samples.py     # Script to generate sample data
├── README.md
├── requirements.txt
└── .gitignore

🔗 API Endpoints

GET /
Returns a message confirming the API is running.

GET /ingest/{filename}
Ingests a sample data file for processing.

GET /run-optimizer
Runs the AI optimization engine and returns a proposed schedule.

📊 Sample Usage
from backend.optimizer.model import run_optimizer

# Run optimization on sample data
schedule = run_optimizer("data_samples/sample_employees.csv")
print(schedule)

🤝 Contributing

Contributions are welcome! Please create a pull request or raise an issue for suggestions, bug fixes, or feature requests.
