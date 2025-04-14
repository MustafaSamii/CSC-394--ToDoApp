# DePaul ToDo App

This is a simple web-based task management application we built as part of my CSC-394/IS 376 project. The app lets you register, log in, and manage your tasks (or "ToDos") from a neat dashboard. It also includes team management features so you can collaborate easily.

## Features

- **User Authentication:**  
  - Register, log in, and log out with ease.
  - Display your email in the header when logged in.

- **Task Management:**  
  - Create, update, and delete tasks.
  - Change task status (Not Started, In Progress, Paused, Completed) with action buttons.
  - Track time for tasks that are in progress.

- **Dashboard:**  
  - View your tasks grouped by status.
  - Each task displays its title, description, category, and a timer if it’s active.
  - Action buttons let you start, pause, resume, or stop (complete) tasks.

- **Team Management:**  
  - Create and edit teams.
  - View team details and manage team members.
  - A default avatar image is used if no profile picture is set.

- **Responsive Design:**  
  - The UI is built with Bootstrap 5, so it looks great on desktops, tablets, and phones.

- **Docker Ready:**  
  - The project includes Docker support so you and your teammates can run it in a container.

## Getting Started

### Local Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/SamSamiSz/CSC-394--ToDoApp.git
   cd CSC-394--ToDoApp
   .\venv\Scripts\activate
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
