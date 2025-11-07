# Qapi

This document outlines the architecture and data store design for the Qapi system.

## Architecture

Qapi is a task management system that uses a large language model (LLM) to help you organize your life. It consists of a central server, a command-line interface (CLI), and a local reminder program.

### Core Components

*   **Central Server:** A Flask server that manages the data stores and interacts with the Gemini API.
*   **CLI Tool:** A Python-based CLI for interacting with the server.
*   **Reminder Program:** A local Python script that provides desktop notifications for upcoming tasks.

## Data Stores

All data is stored in JSON files in the `data/` directory.

*   **`user_goals_map.json`**: A list of the user's high-level goals.
    *   `id`: A unique identifier for the goal.
    *   `description`: A detailed description of the goal.
    *   `truncated_desc`: A truncated description for quick reference.
    *   `entry_date`: The date the goal was added (ISO format).
    *   `due_date`: The target date for achieving the goal (ISO format).

*   **`agent_context.json`**: A list of the agent's memories and context.
    *   `id`: A unique identifier for the memory.
    *   `description`: A detailed description of the memory.
    *   `truncated_desc`: A truncated description for quick reference.
    *   `entry_date`: The date the memory was added (ISO format).

*   **`user_context.json`**: A list of the user's memories and context.
    *   `id`: A unique identifier for the memory.
    *   `description`: A detailed description of the memory.
    *   `truncated_desc`: A truncated description for quick reference.
    *   `entry_date`: The date the memory was added (ISO format).

*   **`agent_tasks.json`**: A list of tasks for the agent to perform.
    *   `id`: A unique identifier for the task.
    *   `description`: A detailed description of the task.
    *   `truncated_desc`: A truncated description for quick reference.
    *   `entry_date`: The date the task was added (ISO format).
    *   `due_date`: The target date for completing the task (ISO format).

*   **`priorities.json`**: A dictionary of the user's priorities.
    *   `daily`: A list of daily priorities.
    *   `weekly`: A list of weekly priorities.
    *   `monthly`: A list of monthly priorities.

*   **`timeheap.json`**: A list of tasks to be performed, ordered by due date. This is used by the reminder program.
    *   `id`: A unique identifier for the task.
    *   `description`: A detailed description of the task, including the consequences of not completing it.
    *   `due_date`: The date and time the task is due (ISO format).

*   **`chatlog.json`**: A log of the conversation between the user and the agent.
    *   `role`: The role of the speaker (`user` or `agent`).
    *   `content`: The content of the message.
    *   `timestamp`: The time the message was sent (ISO format).

*   **`log.txt`**: A general-purpose log file for all system events.
