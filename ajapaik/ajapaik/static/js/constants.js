'use strict';

var constants = {
    keyCodes: {
        ESCAPE: 27,
        D: 68,
        ARROW_RIGHT: 39,
        ARROW_LEFT: 37
    },
    fieldValues: {
        UNSURE: 'UNSURE',
        MALE: 'MALE',
        FEMALE: 'FEMALE',
        CHILD: 'CHILD',
        ADULT: 'ADULT',
        ELDERLY: 'ELDERLY'
    },
    elements: {
        NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID: 'new-object-select-fields-wrapper-id',
        ANNOTATION_MORE_SPECIFIC_FIELDS_WRAPPER_ID: 'more-specific-annotation-fields-wrapper',
        AUTOCOMPLETE_WRAPPER_ID: 'autocomplete-wrapper',
        SUBJECT_AUTOCOMPLETE_ID: 'autocomplete-subject',
        ADD_NEW_FACE_FIELDS_WRAPPER_ID: 'add-new-subject-fields-wrapper',
        SUBJECT_GENDER_SELECT_ID: 'gender-select-subject',
        SUBJECT_GENDER_SELECT_WRAPPER_ID: 'gender-select-subject-wrapper',
        SUBJECT_AGE_GROUP_SELECT_ID: 'age-group-subject',
        SUBJECT_AGE_GROUP_SELECT_WRAPPER_ID: 'age-group-select-subject-wrapper',
        ADD_NEW_SUBJECT_LINK_ID: 'add-new-subject',
        POPOVER_CONTROL_BUTTONS_ID: 'control-buttons',
        OBJECT_CLASS_SELECT_ID: 'select-object-class',
        IS_CORRECT_OBJECT_CHECKBOX_ID: 'is-correct-object',
        IS_FACE_ANNOTATION_CHECKBOX_ID: 'is-face-annotation',
        IS_CORRECT_AGE_CHECKBOX_ID: 'is-correct-age',
        IS_CORRECT_GENDER_CHECKBOX_ID: 'is-correct-gender',
        IS_CORRECT_PERSON_NAME_CHECKBOX_ID: 'is-correct-person',
        SELECT_OBJECT_CLASS_WRAPPER_ID: 'select-object-class-wrapper',
        NEW_ANNOTATION_FORM_ID: 'add-object-class',
        IS_FACE_CHECKBOX_LABEL_ID: 'is-face-label',
        IS_CORRECT_AGE_CHECKBOX_LABEL_ID: 'is-correct-age-label',
        IS_CORRECT_GENDER_CHECKBOX_LABEL_ID: 'is-correct-gender-label',
        PERSON_NAME_FIELDS_WRAPPER_ID: 'person-name-group',
        IS_CORRECT_SUBJECT_NAME_LABEL_ID: 'subject-name',
        IS_OBJECT_CHECKBOX_LABEL_ID: 'is-object-label',
        ALTERNATIVE_OBJECT_SELECT_WRAPPER_ID: 'alternative-object-type-select',
        RE_PHOTO_SHARE_LINK_ID: 'rephoto-share-link',
        IMAGE_SELECTION_AREA_ID: 'image-selection',
        IMAGE_SELECTION_OVERLAY_ID: 'image-selection-overlay',
        ANNOTATION_FILTERS_ID: 'annotation-filters',
        ANNOTATION_CONTAINER_ID_ON_IMAGE: 'annotation-container'
    },
    translations: {
        errors: {
            OBJECT_REQUIRED: gettext('Object is required')
        },
        common: {
            OPTIONAL: gettext('optional'),
            UNSURE: gettext('Unsure')
        },
        button: {
            CANCEL: gettext('Cancel'),
            DELETE: gettext('Delete'),
            SUBMIT: gettext('Submit')
        },
        photoView: {
            links: {
                SHARE_PHOTO: gettext('Photo'),
                SHARE_PHOTO_WITH_RE_PHOTO: gettext('Photo with selected rephoto')
            }
        },
        popover: {
            titles: {
                NEW_ANNOTATION: gettext('What is displayed'),
                EDIT_FACE_ANNOTATION: gettext('Edit face annotation'),
                EDIT_OBJECT_ANNOTATION: gettext('Edit object annotation'),
                EDIT_FEEDBACK: gettext('Edit feedback'),
                ADD_FEEDBACK: gettext('Add feedback'),
                ANNOTATION_ADDED_BY_YOU: gettext('Your annotation info')
            },
            labels: {
                CHANGE_PERSON_NAME: gettext('Change person name'),
                CHANGE_OBJECT_CLASS: gettext('Change object class'),
                FACE_ANNOTATION: gettext('Face'),
                OBJECT_ANNOTATION: gettext('Object'),
                IS_THIS_A_FACE_ANNOTATION: gettext('Is this a face'),
                IS_CORRECT_SUBJECT_NAME_PREFIX: gettext('Is this'),
                IS_CORRECT_OBJECT_PREFIX: gettext('Is this a'),
                IS_CORRECT_AGE_PREFIX: gettext('Is this a'),
                IS_CORRECT_GENDER_PREFIX: gettext('Is this a'),
                OWN_ANNOTATION_FIELD_TYPE: gettext('Annotation type'),
                OWN_ANNOTATION_FIELD_PERSON: gettext('Name'),
                OWN_ANNOTATION_FIELD_OBJECT: gettext('Object type'),
                OWN_ANNOTATION_FIELD_GENDER: gettext('Gender'),
                OWN_ANNOTATION_FIELD_AGE: gettext('Age')
            }
        },
        queries: {
            GET_ANNOTATION_CLASSES_FAILED: gettext('Failed to load object annotation classes'),
            GET_ANNOTATIONS_FAILED: gettext('Failed to load annotations'),
            ADD_ANNOTATION_SUCCESS: gettext('Successfully added object annotation'),
            ADD_ANNOTATION_FAILED: gettext('Unable to save object annotation'),
            UPDATE_OBJECT_ANNOTATION_SUCCESS: gettext('Successfully updated object annotation'),
            UPDATE_OBJECT_ANNOTATION_FAILED: gettext('Unable to update object annotation'),
            ADD_OBJECT_ANNOTATION_FEEDBACK_SUCCESS: gettext('Successfully added object annotation feedback'),
            ADD_OBJECT_ANNOTATION_FEEDBACK_FAILED: gettext('Failed to add object annotation feedback'),
            REMOVE_OBJECT_ANNOTATION_SUCCESS: gettext('Successfully removed object annotation'),
            REMOVE_OBJECT_ANNOTATION_FAILED: gettext('Unable to remove object annotation'),
            ADD_FACE_ANNOTATION_FEEDBACK_SUCCESS: gettext('Successfully added face annotation feedback'),
            ADD_FACE_ANNOTATION_FEEDBACK_FAILED: gettext('Failed to add face annotation feedback'),
            UPDATE_FACE_ANNOTATION_SUCCESS: gettext('Successfully edited face annotation'),
            UPDATE_FACE_ANNOTATION_FAILED: gettext('Failed to save face annotation edit'),
            REMOVE_FACE_ANNOTATION_SUCCESS: gettext('Successfully removed face annotation'),
            REMOVE_FACE_ANNOTATION_FAILED: gettext('Failed to remove face annotation')
        },
        autocomplete: {
            objectSearch: {
                PLACEHOLDER: gettext('Find object'),
                SEARCHING_TEXT: gettext('Searching'),
                SEARCH_PLACEHOLDER: gettext('Search for object'),
                MIN_CHARACTERS_NEEDED: gettext('Need 2 characters'),
                NO_RESULTS_FOUND: gettext('No results found')
            },
            subjectSearch: {
                PLACEHOLDER: gettext('Find existing person'),
                SEARCHING_TEXT: gettext('Searching'),
                SEARCH_PLACEHOLDER: gettext('Enter person name'),
                MIN_CHARACTERS_NEEDED: gettext('Need 2 characters'),
                NO_RESULTS_TEXT: gettext('No results found'),
                ADD_NEW_PERSON: gettext('Add new person')
            },
            label: {
                ADD_NEW_PERSON: gettext('Add new person'),
                SPECIFY_NAME: gettext('Specify person name')
            }
        },
        selectAge: {
            label: {
                SPECIFY_AGE: gettext('Select age group'),
                CHANGE_AGE: gettext('Change age group'),
                SPECIFY_ALTERNATIVE_AGE: gettext('Specify alternative age group')
            }
        },
        selectGender: {
            label: {
                SPECIFY_GENDER: gettext('Select gender'),
                CHANGE_GENDER: gettext('Change gender'),
                SPECIFY_ALTERNATIVE_GENDER: gettext('Specify alternative gender')
            }
        }
    }
};