# Homework 2: Python-Flask Setup & Grading Instructions

This guide walks you through setting up your Python virtual environment, running your Flask server, and executing the automated unit testing grader script (`test_app.py`).

## Step 1: Create & Activate a Virtual Environment

Isolate your project dependencies using a Python virtual environment.

### Open the Terminal in VS Code

Press `Ctrl + ~` (or select **Terminal** -> **New Terminal** from the top menu). Make sure you are in your project root directory.

### Create the Virtual Environment

Run the following command in your terminal:

```powershell
python -m venv .venv
```

### Activate the Virtual Environment (Windows)

* **In PowerShell (VS Code default):**
```powershell
.\.venv\Scripts\Activate.ps1

```

Once activated, you will see `(.venv)` prefixed at the beginning of your terminal command prompt line.

### 4. Install Project Requirements

Upgrade `pip` and install all required packages:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

```

## Step 2: Run Your Flask Server

Before running the grader script, your Flask application must be actively running.

1. In your activated terminal `(.venv)`, start the Flask development server:
```powershell
flask run
```

2. You should see output similar to:
```text
* Serving Flask app 'app.py'
* Debug mode: off
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Leave this terminal window open and running!** If you stop the server, the test script will fail to connect.

## Step 3: Run the Unit Test Grader Script

To test your routes and see your estimated point breakdown, run `test_app.py` in a **second, separate terminal window**.

1. Open a **new terminal tab/window** in VS Code (click the `+` button in the Terminal panel).
2. Activate your virtual environment in the new terminal:
```powershell
.\.venv\Scripts\Activate.ps1
```

3. Run the automated grading script:

```powershell
python test_app.py
```

## Interpreting Your Results

The test runner will execute all tests against your running Flask server. Once finished, it prints a point breakdown:

* **Passed Tests:** Displayed as successes.

* **Failed Tests:** Outlined with the specific endpoint error and the number of points deducted.

* **Total Score:** Displayed at the very bottom out of 100 possible points.

### Example Output:

```text
======================================================================
GRADED POINT BREAKDOWN SUMMARY
======================================================================

[-] test_lotto_input_errors FAILED: Lost 12 pts
    Reason: AssertionError: 200 != 400

----------------------------------------------------------------------
TOTAL SCORE: 88 / 100 pts
======================================================================
```