

class AddAdditionalSubjectData:
    gender = None
    age = None
    subject_annotation_rectangle_id = None

    def __init__(self, subject_rectangle_id: int, age: int, gender: int):
        self.subject_annotation_rectangle_id = subject_rectangle_id
        self.age = age
        self.gender = gender
