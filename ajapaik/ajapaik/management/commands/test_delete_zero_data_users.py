import datetime

from django.core.management import BaseCommand

from ajapaik.ajapaik.models import Profile,NotEqual,Area,AlbumPhoto,Album,Photo,ImageSimilarity,ImageSimilaritySuggestion,PhotoMetadataUpdate,PhotoComment,PhotoLike,DifficultyFeedback,Points,Transcription,TranscriptionFeedback,GeoTag,LocationPhoto,Location,FacebookManager,Profile,Source,ProfileMergeToken,Device,Skip,Action,Licence,GoogleMapsReverseGeocode,Dating,DatingConfirmation,Video,ProfileDisplayNameChange,MyXtdComment,WikimediaCommonsUpload,Suggestion,PhotoSceneSuggestion,PhotoViewpointElevationSuggestion,PhotoFlipSuggestion,PhotoInvertSuggestion,PhotoRotationSuggestion,Supporter,MuisCollection,ApplicationException
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle,FaceRecognitionRectangleSubjectDataSuggestion,FaceRecognitionRectangleFeedback,FaceRecognitionUserSuggestion
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionModel,ObjectAnnotationClass,ObjectDetectionAnnotation,ObjectAnnotationFeedback
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import json
import time
from datetime import timedelta
from django.utils import timezone
class Command(BaseCommand):
    help = 'Find and delete profiles/users that have no data attached (just people who have arrived ' \
           'at the page and never done anything)'


    def get_max_ids(self):
        new={}
#        new['NotEqual']=NotEqual.objects.count()
        new['Area']=Area.objects.last().id
        new['AlbumPhoto']=AlbumPhoto.objects.last().id
        new['Album']=Album.objects.last().id
        new['Photo']=Photo.objects.values('id').order_by('-id').first()['id']
        new['ImageSimilarity']=ImageSimilarity.objects.last().id
        new['ImageSimilaritySuggestion']=ImageSimilaritySuggestion.objects.last().id
        new['PhotoMetadataUpdate']=PhotoMetadataUpdate.objects.last().id
        new['PhotoComment']=PhotoComment.objects.last().id
        new['PhotoLike']=PhotoLike.objects.last().id
        new['DifficultyFeedback']=DifficultyFeedback.objects.last().id
        new['Points']=Points.objects.last().id
        new['Transcription']=Transcription.objects.last().id
        new['TranscriptionFeedback']=TranscriptionFeedback.objects.last().id
        new['GeoTag']=GeoTag.objects.last().id
        new['LocationPhoto']=LocationPhoto.objects.last().id
        new['Location']=Location.objects.last().id
#        new['FacebookManager']=FacebookManager.objects.count()
        new['Profile']=Profile.objects.values('user_id').order_by('-user_id').first()['user_id']
        new['Source']=Source.objects.last().id
        new['ProfileMergeToken']=ProfileMergeToken.objects.last().id
        new['Device']=Device.objects.last().id
        new['Skip']=Skip.objects.last().id
#        new['Action']=Action.objects.count()
        new['Licence']=Licence.objects.last().id
        new['GoogleMapsReverseGeocode']=GoogleMapsReverseGeocode.objects.last().id
        new['Dating']=Dating.objects.last().id
        new['DatingConfirmation']=DatingConfirmation.objects.last().id
        new['Video']=Video.objects.last().id
        new['ProfileDisplayNameChange']=ProfileDisplayNameChange.objects.last().id
        new['MyXtdComment']=MyXtdComment.objects.last().id
