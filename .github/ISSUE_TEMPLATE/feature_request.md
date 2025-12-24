---
name: 
about: 
title: "[] "
labels: 
assignees: ''
---

## Problem

`SessionException` and `AgentException` use private attributes (with underscores), which is inconsistent with other exception classes like `GenerateException`

## Inpact

- May cause `AttributeError` when accessing `.message` after catching exceptions
- Cannnot be handled uniformly in FastAPI error handlers
- Reduces code maintainability

## File to Modify

- `backend/exceptions/exceptions.py`

## Acceptance Criteria

- [ ] All exception classes have consistent attribute names
- [ ] Existing exception handling code workd correctry
- [ ] Ruff lint passes
