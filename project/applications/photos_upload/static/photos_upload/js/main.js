const store = new Vuex.Store({
    state: {
        photos: [],
        user: {},
        licences: [],
        massiveEditFormData: {
            name: '',
            description: '',
            // Geographical centre of Estonia
            latitude: 58.657777777777774,  // 58°39'28"N
            longitude: 25.573888888888888,  // 25°34'26"E
            azimuth: 0,
            isUserAuthor: false,
            selectedLicence: null,
            selectedAlbums: []
        }
    },
    mutations: {
        addPhotoFromFile: (state, {file}) => {
            let photo = {
                originalFileName: file.name,
                name: file.name,
                image: null,
                description: null,
                longitude: null,
                latitude: null,
                azimuth: null,
                isUserAuthor: false,
                licence: null,
                albums: [],
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
            state.massiveEditFormData.name = name;
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
            state.massiveEditFormData.description = description;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].description = description;
            }
        },

        massive_longitude_editing: (state, longitude) => {
            state.massiveEditFormData.longitude = longitude;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].longitude = longitude;
            }
        },

        massive_latitude_editing: (state, latitude) => {
            state.massiveEditFormData.latitude = latitude;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].latitude = latitude;
            }
        },
        massive_azimuth_editing: (state, azimuth) => {
            state.massiveEditFormData.azimuth = azimuth;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].azimuth = azimuth;
            }
        },
        massive_is_author_editing: (state, isUserAuthor) => {
            state.massiveEditFormData.isUserAuthor = isUserAuthor;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].isUserAuthor = isUserAuthor;
            }
        },
        massive_selected_licence_editing: (state, selectedLicence) => {
            state.massiveEditFormData.selectedLicence = selectedLicence;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].licence = selectedLicence;
            }
        },
        massive_selected_albums_editing: (state, selectedAlbums) => {
            state.massiveEditFormData.selectedAlbums = selectedAlbums;
            for(var i = 0; i < state.photos.length; i++) {
                state.photos[i].albums = selectedAlbums;
            }
        },
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
            get () {return this.$store.state.massiveEditFormData.name;},
            set (name) {this.$store.commit('massive_name_editing', name);}
        },
        description: {
            get () {return this.$store.state.massiveEditFormData.description;},
            set (description) {this.$store.commit('massive_description_editing', description);}
        },
        longitude: {
            get () {return this.$store.state.massiveEditFormData.longitude;},
            set (longitude) {this.$store.commit('massive_longitude_editing', longitude);}
        },
        latitude: {
            get () {return this.$store.state.massiveEditFormData.latitude;},
            set (latitude) {this.$store.commit('massive_latitude_editing', latitude);}
        },
        azimuth: {
            get () {return this.$store.state.massiveEditFormData.azimuth;},
            set (azimuth) {this.$store.commit('massive_azimuth_editing', azimuth);}
        },
        isUserAuthor: {
            get () {return this.$store.state.massiveEditFormData.isUserAuthor;},
            set (isUserAuthor) {this.$store.commit('massive_is_author_editing', isUserAuthor);}
        },
        selectedLicence: {
            get () {return this.$store.state.massiveEditFormData.selectedLicence;},
            set (selectedLicence) {this.$store.commit('massive_selected_licence_editing', selectedLicence);}
        },
        selectedAlbums: {
            get () {return this.$store.state.massiveEditFormData.selectedAlbums;},
            set (selectedAlbums) {this.$store.commit('massive_selected_albums_editing', selectedAlbums);}
        },
    },
    created: function() {
        let data = {
            include_empty: true,
            _u: this.$store.state.user.id,
            _s: this.$store.state.user.session_id
        };
        axios.post('/api/v1/albums/', data)
            .then(response => {this.availableAlbums = response.data.albums})
    },
    methods: {},
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
