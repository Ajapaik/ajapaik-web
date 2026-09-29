# AI Agent Guidelines for Ajapaik Web

This document outlines mandatory coding guidelines and development principles for AI agents (and human developers) working on the `ajapaik-web` repository.

---

## 1. Core Principle: Modernize, Do Not Emulate Legacy Patterns

> **CRITICAL RULE:**
> This codebase contains historical code spanning more than a decade (dating back to Python 2 / Django 1.x–2.x).
> **DO NOT** replicate or mimic existing legacy conventions when creating new features, refactoring, or modifying existing code.
> **DO** write clean, modern, idiomatic Python 3.10+ and Django 4.2+ code.

If you encounter legacy patterns (e.g., untyped 500-line procedural views, raw untyped dictionaries, global mutable state, missing error handling), do **not** take them as a template. Instead, implement your changes using modern architecture and strict typing.

---

## 2. Python & Type Hints (Strictly Enforced)

All new Python code and any modified functions/classes **must include explicit type annotations**:

1. **Mandatory Type Hints**:
   - Every function and method parameter must have a type annotation.
   - Every function and method must have an explicit return type annotation (e.g., `-> None`, `-> Response`, `-> list[Photo]`).
   - Class attributes, constants, and complex variables should have type annotations where not obvious.

2. **Modern Typing Syntax (Python 3.10+)**:
   - Use built-in generic types: `list[str]`, `dict[str, Any]`, `set[int]`, `tuple[int, ...]` (do **not** import `List`, `Dict`, `Set`, `Tuple` from `typing`).
   - Use the union operator `|` for optional and union types: `str | None` (do **not** use `Optional[str]`), `int | float` (do **not** use `Union[int, float]`).
   - Import necessary utilities from `typing` when needed: `Callable`, `Iterable`, `Sequence`, `Generator`, `Any`, `cast`, `TypedDict`, `Protocol`.

3. **Data Structures**:
   - Avoid passing unstructured, untyped `dict` objects across function/module boundaries.
   - Prefer `@dataclass(slots=True)`, `NamedTuple`, `TypedDict`, or Django REST Framework `Serializer` / dataclasses to define explicit data contracts.

4. **Avoid Untyped `*args` and `**kwargs`**:
   - Explicitly define accepted arguments whenever possible.
   - If `**kwargs` are unavoidable (e.g., Django subclassing), document or annotate them with `typing.Unpack` / `TypedDict` where applicable.

---

## 3. Formatting, Linting & Quality Tools (Ruff & Mypy)

1. **Ruff (Formatting & Linting)**:
   - Code must be formatted and linted with **Ruff**.
   - Target line length: **120 characters** (consistent with `.flake8`).
   - Run `ruff check --fix` and `ruff format` on any modified or newly created files.
   - Imports must be sorted alphabetically and grouped properly (standard library, third-party, local app).

2. **Mypy**:
   - Ensure code passes `mypy` checks (configured in `mypy.ini` with `mypy_django_plugin` and `mypy_drf_plugin`).
   - Avoid using `# type: ignore` unless strictly necessary due to third-party stub limitations; always document the reason if used.

---

## 4. Architecture & Django Conventions

1. **Domain Logic vs. Views**:
   - Keep views thin! Views should handle HTTP request validation, authentication/permissions, call domain/service layer functions, and return responses.
   - Place business logic in dedicated service modules or domain objects (see modern sub-apps like `ajapaik_face_recognition` and `ajapaik_object_recognition`).
   - Do not write monolithic 500-line view functions. Split logic into small, focused, testable functions and classes.

2. **Django ORM Best Practices**:
   - Always prevent **N+1 query problems**: use `select_related()` for `ForeignKey` / `OneToOne` and `prefetch_related()` for `ManyToManyField` / reverse relations.
   - Use `.only()` or `.values_list()` when only specific columns are needed in performance-critical paths.
   - Avoid executing queries inside template tags or loops.

3. **Background Tasks & Heavy Operations**:
   - Do **not** execute heavy synchronous operations (image processing, face detection, metadata fetching, external API sync) in the request-response cycle.
   - Structure heavy operations so they can be offloaded to background task runners (e.g., `django-tasks` / management commands / background workers) rather than blocking web worker threads.

4. **Error Handling & Logging**:
   - Be specific with exceptions; do not use bare `except:` or `except Exception: pass`.
   - Log unexpected errors with `logger.exception()` including useful context.

---

## 5. Frontend & JavaScript

1. **Modern JavaScript (ES6+)**:
   - Use `const` and `let` (never `var`).
   - Prefer modern standard APIs (`fetch`, `async`/`await`, `URLSearchParams`, modern DOM methods) over legacy jQuery spaghetti where feasible.
   - When modifying existing jQuery code, keep changes clean, modular, and well-commented.

2. **Resilience & Mobile Experience**:
   - Many Ajapaik users take photos and rephotos in the field with poor or fluctuating network connections.
   - Always design mobile-first and offline-tolerant flows (e.g., local queuing via IndexedDB, non-blocking uploads, clean user feedback without modal lockouts).

---

## 6. Testing & Quality Checks

1. **Tests**:
   - When adding features or fixing bugs, write unit or integration tests in `ajapaik/tests/` or the corresponding sub-app's `tests/`.
   - Use `pytest` and `pytest-django`.

2. **Clean Commits & Pull Requests**:
   - Write clear, concise commit messages following standard conventions (`feature: ...`, `fix: ...`, `refactor: ...`).
   - Avoid committing temporary files (`.DS_Store`, debug images, scratch scripts).
