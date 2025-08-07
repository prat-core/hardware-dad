
# Diagram Generation Backend Specification

This document outlines the technical specification for the diagram generation backend.

## 1. Tech Stack, Libraries, and Frameworks

*   **Language:** Python 3.10+
*   **Framework:** FastAPI
*   **Libraries:**
    *   Pydantic (for data validation, included with FastAPI)
    *   Uvicorn (for serving the FastAPI application)

## 2. API Endpoints

The API will expose the following endpoints:

*   **`POST /diagram`**: Creates a new diagram.
    *   **Request Body:** A JSON object representing the diagram, including a list of components and connections.
    *   **Response:** The created diagram object with a unique ID.
*   **`GET /diagram/{diagram_id}`**: Retrieves a diagram.
    *   **Response:** The diagram object in JSON format.
*   **`PUT /diagram/{diagram_id}`**: Updates an existing diagram.
    *   **Request Body:** A JSON object with the updated diagram data.
    *   **Response:** The updated diagram object.
*   **`DELETE /diagram/{diagram_id}`**: Deletes a diagram.
    *   **Response:** A confirmation message.
*   **`GET /diagram/{diagram_id}/wokwi`**: Generates the `diagram.json` for the Wokwi simulator.
    *   **Response:** A JSON object compatible with the Wokwi simulator.

## 3. Architecture

The backend will follow a layered architecture:

```
+-----------------+      +--------------------+      +----------------------+
|                 |      |                    |      |                      |
|      User       |----->|    FastAPI App     |----->|   Diagram Service    |
| (Frontend/CLI)  |      | (API Endpoints)    |      | (Business Logic)     |
|                 |      |                    |      |                      |
+-----------------+      +--------------------+      +----------------------+
                                 |
                                 |
                                 v
                 +--------------------------------+
                 |                                |
                 |      wokwi_components          |
                 | (Python representation of     |
                 |      Wokwi elements)         |
                 +--------------------------------+
```

*   **API Layer (FastAPI App):** This layer is responsible for handling incoming HTTP requests, validating data using Pydantic models, and routing requests to the appropriate service.
*   **Service Layer (Diagram Service):** This layer contains the core business logic of the application. It will handle the creation, retrieval, updating, and deletion of diagrams.
*   **Data Layer (wokwi_components):** This layer will consist of Python classes that represent the Wokwi elements. These classes will be responsible for serializing themselves to and from JSON.

Initially, diagrams will be stored in memory. A persistence layer (e.g., a database) can be added in the future.

## 4. Integrations

*   **Wokwi Simulator:** The primary integration is with the Wokwi simulator. The backend will generate JSON files that can be directly imported into Wokwi.
*   **Frontend:** A future frontend application will use this API to provide a graphical interface for creating and editing diagrams.
