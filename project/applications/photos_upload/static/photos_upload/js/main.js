const store = new Vuex.Store({
    state: {
        photos: [],
        user: {},
        licences: [],
        templateData: {
            name: '',
            description: '',
            // Geographical centre of Estonia
            longitude: 25.573888888888888,  // 25°34'26"E
            latitude: 58.657777777777774,  // 58°39'28"N
            azimuth: 0,
            isUserAuthor: false,
            selectedLicence: null,
            selectedAlbums: []
        },
        uploadStatus: 'waiting',  // Possible values:
                                  // waiting - waiting for user start upload of
                                  //           photos.
                                  // uploading - photos upload in progress.
                                  // success - photos successfully uploaded.
                                  // failure - malfunction during photos upload.
    },
    mutations: {
        addPhotoFromFile: (state, {file}) => {
            var name = file.name;
            if (state.templateData.name) {
                name = `${state.templateData.name} ${state.photos.length + 1}`;
            }
            let photo = {
                originalFileName: file.name,
                name: name,
                image: null,
                description: state.templateData.description,
                longitude: state.templateData.longitude,
                latitude: state.templateData.latitude,
                azimuth: state.templateData.azimuth,
                isUserAuthor: state.templateData.isUserAuthor,
                licence: state.templateData.selectedLicence,
                albums: state.templateData.selectedAlbums,
                raw_file: file,
            };
            let reader = new FileReader();

            reader.onload = function(photo) {
                return function(event){
                    photo.image = event.target.result;
                }
            }(photo);

            reader.readAsDataURL(file);
            state.photos.push(photo);
        },

        setUserProfile: (state, profile) => {state.user = profile;},

        setLicences: (state, licences) => {state.licences = licences;},

        massive_name_editing: (state, name) => {
            state.templateData.name = name;
            for(var i = 0; i < state.photos.length; i++) {
                photo = state.photos[i];
                if (name) {
                    photo.name = `${name} ${i + 1}`;
                } else {
                    photo.name = photo.originalFileName;
                }
            }
        },

        massive_description_editing: (state, description) => {
            state.templateData.description = description;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].description = description;
            }
        },

        massive_longitude_editing: (state, longitude) => {
            state.templateData.longitude = longitude;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].longitude = longitude;
            }
        },

        massive_latitude_editing: (state, latitude) => {
            state.templateData.latitude = latitude;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].latitude = latitude;
            }
        },
        massive_azimuth_editing: (state, azimuth) => {
            state.templateData.azimuth = azimuth;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].azimuth = azimuth;
            }
        },
        massive_is_author_editing: (state, isUserAuthor) => {
            state.templateData.isUserAuthor = isUserAuthor;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].isUserAuthor = isUserAuthor;
            }
        },
        massive_selected_licence_editing: (state, selectedLicence) => {
            state.templateData.selectedLicence = selectedLicence;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].licence = selectedLicence;
            }
        },
        massive_selected_albums_editing: (state, selectedAlbums) => {
            state.templateData.selectedAlbums = selectedAlbums;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].albums = selectedAlbums;
            }
        },
        setUploadStatus: (state, status) => {state.uploadStatus = status;}
    },
    actions: {
        fetchUserProfile: async (context) => {
            let response = await axios.get('/api/v1/user/profile/')
            context.commit('setUserProfile', response.data.user);
        },
        fetchLicences: async (context) => {
            let response = await axios.get('/api/v1/licences/list/')
            context.commit('setLicences', response.data.licences);
        },

        initialFetch: (context) => {
            Promise.all([
                context.dispatch('fetchUserProfile'),
                context.dispatch('fetchLicences'),
            ])
                .then( values => {
                    /* Mount application after fetching all required data. */
                    new Vue({ router, store }).$mount('#photos-upload')
                });
        },
        uploadPhotos: (context) => {
            context.commit('setUploadStatus', 'uploading');
            var authentication_token = context.state.user.authentication_token;
            for(var i=0; i < context.state.photos.length; i++) {
                var formData = new FormData()
                for(var key in context.state.photos[i]) {
                    formData.append(key, context.state.photos[i][key]);
                }
                axios.post('/api/v2/upload/photos/', formData, {
                    headers: {
                        'Authorization': `Token ${authentication_token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                })
                    .then(response => {
                        console.log(response);
                        context.commit('setUploadStatus', 'success');
                    })
                    .catch(error => {
                        console.log(error.response);
                        context.commit('setUploadStatus', 'failure');
                    })
            }
        }
    }
});


store.dispatch('initialFetch');


const uploadTypeForm = Vue.component('upload-type-form', {
    delimiters: ['${', '}'],
    template: '#upload-type-form-template',
    data() {
        return {
            uploadTypeOptions: [
                {value: 'import', text: gettext('Import from public collections')},
                {value: 'upload', text: gettext('Upload yourself')},
            ],
            uploadType: 'import',
        }
    },
    methods: {
        next(event) {
            if (this.uploadType === 'upload') {
                this.$router.push({name: 'user-mass-upload'});
            }
        }
    },
});


const photoUpload = Vue.component('photo-upload', {
    template: '#photo-upload-template',
});


Vue.component('upload-form', {
    template: '#upload-form-template',
    store: store,
    methods: {
        filesChange(files) {
            // TODO: Think about how to load folder of images. If it is possible.
            for(let i = 0; i < files.length; i++) {
                this.$store.commit('addPhotoFromFile', {file: files[i]});
            }
        },
    }
});


Vue.component('photos-editor', {
    delimiters: ['${', '}'],
    template: '#photos-editor-template',
    store: store,
    data: () => {
        return {
            availableAlbums: [],
            licences: [],
        };
    },
    computed: {
        name: {
            get () {return this.$store.state.templateData.name;},
            set (name) {this.$store.commit('massive_name_editing', name);}
        },
        description: {
            get () {return this.$store.state.templateData.description;},
            set (description) {this.$store.commit('massive_description_editing', description);}
        },
        longitude: {
            get () {return this.$store.state.templateData.longitude;},
            set (longitude) {this.$store.commit('massive_longitude_editing', longitude);}
        },
        latitude: {
            get () {return this.$store.state.templateData.latitude;},
            set (latitude) {this.$store.commit('massive_latitude_editing', latitude);}
        },
        azimuth: {
            get () {return this.$store.state.templateData.azimuth;},
            set (azimuth) {this.$store.commit('massive_azimuth_editing', azimuth);}
        },
        isUserAuthor: {
            get () {return this.$store.state.templateData.isUserAuthor;},
            set (isUserAuthor) {this.$store.commit('massive_is_author_editing', isUserAuthor);}
        },
        selectedLicence: {
            get () {return this.$store.state.templateData.selectedLicence;},
            set (selectedLicence) {this.$store.commit('massive_selected_licence_editing', selectedLicence);}
        },
        selectedAlbums: {
            get () {return this.$store.state.templateData.selectedAlbums;},
            set (selectedAlbums) {this.$store.commit('massive_selected_albums_editing', selectedAlbums);}
        },
        uploadButtonType: {
            get () {
                if (this.$store.state.uploadStatus === 'waiting')
                    return 'primary';
                if (this.$store.state.uploadStatus === 'success')
                    return 'success';
                if (this.$store.state.uploadStatus === 'failure')
                    return 'danger';
            },
        },
        uploadButtonIcon: {
            get () {
                if (this.$store.state.uploadStatus === 'uploading')
                    return 'el-icon-loading';
                else
                    return 'el-icon-upload2';
            },
        },
    },
    created: function() {
        var authentication_token = this.$store.state.user.authentication_token;
        axios.post(
            '/api/v1/albums/',
            {include_empty: true},
            {headers: {Authorization: `Token: ${authentication_token}`}}
        )
            .then(response => {this.availableAlbums = response.data.albums})
    },
    methods: {
        startUpload: function(event) {
            this.$store.dispatch('uploadPhotos');
        },
    },
});


Vue.component('photos-editor-photo-element', {
    delimiters: ['${', '}'],
    template: '#photos-editor-photo-element-template',
    props: ['photo', 'albums', 'licences']
});


const router = new VueRouter({
    routes: [
        {path: '/', redirect: {name: 'choose-upload-type'}},
        {path: '/upload-type', name: 'choose-upload-type', component: uploadTypeForm},
        {path: '/user-upload', name: 'user-mass-upload', component: photoUpload},
    ]
})
