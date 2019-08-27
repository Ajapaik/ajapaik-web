'use strict';

var constants = {
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
        IMAGE_SELECTION_AREA_ID: 'image-selection'
    },
    translations: {
        common: {
            OPTIONAL: 'optional'
        },
        button: {
            CANCEL: 'Cancel',
            DELETE: 'Delete',
            SUBMIT: 'Submit'
        },
        photoView: {
            links: {
                SHARE_PHOTO: 'Photo',
                SHARE_PHOTO_WITH_RE_PHOTO: 'Photo with selected rephoto'
            }
        },
        popover: {
            titles: {
                NEW_ANNOTATION: 'What is displayed',
                EDIT_FACE_ANNOTATION: 'Edit face annotation',
                EDIT_OBJECT_ANNOTATION: 'Edit object annotation',
                EDIT_FEEDBACK: 'Edit feedback',
                ADD_FEEDBACK: 'Add feedback'
            },
            labels: {
                CHANGE_PERSON_NAME: 'Change person name',
                CHANGE_OBJECT_CLASS: 'Change object class',
                FACE_ANNOTATION: 'Face',
                OBJECT_ANNOTATION: 'Object',
                IS_THIS_A_FACE_ANNOTATION: 'Is this a face',
                IS_CORRECT_SUBJECT_NAME_PREFIX: 'Is this'
            }
        },
        queries: {
            GET_ANNOTATION_CLASSES_FAILED: 'Failed to load object annotation classes',
            GET_ANNOTATIONS_FAILED: 'Failed to load annotations',
            ADD_ANNOTATION_SUCCESS: 'Successfully added object annotation',
            ADD_ANNOTATION_FAILED: 'Unable to save object annotation',
            UPDATE_OBJECT_ANNOTATION_SUCCESS: 'Successfully updated object annotation',
            UPDATE_OBJECT_ANNOTATION_FAILED: 'Unable to update object annotation',
            ADD_OBJECT_ANNOTATION_FEEDBACK_SUCCESS: 'Successfully added object annotation feedback',
            ADD_OBJECT_ANNOTATION_FEEDBACK_FAILED: 'Failed to add object annotation feedback',
            REMOVE_OBJECT_ANNOTATION_SUCCESS: 'Successfully removed object annotation',
            REMOVE_OBJECT_ANNOTATION_FAILED: 'Unable to remove object annotation',
            ADD_FACE_ANNOTATION_FEEDBACK_SUCCESS: 'Successfully added face annotation feedback',
            ADD_FACE_ANNOTATION_FEEDBACK_FAILED: 'Failed to add face annotation feedback',
            UPDATE_FACE_ANNOTATION_SUCCESS: 'Successfully edited face annotation',
            UPDATE_FACE_ANNOTATION_FAILED: 'Failed to save face annotation edit',
            REMOVE_FACE_ANNOTATION_SUCCESS: 'Successfully removed face annotation',
            REMOVE_FACE_ANNOTATION_FAILED: 'Failed to remove face annotation'
        },
        autocomplete: {
            subjectSearch: {
                PLACEHOLDER: 'Find existing person',
                SEARCHING_TEXT: 'Searching',
                SEARCH_PLACEHOLDER: 'Enter person name',
                MIN_CHARACTERS_NEEDED: 'Need 2 characters',
                NO_RESULTS_TEXT: 'No results found.',
                ADD_NEW_PERSON: 'Add new person.'
            },
            label: {
                ADD_NEW_PERSON: 'Add new person',
                SPECIFY_NAME: 'Specify person name'
            }
        }
    }
};