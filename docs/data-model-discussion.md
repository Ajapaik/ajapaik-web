# Ajapaik Data Model Discussion

## Overview

Ajapaik is a collaborative platform for enriching historical photos with metadata (locations, people, transcriptions, etc.). This document discusses two interconnected but separate concerns:

1. **Image/Physical Structure** - What IS a photo? (Work, Exemplar, Surface, Digital)
2. **Activity Tracking** - Who did WHAT and when?

---

# Part I: Image Structure Model

## The Core Problem

Historical photos have complex relationships that simple models don't capture:

- Same photo exists as glass negative, paper print, and colored postcard
- Composite images (postcards with multiple mini-photos)
- Same scene captured at different times (repeat photography / refotos)
- Original capture order vs. later album arrangements

## Core Entities

```
ImageWork          → "Root photo / meta photo"
PhysicalExemplar   → Physical object (glass negative, postcard, print)
ExemplarSurface   → Side (recto/verso)
DigitalImage       → Digital file
SurfaceWork        → Relationship: which work is on which surface (with region)
ImageSequence      → Series/orderings
```

## 1.1 ImageWork

Abstract representation - same across all exemplars. This is the "essence" of the photo.

**Fields:**

- title, description
- author/photographer
- creation date (year, interval, ca-date)
- location (geocoordinates)
- depicted objects, persons
- keywords, themes, categories
- license status

**Rule:** Everything describing "this scene/frame" belongs at Work level. This is what gets shared across all physical copies.

## 1.2 PhysicalExemplar

Concrete physical object - glass negative, paper print, postcard, slide, etc. This is the actual physical item in archives.

**Fields:**

- related work (FK to ImageWork)
- repository, collection, signature
- type: glass_negative / paper_print / postcard / slide / album_page / other
- dimensions, material, technique
- condition, notes
- digitization info (scanner, DPI, date)

**Rule:** Everything related to the physical item, not image content. Different copies may have different conditions, marks, or even be colored versions of a black-and-white original.

## 1.3 ExemplarSurface

Side of an exemplar. Some exemplars have 1 side (glass negative), some have 2 (postcard), some have multiple (album page with multiple photos).

**Fields:**

- exemplar (FK)
- side_type: recto, verso, spine, other
- sequence_index (if more than 2 sides)

## 1.4 DigitalImage

Digital file / scan - the actual image file served to users.

**Fields:**

- surface (FK)
- file_uri, width, height, filesize
- type: master/derivative/thumbnail
- color_mode: bw / greyscale / colour / tinted

---

# Part II: Complex Relationships

## The Composite Problem

A postcard might show 6 different views of a city. Each view is a separate "root image" but exists on the same physical postcard. How to model this?

## 2.1 SurfaceWork Join Table

Binds Work to Surface - this is the key innovation that enables composites.

```
SurfaceWork
├── surface (FK)
├── work (FK)
├── region_on_surface (bounding box, normalized 0-1 or IIIF style coordinates)
└── order_index (for composites - order of mini-images)
```

**The genius:** A surface can have MULTIPLE works (composite), and a work can appear on MULTIPLE surfaces (same view on glass negative AND paper print).

**Examples:**

**Simple photo:**

- One Work, one Exemplar, one SurfaceWork entry, no region (or "full": 0,0,1,1)

**Composite postcard:**

- PhysicalExemplar: postcard
- ExemplarSurface (recto): front side of postcard
- Multiple ImageWorks: each "mini-image" on the postcard
  - Work #1: "City X church"
  - Work #2: "City X town hall"
  - ...