#        new['WikimediaCommonsUpload']=WikimediaCommonsUpload.objects.last().photo
#        new['Suggestion']=Suggestion.objects.count()
        new['PhotoSceneSuggestion']=PhotoSceneSuggestion.objects.last().id
        new['PhotoViewpointElevationSuggestion']=PhotoViewpointElevationSuggestion.objects.last().id
        new['PhotoFlipSuggestion']=PhotoFlipSuggestion.objects.last().id
        new['PhotoInvertSuggestion']=PhotoInvertSuggestion.objects.last().id
        new['PhotoRotationSuggestion']=PhotoRotationSuggestion.objects.last().id
        new['Supporter']=Supporter.objects.last().id
        new['MuisCollection']=MuisCollection.objects.last().id
        new['ApplicationException']=ApplicationException.objects.last().id
        new['FaceRecognitionRectangle']=FaceRecognitionRectangle.objects.last().id
        new['FaceRecognitionRectangleSubjectDataSuggestion']=FaceRecognitionRectangleSubjectDataSuggestion.objects.last().id
        new['FaceRecognitionRectangleFeedback']=FaceRecognitionRectangleFeedback.objects.last().id
        new['FaceRecognitionUserSuggestion']=FaceRecognitionUserSuggestion.objects.last().id
        new['ObjectDetectionModel']=ObjectDetectionModel.objects.last().id
        new['ObjectAnnotationClass']=ObjectAnnotationClass.objects.last().id
        new['ObjectDetectionAnnotation']=ObjectDetectionAnnotation.objects.last().id
#        new['ObjectAnnotationFeedback']=ObjectAnnotationFeedback.objects.last().id

        return new


    def get_counts(self, old):
        new={}
#        new['NotEqual']=NotEqual.objects.count()
        new['Area']=Area.objects.count()
        new['AlbumPhoto']=AlbumPhoto.objects.count()
        new['Album']=Album.objects.count()
        new['Photo']=Photo.objects.count()
        new['ImageSimilarity']=ImageSimilarity.objects.count()
        new['ImageSimilaritySuggestion']=ImageSimilaritySuggestion.objects.count()
        new['PhotoMetadataUpdate']=PhotoMetadataUpdate.objects.count()
        new['PhotoComment']=PhotoComment.objects.count()
        new['PhotoLike']=PhotoLike.objects.count()
        new['DifficultyFeedback']=DifficultyFeedback.objects.count()
        new['Points']=Points.objects.count()
        new['Transcription']=Transcription.objects.count()
        new['TranscriptionFeedback']=TranscriptionFeedback.objects.count()
        new['GeoTag']=GeoTag.objects.count()
        new['LocationPhoto']=LocationPhoto.objects.count()
        new['Location']=Location.objects.count()
#        new['FacebookManager']=FacebookManager.objects.count()
        new['Profile']=Profile.objects.count()
        new['Source']=Source.objects.count()
        new['ProfileMergeToken']=ProfileMergeToken.objects.count()
        new['Device']=Device.objects.count()
        new['Skip']=Skip.objects.count()
#        new['Action']=Action.objects.count()
        new['Licence']=Licence.objects.count()
        new['GoogleMapsReverseGeocode']=GoogleMapsReverseGeocode.objects.count()
        new['Dating']=Dating.objects.count()
        new['DatingConfirmation']=DatingConfirmation.objects.count()
        new['Video']=Video.objects.count()
        new['ProfileDisplayNameChange']=ProfileDisplayNameChange.objects.count()
        new['MyXtdComment']=MyXtdComment.objects.count()
        new['WikimediaCommonsUpload']=WikimediaCommonsUpload.objects.count()
