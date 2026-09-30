'use strict';

var constants = {
    keyCodes: {
        ESCAPE: 27,
        D: 68,
        ARROW_RIGHT: 39,
        ARROW_LEFT: 37,
    },
    fieldValues: {
        common: {
            UNSURE: 'UNSURE',
        },
        genders: {
            MALE: 'MALE',
            FEMALE: 'FEMALE',
        },
        ageGroups: {
            CHILD: 'CHILD',
            ADULT: 'ADULT',
            ELDERLY: 'ELDERLY',
        },
    },
    elements: {
        NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID:
            'new-object-select-fields-wrapper-id',
        ANNOTATION_MORE_SPECIFIC_FIELDS_WRAPPER_ID:
            'more-specific-annotation-fields-wrapper',
        AUTOCOMPLETE_WRAPPER_ID: 'autocomplete-wrapper',
        SUBJECT_AUTOCOMPLETE_ID: 'autocomplete-subject',
        SUBJECT_GENDER_SUGGESTION_COMPONENT_ID: 'person-popover-gender-suggestion',
        SUBJECT_AGE_GROUP_SUGGESTION_COMPONENT_ID:
            'person-popover-age-group-suggestion',
        ADD_NEW_FACE_FIELDS_WRAPPER_ID: 'add-new-subject-fields-wrapper',
        ADD_NEW_SUBJECT_LINK_ID: 'add-new-subject',
        POPOVER_CONTROL_BUTTONS_ID: 'control-buttons',
        OBJECT_CLASS_SELECT_ID: 'select-object-class',
        SELECT_OBJECT_CLASS_WRAPPER_ID: 'select-object-class-wrapper',
        NEW_ANNOTATION_FORM_ID: 'add-object-class',
        IMAGE_SELECTION_AREA_ID: 'image-selection',
        IMAGE_SELECTION_OVERLAY_ID: 'image-selection-overlay',
        FACE_ANNOTATIONS_ID: 'person-annotations',
        OBJECT_ANNOTATIONS_ID: 'object-annotations',
        ANNOTATION_CONTAINER_ID_ON_IMAGE: 'annotation-container',
    },
    translations: {
        annotations: {
            INFORM_HOW_TO_ANNOTATE: gettext(
                'Click (don\'t drag) to start drawing the annotation. Click again to finish drawing.',
            ),
        },
        errors: {
            OBJECT_REQUIRED: gettext('Object is required'),
        },
        common: {
            OPTIONAL: gettext('optional'),
            UNIDENTIFIED: gettext('Unidentified'),
            MALE: gettext('Male'),
            FEMALE: gettext('Female'),
            CHILD: gettext('Child'),
            ELDERLY: gettext('Elderly'),
            ADULT: gettext('Adult'),
        },
        button: {
            CANCEL: gettext('Cancel'),
            DELETE: gettext('Delete'),
            SUBMIT: gettext('Submit'),
        },
        popover: {
            titles: {
                NEW_ANNOTATION: gettext('What is displayedsss'),
                EDIT_FACE_ANNOTATION: gettext('Edit face annotation'),
                EDIT_OBJECT_ANNOTATION: gettext('Edit object annotation'),
                ADD_FEEDBACK: gettext('Add feedback'),
            },
            labels: {
                CHANGE_PERSON_NAME: gettext('Change person name'),
                CHANGE_OBJECT_CLASS: gettext('Change object class'),
                FACE_ANNOTATION: gettext('Face'),
                OBJECT_ANNOTATION: gettext('Object'),
            },
        },
        queries: {
            GET_ANNOTATION_CLASSES_FAILED: gettext(
                'Failed to load object annotation classes',
            ),
            GET_ANNOTATIONS_FAILED: gettext('Failed to load annotations'),
            ADD_OBJECT_ANNOTATION_SUCCESS: gettext(
                'Successfully added object annotation',
            ),
            ADD_OBJECT_ANNOTATION_FAILED: gettext('Unable to save object annotation'),
            UPDATE_OBJECT_ANNOTATION_SUCCESS: gettext(
                'Successfully updated object annotation',
            ),
            UPDATE_OBJECT_ANNOTATION_FAILED: gettext(
                'Unable to update object annotation',
            ),
            ADD_OBJECT_ANNOTATION_FEEDBACK_SUCCESS: gettext(
                'Successfully added object annotation feedback',
            ),
            ADD_OBJECT_ANNOTATION_FEEDBACK_FAILED: gettext(
                'Failed to add object annotation feedback',
            ),
            REMOVE_OBJECT_ANNOTATION_SUCCESS: gettext(
                'Successfully removed object annotation',
            ),
            REMOVE_OBJECT_ANNOTATION_FAILED: gettext(
                'Unable to remove object annotation',
            ),
            ADD_FACE_ANNOTATION_SUCCESS: gettext(
                'Successfully added face annotation',
            ),
            ADD_FACE_ANNOTATION_FAILED: gettext('Unable to save face annotation'),
            UPDATE_FACE_ANNOTATION_SUCCESS: gettext(
                'Successfully edited face annotation',
            ),
            UPDATE_FACE_ANNOTATION_FAILED: gettext(
                'Failed to save face annotation edit',
            ),
            REMOVE_FACE_ANNOTATION_SUCCESS: gettext(
                'Successfully removed face annotation',
            ),
            REMOVE_FACE_ANNOTATION_FAILED: gettext(
                'Failed to remove face annotation',
            ),
        },
        autocomplete: {
            objectSearch: {
                PLACEHOLDER: gettext('Find object'),
                SEARCHING_TEXT: gettext('Searching'),
                SEARCH_PLACEHOLDER: gettext('Search for object'),
                MIN_CHARACTERS_NEEDED: gettext('Need 2 characters'),
                NO_RESULTS_FOUND: gettext('No results found'),
            },
            subjectSearch: {
                PLACEHOLDER: gettext('Find existing person'),
                SEARCHING_TEXT: gettext('Searching'),
                SEARCH_PLACEHOLDER: gettext('Enter person name'),
                MIN_CHARACTERS_NEEDED: gettext('Need 2 characters'),
                NO_RESULTS_TEXT: gettext('No results found'),
                ADD_NEW_PERSON: gettext('Add new person'),
            },
            label: {
                ADD_NEW_PERSON: gettext('Add new person'),
                SPECIFY_NAME: gettext('Specify person name'),
            },
        },
    },
};
