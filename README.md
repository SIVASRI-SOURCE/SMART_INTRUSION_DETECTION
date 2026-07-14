# SMART INTRUSION DETECTION

AI-powered honeypot project for simulating attacks and monitoring suspicious activity in a simple web-based interface.

## Overview
This project combines a Streamlit-based frontend with a honeypot simulation module to demonstrate intrusion detection concepts. It can simulate common attack patterns such as port scans, brute force attempts, URL scanning, and DDoS-like traffic while logging activity for analysis.

## Features
- Streamlit web interface for user login and signup
- Honeypot simulation for attack scenarios
- Logging of detected activity
- Basic alert email support using environment variables
- Local SQLite database for user accounts

## Project Structure
- Sourcecode/app.py - Main Streamlit application with login and signup flow
- Sourcecode/app1.py - Honeypot simulation and alert handling
- Sourcecode/honeypot_simulator.py - Simulation logic
- Sourcecode/honeypot_simulator1.py - Additional simulation logic
- Sourcecode/Background - Static assets used by the UI

## Requirements
Recommended environment:
- Windows 10
- Python 3.11
- 8 GB RAM or more

Install dependencies:
```bash
pip install tensorflow keras streamlit
```

## Setup
1. Open the project folder.
2. Create a virtual environment if needed.
3. Install the required packages.
4. Set the following environment variables for email alerts (optional):

```bash
set SENDER_EMAIL=your_email@gmail.com
set EMAIL_PASSWORD=your_app_password
set RECEIVER_EMAIL=recipient_email@gmail.com
```

## Running the Project
Run the main app:
```bash
cd Sourcecode
streamlit run app.py
```

Run the simulation interface:
```bash
cd Sourcecode
streamlit run app1.py
```

## Notes
- Local database files, logs, and generated artifacts are ignored by Git using the repository ignore rules.
- Do not commit real passwords, email credentials, or private data.

## License
This project is intended for educational and demonstration purposes.
