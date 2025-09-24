# Task Template

Use this template for creating new development tasks.

## Task Information

**ID:** [Unique task identifier, e.g., PROJ-05, OCR-03, UI-02]

**Description:** [Brief description of what needs to be accomplished]

**Start:** [Clear starting condition/prerequisite state]

**End:** [Specific deliverable or completion criteria]

**Tests:** [Concrete acceptance tests to verify completion]

**Dependencies:** [List of task IDs that must be completed first, or "none"]

## Example

**ID:** EXAMPLE-01

**Description:** Add user authentication endpoint

**Start:** API skeleton with basic routing exists

**End:** POST /auth/login endpoint accepting email/password and returning JWT token

**Tests:** curl -X POST /auth/login with valid credentials returns 200 and JWT; invalid credentials return 401

**Dependencies:** none
