# Spy Cat Agency API
[Link to Swagger UI](https://lfj7rc-8000.csb.app/docs#/)

## Endpoints

GET /cats - List Spy Cats

POST /cats - Create Spy Cat

GET /cats/{cat_id} - Get Spy Cat

PATCH /cats/{cat_id} - Update Spy Cat

DELETE /cats/{cat_id} - Delete Spy Cat

GET /missions - List Missions

POST /missions - Create Mission

GET /missions/{mission_id} - Get Mission

DELETE /missions/{mission_id} - Delete Mission

## Overview

A RESTful API system for managing spy cats, their missions, and surveillance targets. The application enables the Spy Cat Agency to track their operative cats, assign missions, and manage mission targets with data collection capabilities. Built with FastAPI and SQLAlchemy, it integrates with TheCatAPI for breed validation.

## System Architecture

### Backend Framework
- **FastAPI** - Modern Python web framework chosen for automatic API documentation, type validation, and async capabilities
- RESTful API design pattern for resource management
- Dependency injection for database session management

### Database Layer
- **SQLAlchemy ORM** - Provides database abstraction and relationship management
- **SQLite** - Lightweight file-based database for development and deployment simplicity
- Three-table relational schema:
  - `spy_cats` - Core operative entity with professional details
  - `missions` - Assignment entities linking cats to objectives
  - `targets` - Surveillance objectives with tracking capabilities

### Data Model Design
- **One-to-Many**: SpyCat → Missions (one cat can have multiple missions over time)
- **One-to-Many**: Mission → Targets (each mission has 1-3 targets)
- **Business Rules**:
  - Missions have 1-3 targets (enforced at validation layer)
  - Targets can be marked complete independently
  - Missions track completion status
  - Cascade delete for mission-target relationships

### Validation Layer
- **Pydantic schemas** - Type validation and serialization
- Field-level validators for business rule enforcement
- Separate schemas for Create/Update/Read operations following best practices

### API Structure
- Resource-based endpoints (`/cats`, `/missions`, `/targets`)
- Standard HTTP methods (GET, POST, PUT, DELETE) for CRUD operations
- Status code conventions (201 for creation, 400 for validation errors, 503 for external service issues)

## External Dependencies

### Third-Party APIs
- **TheCatAPI** (`https://api.thecatapi.com/v1/breeds`) - Validates cat breed authenticity
  - Used during spy cat creation to ensure valid breed data
  - Fallback error handling for service unavailability (HTTP 503)

### Python Libraries
- **FastAPI** - Web framework and routing
- **SQLAlchemy** - ORM and database toolkit
- **Pydantic** - Data validation and serialization
- **Requests** - HTTP client for external API calls

### Database
- **SQLite** - Embedded relational database
  - File-based storage (`spy_cats.db`)
  - Configured with `check_same_thread=False` for FastAPI compatibility
  - Auto-creates tables on application startup
