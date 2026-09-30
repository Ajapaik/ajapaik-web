# Ajapaik API Keys Architecture & Implementation Plan

**Date:** September 30, 2026  
**Document Status:** Proposal / For Discussion

---

## 1. Context & Motivation

Ajapaik provides a wide array of REST APIs that have historically served mobile applications (Android app), integration partners (e.g., Delfi, Wikidocumentaries, Finna), as well as research and cultural heritage projects.

### Current Situation & Why We Need API Keys
- **Unrestricted Access & Scraping:** Currently, most of Ajapaik's API endpoints are publicly accessible without authentication. This creates significant risks of server overload (DDoS, aggressive scraping, automated AI training crawlers) and prevents us from distinguishing between legitimate community partners and abusive traffic.
- **Decommissioned / Deprecated Clients:**
  - **Ajapaik Android App:** The Android application is deprecated and no longer maintained or actively used. Maintaining backward compatibility for it is no longer required.
  - **Delfi Map Layer:** Delfi has removed the Ajapaik map layer; dedicated legacy partner endpoints are no longer needed in their original unrestricted form.
- **Objectives:**
  - Restrict Ajapaik's external APIs so that access requires a valid **API key**.
  - Provide a clean, secure, and easily manageable API key issuance system within the **Django Admin**.
  - Provide clear, user-friendly error messages and actionable guidance: **to access or request an API key, users must contact `info@ajapaik.ee`**.
  - Ensure that **Ajapaik's own web applications (browser frontend, PWA, in-page annotation tools)** continue operating smoothly using standard web sessions and CSRF protection without requiring external API keys.

---

## 2. API Inventory & Scope

Ajapaik's API architecture relies heavily on **Django REST Framework (DRF)**. This makes implementing global authorization straightforward and consistent.

### A. Primary REST API (`/api/v1/...`) — ~30 endpoints
*Defined in:* `ajapaik/ajapaik/api.py` and `ajapaik/ajapaik/urls.py`
- **Photos:**
  - Search & listings: `/api/v1/photos/search/`, `/api/v1/photos/search/user-rephotos/`, `/api/v1/photos/similar/`
  - Details & state: `/api/v1/photo/state/`, `/api/v1/photo/applied-operations/`
  - Rephotography & uploads: `/api/v1/photo/upload/`, `/api/v1/photo/upload/settings`
  - Favorites & suggestions: `/api/v1/photo/favorite/set/`, `/api/v1/photo/suggestion/`
- **Albums:**
  - `/api/v1/albums/`, `/api/v1/albums/search/`, `/api/v1/album/<id>/`, `/api/v1/album/nearest/`, `/api/v1/album/photos/search/`
- **Transcriptions:**
  - `/api/v1/transcriptions/`, `/api/v1/transcriptions/<photo_id>/`, `/api/v1/transcription-feedback/`
- **Partner / External Integrations:**
  - `/api/v1/finna/nearest/`, `/api/v1/photo/fetch-hkm-finna/`
  - `/api/v1/wikidocumentaries/`, `/api/v1/wikidocumentaries/photos/`
- **User Settings & Profiles:**
  - `/api/v1/user/me/`, `/api/v1/user-settings/`, `/api/v1/merge-profiles/`, `/api/v1/change-profile-display-name`

### B. Machine Recognition APIs
*Defined in:* `ajapaik/ajapaik_face_recognition/` and `ajapaik/ajapaik_object_recognition/`
- `/face-recognition/api/v1/annotation/<id>/`
- `/face-recognition/api/v1/subject-data/` *(Note: also called by the in-browser face annotation UI)*
- `/face-recognition/api/v1/album-has-annotations/<id>/`
- `/object-recognition/api/v1/annotation/<id>/`

### C. Partner Endpoints & Exceptions
- **Delfi & Bbox:** `/delfi-api/v1/...`, `/bbox/v1/` — protect with API keys or formally deprecate/retire.
- **IIIF Protocol:** `/photo/<id>/info.json/`, `/photo/<id>/manifest.json/` — *Recommendation:* Keep public. IIIF is an open cultural heritage image delivery standard; restricting it would break embedded open viewers.
- **Internal Web AJAX Views:** `/map-data/`, `/frontpage-async/`, `/autocomplete/...` — These are frontend view endpoints rather than external public APIs and will continue to work via standard web sessions.

---

## 3. Technical Architecture

### 3.1. Database Model: `ApiKey`
Create an `ApiKey` model (in `ajapaik_auth` or a dedicated lightweight app `ajapaik_api_auth`):