#        new['Suggestion']=Suggestion.objects.count()
        new['PhotoSceneSuggestion']=PhotoSceneSuggestion.objects.count()
        new['PhotoViewpointElevationSuggestion']=PhotoViewpointElevationSuggestion.objects.count()
        new['PhotoFlipSuggestion']=PhotoFlipSuggestion.objects.count()
        new['PhotoInvertSuggestion']=PhotoInvertSuggestion.objects.count()
        new['PhotoRotationSuggestion']=PhotoRotationSuggestion.objects.count()
        new['Supporter']=Supporter.objects.count()
        new['MuisCollection']=MuisCollection.objects.count()
        new['ApplicationException']=ApplicationException.objects.count()
        new['FaceRecognitionRectangle']=FaceRecognitionRectangle.objects.count()
        new['FaceRecognitionRectangleSubjectDataSuggestion']=FaceRecognitionRectangleSubjectDataSuggestion.objects.count()
        new['FaceRecognitionRectangleFeedback']=FaceRecognitionRectangleFeedback.objects.count()
        new['FaceRecognitionUserSuggestion']=FaceRecognitionUserSuggestion.objects.count()
        new['ObjectDetectionModel']=ObjectDetectionModel.objects.count()
        new['ObjectAnnotationClass']=ObjectAnnotationClass.objects.count()
        new['ObjectDetectionAnnotation']=ObjectDetectionAnnotation.objects.count()
        new['ObjectAnnotationFeedback']=ObjectAnnotationFeedback.objects.count()

        if old!=None:
            for classname in new:
                if classname=="Profile":
                    print("DELETED\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname]) )
                elif old[classname]!=new[classname]:
                    print("ERROR\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname])  )
#                else:
#                    print("OK\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname]) )


        return new
        #,NotEqual,Area,AlbumPhoto,Album,Photo,ImageSimilarity,ImageSimilaritySuggestion,PhotoMetadataUpdate,PhotoComment,PhotoLike,DifficultyFeedback,Points,Transcription,TranscriptionFeedback,GeoTag,LocationPhoto,Location,FacebookManager,Profile,Source,ProfileMergeToken,Device,Skip,Action,Licence,GoogleMapsReverseGeocode,Dating,DatingConfirmation,Video,ProfileDisplayNameChange,MyXtdComment,WikimediaCommonsUpload,Suggestion,PhotoSceneSuggestion,PhotoViewpointElevationSuggestion,PhotoFlipSuggestion,PhotoInvertSuggestion,PhotoRotationSuggestion,Supporter,MuisCollection,ApplicationException,FaceRecognitionRectangle,FaceRecognitionRectangleSubjectDataSuggestion,FaceRecognitionRectangleFeedback,FaceRecognitionUserSuggestion

    def get_counts_filter(self, old, max):
        new={}
#        new['NotEqual']=NotEqual.objects.count()
        new['Area']=Area.objects.filter(pk__lte=max['Area']).count()
        new['AlbumPhoto']=AlbumPhoto.objects.filter(pk__lte=max['AlbumPhoto']).count()
        new['Album']=Album.objects.filter(pk__lte=max['Album']).count()
        new['Photo']=Photo.objects.filter(pk__lte=max['Photo']).count()
        new['ImageSimilarity']=ImageSimilarity.objects.filter(pk__lte=max['ImageSimilarity']).count()
        new['ImageSimilaritySuggestion']=ImageSimilaritySuggestion.objects.filter(pk__lte=max['ImageSimilaritySuggestion']).count()
        new['PhotoMetadataUpdate']=PhotoMetadataUpdate.objects.filter(pk__lte=max['PhotoMetadataUpdate']).count()
        new['PhotoComment']=PhotoComment.objects.filter(pk__lte=max['PhotoComment']).count()
        new['PhotoLike']=PhotoLike.objects.filter(pk__lte=max['PhotoLike']).count()
        new['DifficultyFeedback']=DifficultyFeedback.objects.filter(pk__lte=max['DifficultyFeedback']).count()
        new['Points']=Points.objects.filter(pk__lte=max['Points']).count()
        new['Transcription']=Transcription.objects.filter(pk__lte=max['Transcription']).count()
        new['TranscriptionFeedback']=TranscriptionFeedback.objects.filter(pk__lte=max['TranscriptionFeedback']).count()
        new['GeoTag']=GeoTag.objects.filter(pk__lte=max['GeoTag']).count()
        new['LocationPhoto']=LocationPhoto.objects.filter(pk__lte=max['LocationPhoto']).count()
        new['Location']=Location.objects.filter(pk__lte=max['Location']).count()
#        new['FacebookManager']=FacebookManager.objects.count()
        new['Profile']=Profile.objects.filter(user_id__lte=max['Profile']).count()
        new['Source']=Source.objects.filter(pk__lte=max['Source']).count()
        new['ProfileMergeToken']=ProfileMergeToken.objects.filter(pk__lte=max['ProfileMergeToken']).count()
        new['Device']=Device.objects.filter(pk__lte=max['Device']).count()
        new['Skip']=Skip.objects.filter(pk__lte=max['Skip']).count()
#        new['Action']=Action.objects.count()
        new['Licence']=Licence.objects.filter(pk__lte=max['Licence']).count()
        new['GoogleMapsReverseGeocode']=GoogleMapsReverseGeocode.objects.filter(pk__lte=max['GoogleMapsReverseGeocode']).count()
        new['Dating']=Dating.objects.filter(pk__lte=max['Dating']).count()
        new['DatingConfirmation']=DatingConfirmation.objects.filter(pk__lte=max['DatingConfirmation']).count()
        new['Video']=Video.objects.filter(pk__lte=max['Video']).count()
        new['ProfileDisplayNameChange']=ProfileDisplayNameChange.objects.filter(pk__lte=max['ProfileDisplayNameChange']).count()
        new['MyXtdComment']=MyXtdComment.objects.filter(pk__lte=max['MyXtdComment']).count()
##        new['WikimediaCommonsUpload']=WikimediaCommonsUpload.objects.filter(pk__lte=max['WikimediaCommonsUpload']).count()
#        new['Suggestion']=Suggestion.objects.count()
        new['PhotoSceneSuggestion']=PhotoSceneSuggestion.objects.filter(pk__lte=max['PhotoSceneSuggestion']).count()
        new['PhotoViewpointElevationSuggestion']=PhotoViewpointElevationSuggestion.objects.filter(pk__lte=max['PhotoViewpointElevationSuggestion']).count()
        new['PhotoFlipSuggestion']=PhotoFlipSuggestion.objects.filter(pk__lte=max['PhotoFlipSuggestion']).count()
        new['PhotoInvertSuggestion']=PhotoInvertSuggestion.objects.filter(pk__lte=max['PhotoInvertSuggestion']).count()
        new['PhotoRotationSuggestion']=PhotoRotationSuggestion.objects.filter(pk__lte=max['PhotoRotationSuggestion']).count()
        new['Supporter']=Supporter.objects.filter(pk__lte=max['Supporter']).count()
        new['MuisCollection']=MuisCollection.objects.filter(pk__lte=max['MuisCollection']).count()
        new['ApplicationException']=ApplicationException.objects.filter(pk__lte=max['ApplicationException']).count()
        new['FaceRecognitionRectangle']=FaceRecognitionRectangle.objects.filter(pk__lte=max['FaceRecognitionRectangle']).count()
        new['FaceRecognitionRectangleSubjectDataSuggestion']=FaceRecognitionRectangleSubjectDataSuggestion.objects.filter(pk__lte=max['FaceRecognitionRectangleSubjectDataSuggestion']).count()
        new['FaceRecognitionRectangleFeedback']=FaceRecognitionRectangleFeedback.objects.filter(pk__lte=max['FaceRecognitionRectangleFeedback']).count()
        new['FaceRecognitionUserSuggestion']=FaceRecognitionUserSuggestion.objects.filter(pk__lte=max['FaceRecognitionUserSuggestion']).count()
        new['ObjectDetectionModel']=ObjectDetectionModel.objects.filter(pk__lte=max['ObjectDetectionModel']).count()
        new['ObjectAnnotationClass']=ObjectAnnotationClass.objects.filter(pk__lte=max['ObjectAnnotationClass']).count()
        new['ObjectDetectionAnnotation']=ObjectDetectionAnnotation.objects.filter(pk__lte=max['ObjectDetectionAnnotation']).count()
##        new['ObjectAnnotationFeedback']=ObjectAnnotationFeedback.objects.filter(pk__lte=max['ObjectAnnotationFeedback']).count()

        if old!=None:
            for classname in new:
                if classname=="Profile":
                    print("DELETED\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname]) )
                elif old[classname]!=new[classname]:
                    print("ERROR\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname])  )
                else:
                    print("OK\t" + "diff: " + str(new[classname]-old[classname]) + "\t" + classname + "\t" + "old: " + str(old[classname]) +"\t" + "new: " + str(new[classname]) )


        return new



    def handle(self, *args, **options):
#        for relation in Profile._meta.related_objects:
#            print(relation.related_model)
#            print(relation.model)
#            print(relation.field.name)

        max_ids=self.get_max_ids()
        counts=self.get_counts(None)
#        if 1:
#            return
        time_threshold = timezone.now() - timedelta(days=90)
        profiles = Profile.objects.filter(
            score=0,
            score_rephoto=0,
            score_recent_activity=0,
            modified__lte=time_threshold,
            # Own fields
            first_name__isnull=True,
            last_name__isnull=True,

            fb_name__isnull=True,
            fb_link__isnull=True,
            fb_id__isnull=True,
            fb_token__isnull=True,
            fb_hometown__isnull=True,
            fb_current_location__isnull=True,
            fb_birthday__isnull=True,
            fb_email__isnull=True,
            fb_user_friends__isnull=True,

            google_plus_id__isnull=True,
            google_plus_email__isnull=True,
            google_plus_link__isnull=True,
            google_plus_name__isnull=True,
            google_plus_token__isnull=True,
            google_plus_picture__isnull=True,

            deletion_attempted__isnull=True,

            # Related model fields
            photos__isnull=True,
            albums__isnull=True,
            album_photo_links__isnull=True,
            datings__isnull=True,
            dating_confirmations__isnull=True,
            difficulty_feedbacks__isnull=True,
            geotags__isnull=True,
            points__isnull=True,
            skips__isnull=True,
            likes__isnull=True,
            user_last_modified__isnull=True,
            image_similarity_proposer__isnull=True,
            transcriptions__isnull=True,
            transcription_feedback__isnull=True,
            profile_merge_tokens__isnull=True,
            merged_from_profile__isnull=True,
            merged_into_profile__isnull=True,
            display_name_changes__isnull=True,
            photo_scene_suggestions__isnull=True,
            photo_viewpoint_elevation_suggestions__isnull=True,
            photo_flip_suggestions__isnull=True,
            photo_invert_suggestions__isnull=True,
            photo_rotate_suggestions__isnull=True,
            supporter__isnull=True,

            face_recognition_rectangles__isnull=True,
            subject_data_proposer__isnull=True,
            face_recognition_rectangle_feedback__isnull=True,
            face_recognition_suggestions__isnull=True,

#    profile = ForeignKey('Profile', blank=True, null=True, related_name='album_photo_links', on_delete=CASCADE)
#    profile = ForeignKey('Profile', related_name='albums', blank=True, null=True, on_delete=CASCADE)
#    user = ForeignKey('Profile', related_name='photos', blank=True, null=True, on_delete=CASCADE)
#    user_last_modified = ForeignKey('Profile', related_name='user_last_modified', null=True, on_delete=CASCADE)
#    proposer = ForeignKey('Profile', on_delete=CASCADE, related_name='image_similarity_proposer', null=True, blank=True)
#    profile = ForeignKey('Profile', related_name='likes', on_delete=CASCADE)
#    user_profile = ForeignKey('Profile', related_name='difficulty_feedbacks', on_delete=CASCADE)
#    user = ForeignKey('Profile', related_name='points', on_delete=CASCADE)
#   user = ForeignKey('Profile', related_name='transcriptions', on_delete=CASCADE)
#    user = ForeignKey('Profile', related_name='transcription_feedback', on_delete=CASCADE)
#    user = ForeignKey('Profile', related_name='geotags', null=True, blank=True, on_delete=CASCADE)
#    profile = ForeignKey('Profile', related_name='profile_merge_tokens', on_delete=CASCADE)
#    source_profile = ForeignKey('Profile', blank=True, null=True, related_name='merged_from_profile', on_delete=CASCADE)
#    target_profile = ForeignKey('Profile', blank=True, null=True, related_name='merged_into_profile', on_delete=CASCADE)
#    user = ForeignKey('Profile', related_name='skips', on_delete=CASCADE)
#    profile = ForeignKey('Profile', blank=True, null=True, related_name='datings', on_delete=CASCADE)
#    profile = ForeignKey('Profile', related_name='dating_confirmations', on_delete=CASCADE)
#    profile = ForeignKey('Profile', related_name='display_name_changes', on_delete=CASCADE)
#    proposer = ForeignKey('Profile', blank=True, null=True, related_name='photo_scene_suggestions', on_delete=CASCADE)
#    proposer = ForeignKey('Profile', blank=True, null=True, related_name='photo_viewpoint_elevation_suggestions',
#    proposer = ForeignKey('Profile', blank=True, null=True, related_name='photo_flip_suggestions', on_delete=CASCADE)
#    proposer = ForeignKey('Profile', blank=True, null=True, related_name='photo_invert_suggestions', on_delete=CASCADE)
#    proposer = ForeignKey('Profile', blank=True, null=True, related_name='photo_rotate_suggestions', on_delete=CASCADE)
#    profile = ForeignKey('Profile', blank=True, null=True, related_name='supporter', on_delete=CASCADE)


##
#    user = models.ForeignKey(Profile, blank=True, null=True, on_delete=CASCADE,
#    proposer = models.ForeignKey(Profile, on_delete=CASCADE, related_name='subject_data_proposer')
#    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_rectangle_feedback')
#    user = models.ForeignKey(Profile, on_delete=CASCADE, related_name='face_recognition_suggestions', blank=True,

##
#    detection_model = models.ForeignKey(ObjectDetectionModel, on_delete=CASCADE)
#    photo = models.ForeignKey(Photo, on_delete=CASCADE)
#    detected_object = models.ForeignKey(ObjectAnnotationClass, on_delete=CASCADE)
#    user = models.ForeignKey(Profile, on_delete=CASCADE)
#    object_detection_annotation = models.ForeignKey(ObjectDetectionAnnotation, related_name='feedback',
#    alternative_object = models.ForeignKey(ObjectAnnotationClass, null=True, on_delete=CASCADE)
#    user = models.ForeignKey(Profile, on_delete=CASCADE)


        )
        starttime = time.time()
        used_time=0
        for user_id in profiles.values_list('user_id', flat=True)[:500000]:
            try:
                starttime2 = time.time()
                p=Profile.objects.get(pk=user_id)
                dict_obj = model_to_dict( p )
                t=json.dumps(dict_obj)
#                print(t)
#                print(p.modified)
#                print(p.user.username)
                u=User.objects.filter(
			pk=user_id,
                        last_login__lte=time_threshold,
                        date_joined__lte=time_threshold,
			first_name__exact='',
			last_name__exact='',
			email__exact=''
		).first()

                if u:
                    time_diff=(u.last_login-u.date_joined).total_seconds()
#                    print(time_diff)
                    if (time_diff<1):
                        print("delete user: %d %s" % (user_id, u) )
                        p.user.delete()

#                        u2=User.objects.get(pk=user_id)
#                        if u2:
#                            print("user exists: %s" % ( u) )
#                            print("* 5a : " + str(time.time() - starttime2)) 
#                            return
                else:
                    print("skipped: %s" % (p) )
                used_time=used_time+(time.time() - starttime2)
#                print("* 5 : " + str(time.time() - starttime2)) 


            except:  # noqa
                p.deletion_attempted = datetime.datetime.now()
                p.save()
                print("Failed")
                return

        print("* 6 : " + str((time.time() - starttime)/60)) 
        print("* 7 : " + str((used_time)/60) )
        time.sleep(2)

        counts_t=self.get_counts(counts)
        counts_t2=self.get_counts_filter(counts,max_ids)
        counts_t=self.get_counts(counts)
