
class FaceAnnotationRemoveRequest:
    def __init__(self, annotation_id: int, user_id: int):
        self.user_id = user_id
        self.annotation_id = annotation_id