```python
class ApiKey(models.Model):
    name = models.CharField(max_length=255, help_text="Client or project name (e.g. 'University of Tartu Research Lab')")
    contact_email = models.EmailField(help_text="Contact email of the key owner")
    prefix = models.CharField(max_length=8, unique=True, db_index=True)
    hashed_key = models.CharField(max_length=128)
    
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
```

- **Security & Key Format:**
  - Keys will follow a recognizable format such as `ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`.
  - For maximum security, the raw key is displayed **only once** to the admin upon creation.
  - The database stores only a secure SHA-256 hash and the 8-character prefix for lookup.

### 3.2. Key Transmission Methods
Clients will be able to provide the API key via:
1. **HTTP Authorization Header (Standard):**
   ```http
   Authorization: Api-Key ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
2. **Custom HTTP Header:**
   ```http
   X-API-KEY: ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. **Query Parameter (Convenient for simple GET requests):**
   ```http
   https://ajapaik.ee/api/v1/photos/search/?query=Tallinn&api_key=ajp_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 3.3. DRF Permission Class: `HasApiKeyOrWebSession`
Because certain parts of Ajapaik's web frontend (e.g., the face annotation tool) make client-side requests to API endpoints, the permission class must handle both external consumers and first-party web sessions:

- **ALLOWED** if the request contains a valid, active `ApiKey`.
- **ALLOWED** if the request comes from an authenticated Django web session (or valid session cookie with CSRF check).
- **DENIED (401 Unauthorized)** if neither is present.

Configured globally in `ajapaik/settings/default.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'ajapaik.ajapaik.permissions.HasApiKeyOrWebSession',
    ],
    ...
}
```

---

## 4. Error Response & Guidance

When an unauthenticated request is received without a valid API key, the API returns an **HTTP 401 Unauthorized** with clear JSON guidance:

```json
{
  "error": "api_key_required",
  "detail": "Ajapaik API requires a valid API key. If you wish to use the Ajapaik API, please contact info@ajapaik.ee to request an access key.",
  "contact": "info@ajapaik.ee",
  "documentation": "https://ajapaik.ee/api/"
}
```

This guarantees that external script authors and researchers immediately know who to contact and how to gain access.

---

## 5. Administration Interface (Django Admin)

In the standard Django admin (`/admin/`):
- **Key Overview:** List view showing owner name, contact email, active/revoked status, last used timestamp, and rate limits.
- **Key Generation:** Admin fills in the client name and contact email; upon saving, the generated key is shown in a modal/banner for one-time copying.
- **Immediate Revocation:** Ability to deactivate or revoke keys immediately if abuse is detected.

---

## 6. Rate Limiting & Throttling

To prevent resource exhaustion from approved clients:
- Integrate with DRF's built-in throttling mechanism per API key.
- **Default Profile:**
  - Standard key: 60 requests/minute, 10,000 requests/day.
  - Custom partner tier: Configurable higher thresholds for verified research or institutional partners.
- When limits are exceeded, return an HTTP **429 Too Many Requests** response.

---

## 7. Phased Rollout Plan

To ensure a smooth transition without breaking legitimate use cases, a 3-phase rollout is recommended:

### Phase 1: Implementation & Admin Setup (1–2 days)
1. Add the `ApiKey` model and migrations.
2. Build the Django Admin interface for key generation, listing, and revocation.
3. Implement the `HasApiKeyOrWebSession` permission class and throttling logic.

### Phase 2: Staging Testing & Production "Shadow Mode" (3–7 days)
1. Deploy to the `staging` server to verify that all web and PWA frontend workflows function without disruption.
2. Deploy to production in **Shadow Mode (Telemetry)**:
   - Requests without an API key are logged (recording IP, User-Agent, and endpoint), but not yet blocked.
   - This provides the team with full visibility into whether any critical external integration is still running that we were not aware of.

### Phase 3: Full Enforcement
1. Issue keys to any verified active partners identified during Phase 2.
2. Switch from logging to full enforcement (returning HTTP 401 with the `info@ajapaik.ee` message).
3. Update Ajapaik footer/documentation with brief instructions on requesting an API key.

---

## 8. Discussion Points for Märt & Kimmo

1. **Known Active Partners:**
   - Are there specific partners (e.g. Wikidocumentaries, Wikimedia Commons bots, Finna, universities) whose workflows we should proactively reach out to and provide keys for?
2. **IIIF Protocol:**
   - Do you agree that IIIF endpoints (`/photo/<id>/info.json/`, `/photo/<id>/manifest.json/`) should remain open as standard cultural heritage protocols?
3. **Admin-only Issuance vs Self-service:**
   - Recommendation: Keep it admin-only initially (keys issued manually upon emailing `info@ajapaik.ee`). Self-service (generating keys from the user profile page) can be added later if demand justifies it.
