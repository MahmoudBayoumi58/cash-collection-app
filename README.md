
# Cash Collection Application

This project is a Django-based Cash Collection application with a RESTful backend. The application supports managing tasks for cash collectors and includes features like task assignment, status tracking, and account freezing based on specified thresholds.

## Features

- **Database Models**: Manages users (cash collectors and managers), tasks, and collection records.
- **Status Display**: Shows the status of tasks at different time points.
- **RESTful API**: Provides endpoints for tasks, task statuses, collections, and deliveries.
- **Account Freezing**: Freezes accounts if they hold more than 5000 USD for over 2 days.
- **Configuration**: Uses environment variables for configurable thresholds.

## Getting Started


### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/MahmoudBayoumi58/cash-collection-app.git
    cd cash-collection-app
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run database migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Start the development server:
    ```bash
    python manage.py runserver
    ```

### Usage

- Use the API endpoints in post-man collection to interact with tasks, collections, and statuses.

### API Endpoints

- **Registration**: `/user/v1/register/` - By default register user as cash-collector account.
- **Login**: `/user/v1/login/` - Auth user using JWT.
- **Logout**: `/user/v1/logout/` - Used to log out a user by revoking the refresh token.
- **Add Customer**: `/user/v1/customer/add/` - Used to add a new customer.
- **Users Status**: `/user/v1/status/list` - Get up-to-date list of frozen/unfrozen users.
- **Create Task**: `/cash/v1/task/add/` - Used to add a new cash collection task.
- **Cash Collector Completed Tasks**: `/cash/v1/cash_collector/tasks` - Get list of cash collector tasks that has been done be him.
- **Next Task**: `/cash_collector/task/next` - Get the next task for a cash collector.
- **Status**: `/cash/v1/cash_collector/status/<int:id>/` - Check if a cash collector is frozen with the specified ID.
- **Collect**: `/cash/v1/cash_collector/task/collect/<int:id>/` - Update status of task from pending to collected with the specified ID.
- **Pay**: `/cash/v1/cash_collector/task/pay/` - Log delivered amounts to the manager.
- **Collection Record**: `/cash/v1/cash_collector/records/<int:id>/` - used to retrieve the status of cash-collector at different time points.
- **Tasks Status**: `/cash/v1/tasks/` - Allows to retrieve cash-collector tasks by status ['pending', 'collected', 'completed'].

## Configuration

Environment variables can be used to configure thresholds and other settings.
