# Support Ticket API Specification

## Purpose
Build a simple API for managing customer support tickets.

## Features
- Create a ticket
- List tickets
- Get a single ticket
- Update ticket status
- Delete a ticket

## Ticket
- customer_name
- customer_email
- subject
- description
- status

## Business Rules
- New tickets start as `open`.
- `open` can become `in_progress`.
- `in_progress` can become `resolved`.
- `resolved` cannot become `open`.
- Missing tickets return 404.
- Invalid email addresses are rejected.