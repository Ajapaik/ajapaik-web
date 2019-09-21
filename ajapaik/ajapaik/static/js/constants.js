'use strict';

var constants = {
    keyCodes: {
        ESCAPE: 27
    },
    elements: {
        AUTOCOMPLETE_WRAPPER_ID: 'autocomplete-wrapper',
        SUBJECT_AUTOCOMPLETE_ID: 'autocomplete-subject',
        ADD_NEW_SUBJECT_LINK_ID: 'add-new-subject',
        POPOVER_CONTROL_BUTTONS_ID: 'control-buttons',
        OBJECT_CLASS_SELECT_ID: 'select-object-class',
        IS_CORRECT_OBJECT_CHECKBOX_ID: 'is-correct-object',
        IS_FACE_ANNOTATION_CHECKBOX_ID: 'is-face-annotation',
        IS_CORRECT_PERSON_NAME_CHECKBOX_ID: 'is-correct-person',
        SELECT_OBJECT_CLASS_WRAPPER_ID: 'select-object-class-wrapper',
        NEW_ANNOTATION_FORM_ID: 'add-object-class',
        IS_FACE_CHECKBOX_LABEL_ID: 'is-face-label',
        PERSON_NAME_FIELDS_WRAPPER_ID: 'person-name-group',
        IS_CORRECT_SUBJECT_NAME_LABEL_ID: 'subject-name',
        IS_OBJECT_CHECKBOX_LABEL_ID: 'is-object-label',
        ALTERNATIVE_OBJECT_SELECT_WRAPPER_ID: 'alternative-object-type-select',
        RE_PHOTO_SHARE_LINK_ID: 'rephoto-share-link',
        IMAGE_SELECTION_AREA_ID: 'image-selection',
        IMAGE_SELECTION_OVERLAY_ID: 'image-selection-overlay',
        ANNOTATION_FILTERS_ID: 'annotation-filters'
    },
    translations: {
        common: {
            OPTIONAL: gettext('optional')
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
                ADD_FEEDBACK: gettext('Add feedback')
            },
            labels: {
                CHANGE_PERSON_NAME: gettext('Change person name'),
                CHANGE_OBJECT_CLASS: gettext('Change object class'),
                FACE_ANNOTATION: gettext('Face'),
                OBJECT_ANNOTATION: gettext('Object'),
                IS_THIS_A_FACE_ANNOTATION: gettext('Is this a face'),
                IS_CORRECT_SUBJECT_NAME_PREFIX: gettext('Is this'),
                IS_CORRECT_OBJECT_PREFIX: gettext('Is this a')
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
        }
    }
};