from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_gender_to_constant, parse_age_to_constant


def get_if_key_present(data, key):
    if key in data:
        return data[key]

    return None


class DetectionRectangle:
    def __init__(self, init):
        previous_feedback = init['previous_feedback']

        self.id = init['id']

        self.x1 = init['x1']
        self.y1 = init['y1']
        self.x2 = init['x2']
        self.y2 = init['y2']

        self.age = get_if_key_present(init, 'age')
        self.gender = get_if_key_present(init, 'gender')
        self.subjectId = get_if_key_present(init, 'subject_id')
        self.subjectName = get_if_key_present(init, 'subject_name')
        self.wikiDataId = get_if_key_present(init, 'wiki_data_id')
        self.translations = get_if_key_present(init, 'translations')
        self.isDeletable = get_if_key_present(init, 'is_deletable')
        self.hasUserGivenFeedback = get_if_key_present(init, 'has_user_given_feedback')
        self.isAddedByCurrentUser = get_if_key_present(init, 'is_added_by_current_user')

        self.previousFeedback = {
            'isFace': get_if_key_present(previous_feedback, 'is_face'),
            'isCorrectName': get_if_key_present(previous_feedback, 'is_correct_name'),
            'name': get_if_key_present(previous_feedback, 'name'),
            'age': parse_age_to_constant(get_if_key_present(previous_feedback, 'age')),
            'gender': parse_gender_to_constant(get_if_key_present(previous_feedback, 'gender')),

            'isCorrectObject': get_if_key_present(previous_feedback, 'is_correct_object'),
            'alternativeObjectId': get_if_key_present(previous_feedback, 'alternative_object_id'),
            'alternativeObjectTranslations': get_if_key_present(previous_feedback, 'alternative_object_translations'),
            'isCorrectAge': get_if_key_present(previous_feedback, 'is_correct_age'),
            'isCorrectGender': get_if_key_present(previous_feedback, 'is_correct_gender'),
            'subjectId': get_if_key_present(previous_feedback, 'subject_id'),
            'subjectName': get_if_key_present(previous_feedback, 'subject_name')
        }
