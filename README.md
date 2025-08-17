# JobOrbit: Your Personal Job Aggregator

JobOrbit is a powerful, personalized job scraping and aggregation platform designed to streamline your job search. It fetches job listings from various online sources, collates them into a unified dashboard, and provides tools to filter and manage applications, saving you time and effort.

## Core Features

*   **Multi-Source Scraping**: Gathers job postings from popular platforms like LinkedIn, Indeed, and others.
*   **Centralized Dashboard**: All scraped jobs are displayed in a clean, easy-to-navigate interface.
*   **Advanced Filtering**: Users can filter jobs by title, company, location, and keywords.
*   **User Authentication**: Secure user registration and login system to manage personal job searches.
*   **Personalized Experience**: Save searches, track applications, and customize your job feed.

## Tech Stack

*   **Backend**: Python, Django
*   **Frontend**: HTML, CSS, JavaScript
*   **Database**: SQLite (or other Django-supported DB)
*   **Scraping**: Utilizes libraries like Beautiful Soup and Selenium.

## Getting Started

### Prerequisites

*   Python 3.x
*   Pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/JobOrbit.git
    cd JobOrbit/aggregator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

## Resume Description Points

*   Engineered and launched **JobOrbit**, a full-stack job aggregation platform using Django and Python to scrape and centralize listings from multiple online sources, improving job search efficiency.
*   Implemented a robust web scraping module with Selenium and BeautifulSoup to parse complex job sites, overcoming challenges like dynamic content loading and anti-scraping measures.
*   Designed and built a user-centric dashboard with features for advanced filtering, saved searches, and application tracking, demonstrating strong problem-solving and full-stack development skills.
*   Developed a secure user authentication system, managed a relational database with SQLite, and deployed the application, showcasing end-to-end project ownership and a grasp of the software development lifecycle.