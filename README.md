# Event Management System

This project is an event management system built using Django and Django REST Framework. The system allows users to register, log in, view events, register for events, and manage event details. It includes both frontend and backend components and is containerized using Docker.

## Features

- **User Authentication**: Register, login, and logout functionality.
- **Event Management**: Create, update, delete, and view events.
- **Event Registration**: Users can register for events and receive email confirmations.
- **Filters and Search**: Events can be filtered by date, time, and location.
- **Admin Capabilities**: Only admins can create and manage events.

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: Bootstrap (for styling and responsive design)
- **Database**: PostgreSQL (can be replaced with other databases)
- **Email**: Django's email backend for sending confirmation emails
- **Containerization**: Docker


## Installation

### Prerequisites

- Python 3.12
- Docker and Docker Compose

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Zvnazar00/Event_Management_.git

2. **Set up a virtual environment and install dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
3. **Set up environment variables**:
Create a .env file in the root directory of the project and add the necessary environment variables, such as database configurations and email settings.

4. **Apply migrations**:
   ```bash
   python manage.py migrate

5.**Run the development serve**:
     ```bash
     python manage.py runserver
     
### Docker Setup

1. **Build the Docker image**:
   ```bash
   docker-compose build
   
2. **Run the Docker container**:
   ```bash
   docker-compose up

## Usage

### User Registration and Login
- Navigate to `/register` to create a new user account.
- After registration, log in at `/login`.

### Event Management
- Users can view the list of events on the homepage.
- Admin users can create, update, and delete events.

### Event Registration
- Users can register for events directly from the event list or detail pages.
- Upon registration, users will receive a confirmation email with event details.

## Frontend Design

The frontend of this application is styled using Bootstrap, a popular CSS framework that provides responsive and modern design components.
