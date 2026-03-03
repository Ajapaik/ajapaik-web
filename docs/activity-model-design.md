# Activity Model Design Doc

## Status

Draft for discussion

## Problem

Currently ~15 different tables store user activities, each with different schema. Unified activity log requires 8+ separate queries. No distinction between human and AI activities. Comments are decoupled from specific activities.

## Proposed Solution

### Core Model: Activity

```
Activity
├── photo_id (FK)
├── user_id (FK, NULL = AI)
├── activity_type (enum)
├── action (enum)
├── content (JSON)
├── points_awarded (int)
├── parent_activity_id (FK, nullable)
├── source (enum: HUMAN, AI)
└── created (datetime)
```

### Activity Types

| Type          | Current Table                                 |
| ------------- | --------------------------------------------- |
| GEOTAG        | GeoTag                                        |
| DATING        | Dating                                        |
| CATEGORY      | PhotoSceneSuggestion                          |
| VIEWPOINT     | PhotoViewpointElevationSuggestion             |
| FACE_BOX      | FaceRecognitionRectangle                      |
| FACE_AGE      | FaceRecognitionRectangleSubjectDataSuggestion |
| FACE_GENDER   | FaceRecognitionRectangleSubjectDataSuggestion |
| FACE_NAME     | FaceRecognitionRectangleSubjectDataSuggestion |
| OBJECT_BOX    | (broken)                                      |
| FLIP          | PhotoFlipSuggestion                           |
| INVERT        | PhotoInvertSuggestion                         |
| ROTATE        | PhotoRotationSuggestion                       |
| TRANSCRIPTION | Transcription                                 |
| TAG (→album)  | AlbumPhoto                                    |
| SIMILARITY    | ImageSimilarity                               |
| LIKE          | PhotoLike                                     |

### Actions

- CREATE
- UPDATE
- CONFIRM
- CORRECT
- DISPUTE (without alternative)
- DELETE

### ActivityComment (extends current comments)

```
ActivityComment
├── activity_id (FK, nullable - NULL = general comment)
├── user_id (FK)
├── text
└── created
```

## Migration Strategy

1. Create Activity model
2. One-time migration: populate from existing tables
3. Transition services to write to Activity
4. Deprecate old tables or keep for backwards compat
5. Frontend: single activity log query

## Notes

- AI activities: `user_id = NULL`, `source = AI`
- All points calculations move to model layer (not stored separately)
- Comments become linked to specific activities or general
- Disputes can be filed without alternative suggestion

## Open Questions

- How to handle bulk migrations with large datasets?
- Keep old tables for read-only history or migrate completely?
- Naming: "Tags" vs "Albums" for photo organization?