- SurfaceWork: each with region coordinates:
  - (surface=recto, work=Work#1, region=(0.0,0.0,0.5,0.33))
  - (surface=recto, work=Work#2, region=(0.5,0.0,0.5,0.33))

If someone has the same "church view" as a separate glass negative, that negative has its own ExemplarSurface, also linked to Work #1.

**Benefits:**

- Shared data (location, date, persons) at Work level
- Physical/technical differences at Exemplar/Surface level
- Composite images properly linked to their root images

## 2.2 ImageSequence

Series/orderings - capture order vs. later arrangement. Important distinction:

- **Capture order:** Photos taken on same film roll
- **Physical layout:** Photos arranged on album page
- **Curatorial:** Later intellectual ordering (exhibitions, web galleries)

```
ImageSequence
├── id
├── label (e.g., "Film nr 24, 35mm, Narva trip 1938")
├── sequence_kind:
│   ├── CAPTURE_ORDER     - creation order (film strip)
│   ├── PHYSICAL_LAYOUT   - physical arrangement (album page)
│   └── CURATORIAL        - later intellectual ordering
├── created_by
├── created_at
└── notes

SequenceMembership
├── sequence (FK)
├── member_work (FK, nullable)
├── member_surface (FK, nullable)
├── member_exemplar (FK, nullable)
├── position_index (frame number)
└── row, column (optional - for contact sheets or album grids)
```

**Use cases:**

- Browse "film roll" by frame (sequence continuity in UI)
- Link same root image through multiple exemplars (if a frame was also printed separately)
- Simple alternative: Work can have previous_work / next_work fields

---

# Part III: Orientation & Mirroring

## The Problem

Some glass negatives have 4 frames, some rotated 90°. Some paper prints are mirror-images of the negative. The "correct" orientation belongs at Work level, but physical reality may differ.

## Three Levels

1. **ImageWork** - canonical orientation (the "correct" way to view)
2. **SurfaceWork** - how work appears on this specific surface (rotation + mirror)
3. **DigitalImage** - how file is encoded (EXIF orientation)

## Fields

**ImageWork - canonical orientation:**

- canonical_rotation: 0, 90, 180, 270
- canonical_mirrored: bool (usually false)

Most photos don't need this - system assumes 0/not mirrored. But some artistic choices result in mirrored images.

**SurfaceWork - work on surface:**

- rotation_from_work: 0, 90, 180, 270
- mirrored_from_work: bool

**Example A: 4 frames on one glass plate, different orientations**

- PhysicalExemplar: glass plate
- ExemplarSurface(recto): entire plate image
- Each frame = separate ImageWork
- Each SurfaceWork: region_on_surface (coordinates of that frame), rotation_from_work (if that frame is "sideways")

**Example B: Glass negative → mirrored paper print**

Define "correct" orientation based on negative (canonical_mirrored=false).

Negative:

- SurfaceWork (plate recto, region full), rotation=0, mirrored=false

Mirrored paper print:

- Different PhysicalExemplar
- SurfaceWork: same Work, rotation=0, mirrored=true

Result:

- Historical fact: this specific copy IS mirrored - preserved
- "Correct" orientation at Work level - usable for mapping, face detection, AI
- Viewer can warn: "This exemplar is mirrored compared to the canonical version"

---

# Part IV: Special Cases

## 4.1 Stereophotos

Two images, left/right eye, slightly different angles. Conceptually a special composite.

**Solution:**

- Each eye = separate ImageWork
- Same PhysicalExemplar, same SurfaceWork entries with different region_on_surface
- Linked via ImageSequence (sequence_kind = STEREO_PAIR)
- Or via WorkRelation table: STEREO_LEFT_OF / STEREO_RIGHT_OF

**Metadata handling:**

- Location, persons - can be shared between both works
- Simple: annotate on one Work, system copies to other
- Complex: use "stereo scene" Work at higher level

**Viewing:**

- Two DigitalImages OR one scan, viewer crops via region_on_surface
- sequence_kind + left/right position tells viewer how to display

## 4.2 Refotos (Repeat Photography)

Ajapaik's core feature: new photo from same viewpoint as historical photo. "Before and after" comparison.

**Each refoto = new ImageWork:**

- author = Ajapaik user
- creation date, location (GPS)
- work_type = REFOTO

**WorkRelation table - semantic link:**

```
WorkRelation
├── from_work (refoto)
├── to_work (original historical)
├── relation_type: REPHOTO_OF, DUPLICATE_OF, CROPPED_FROM, STEREO_LEFT_OF, etc.
├── created_by
├── created_at
└── quality_score (optional)
```

**For temporal series (1900 → 1960 → 1990 → 2024):**

- ImageSequence with sequence_kind = REPHOTO_SERIES
- Enables: timeline slider, chronological ordering, "then vs. now" features

**Location handling:**

- Historical Work: reconstructed camera position (from refotos)
- Refoto Work: actual GPS coordinates
- Both stored, but historical work's location is primary for search/maps

---

# Part V: Activity Tracking (Proposed)

_This section proposes a unified Activity model for tracking all user interactions._

## Why Separate From Physical Model?

The physical model (Parts I-IV) describes WHAT the photos ARE.
The Activity model describes WHO DID WHAT.

They are complementary:

- ImageWork = the photo's data
- Activity = who contributed what to that data

## Current Problem

Currently ~15 different tables store user activities, each with different schema:

- Points (some activities)
- PhotoLike
- PhotoComment / MyXtdComment
- PhotoSceneSuggestion
- PhotoViewpointElevationSuggestion
- GeoTag
- Dating
- FaceRecognitionRectangle
- PhotoFlipSuggestion
- PhotoInvertSuggestion
- PhotoRotationSuggestion
- Transcription
- AlbumPhoto
- ImageSimilarity

Each requires separate query. No distinction between human and AI activities. Comments decoupled from specific activities.

## Proposed Solution: Activity Model

```
Activity
├── photo_id (FK)
├── user_id (FK, NULL = AI)
├── activity_type (enum)
├── action (enum)
├── content (JSON - type-specific data)
├── points_awarded (int)
├── parent_activity_id (FK, nullable - for replies/disputes)
├── source: HUMAN | AI
└── created (datetime)
```

### Activity Types

| Type          | Current Table                     |
| ------------- | --------------------------------- |
| GEOTAG        | GeoTag                            |
| DATING        | Dating                            |
| CATEGORY      | PhotoSceneSuggestion              |
| VIEWPOINT     | PhotoViewpointElevationSuggestion |
| FACE_BOX      | FaceRecognitionRectangle          |
| FACE_AGE      | FaceRecognitionSuggestion         |
| FACE_GENDER   | FaceRecognitionSuggestion         |
| FACE_NAME     | FaceRecognitionSuggestion         |
| OBJECT_BOX    | (currently broken)                |
| FLIP          | PhotoFlipSuggestion               |
| INVERT        | PhotoInvertSuggestion             |
| ROTATE        | PhotoRotationSuggestion           |
| TRANSCRIPTION | Transcription                     |
| TAG (→album)  | AlbumPhoto                        |
| SIMILARITY    | ImageSimilarity                   |
| LIKE          | PhotoLike                         |

### Actions

- CREATE - Initial creation of annotation
- UPDATE - User corrected/changed something
- CONFIRM - User confirmed existing annotation (currently underused)
- CORRECT - User provided better alternative
- DISPUTE - User challenges without providing alternative
- DELETE - User removed their contribution

### Activity Comments

Comments should be linked to activities or be general:

```
ActivityComment
├── activity_id (FK, nullable - NULL = general comment)
├── user_id (FK)
├── text
└── created
```

### AI vs. Human Activities

AI-generated content (face detection, similarity hashes, object detection) gets:

- user_id = NULL
- source = AI

This enables filtering: "show only human contributions" or "show only AI suggestions for human review".

---

# Part VI: Standards Compliance

## CIDOC CRM Mapping

| Our Concept      | CIDOC CRM Concept                               |
| ---------------- | ----------------------------------------------- |
| ImageWork        | E38 Visual Item (abstract visual entity)        |
| PhysicalExemplar | E22 Man-Made Object (physical item)             |
| ExemplarSurface  | Physical surface/side                           |
| SurfaceWork      | E5 Event / E4 Period (binding work to physical) |

## IIIF Mapping

- SurfaceWork.region_on_surface → IIIF Canvas Annotation
- ImageSequence → IIIF Sequence/Range
- DigitalImage + region → IIIF Canvas + Annotation
- If Ajapaik ever implements IIIF, mapping is natural

---

# Summary

## Physical Model (What IS the photo)

```
ImageWork (content: location, date, persons, description)
    ↓
PhysicalExemplar (physical: type, collection, condition)
    ↓
ExemplarSurface (side: recto/verso)
    ↓
DigitalImage (file: URI, dimensions, format)

SurfaceWork (binds work to surface with region = enables composites)
ImageSequence (orderings: capture, layout, curatorial)
WorkRelation (refotos, duplicates, stereo pairs)
```

## Activity Model (Who did WHAT)

```
Activity (all user/AI actions unified)
ActivityComment (linked to activity OR general)
```

## Key Design Principles

1. **Separate concerns:** Physical structure ≠ Activity tracking
2. **Normalized but flexible:** SurfaceWork join enables complex relationships
3. **Standards-aligned:** Maps to CIDOC CRM and IIIF
4. **Future-proof:** Activity.source distinguishes AI from human contributions
5. **Composable:** Same work can appear on multiple surfaces, same surface can show multiple works

This model handles simple photos, composite images, stereo pairs, repeat photography, orientation quirks, and provides a foundation for unified activity tracking.
