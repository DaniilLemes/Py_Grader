# PyGrader

## Overview
PyGrader is a desktop application for organizing and checking programming assignments. It is built with Tkinter and `customtkinter` for a modern interface. Task data and user accounts are stored in an encrypted SQLite database. If Docker is available, solutions can be executed inside a container for isolation; otherwise the code runs directly on the host.

## Features

### User functions
- Log in and view assigned tasks
- Read task descriptions and deadlines
- Edit or upload solutions and run them against provided tests
- Submit results and track how many tests were passed

### Admin functions
- Create and manage user accounts (with optional admin rights)
- Add programming tasks with descriptions, validation rules and test cases
- Review the list of users and tasks

## Installation
Python 3.10 or newer is recommended. The application requires the following packages:

```
pip install customtkinter cryptography
```

For running code in a container install the Docker Python library and make sure the Docker daemon is available:

```
pip install docker
```

If you prefer the themed widgets from ttkbootstrap you can install it as well:

```
pip install ttkbootstrap
```

## Quick start
1. Install the required packages as shown above.
2. Run the application:
   ```bash
   python main.py
   ```
   On the first start a default administrator account is created with login `admin` and password `admin`.
3. Use these credentials to log in and create additional users or tasks.

## Usage
- **Logging in:** choose *Admin Mode* on the login screen when signing in as the administrator.
- **Admin panel:** create new users or tasks using the sidebar buttons. Each task can contain multiple test cases that will be used to check solutions.
- **User panel:** select a task to open its dedicated window. Write or upload code, run it against the tests and submit the result to store your progress.

The GUI has animated backgrounds and a dark theme to keep the interface clean. Docker integration is optional—if it is not available, tests will run directly on the host system.
