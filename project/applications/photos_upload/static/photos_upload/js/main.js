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
    data() {return {
        fileList: [],
    }},
    methods: {
        showFiles(files) {
            this.fileList = files;
        },
    }
});


Vue.component('upload-form', {
    template: '#upload-form-template',
    data() {return {}},
    methods: {
        filesChange(files) {
            // TODO: Think about how to load folder of images. If it is possible.
            this.$emit('got-files', files);
        },
    }
});


Vue.component('photos-editor', {
    delimiters: ['${', '}'],
    template: '#photos-editor-template',
    props: ['fileList'],
    watch: {
        fileList: function (newFileList, oldFileList) {
            for (var i = 0; i < newFileList.length; i++) {
                var reader = new FileReader();
                var file = newFileList[i];
                var photo = {
                    originalFileName: file.name,
                    name: file.name,
                    image: null,
                    description: null,
                    longitude: null,
                    latitude: null,
                    azimuth: null,
                    isUserAuthor: false,
                };

                reader.onload = function(photo) {
                    return function(event){
                        photo.image = event.target.result;
                    }
                }(photo);

                reader.readAsDataURL(file);
                this.photos.push(photo);
            }
        },
    },
    data() {return {
        photos: [],
    }},
    methods: {}
});


Vue.component('photos-editor-photo-element', {
    delimiters: ['${', '}'],
    template: '#photos-editor-photo-element-template',
    props: ['photo'],
    data() {return {}},
    methods: {}
});


const router = new VueRouter({
    routes: [
        {path: '/', redirect: {name: 'choose-upload-type'}},
        {path: '/upload-type', name: 'choose-upload-type', component: uploadTypeForm},
        {path: '/user-upload', name: 'user-mass-upload', component: photoUpload},
    ]
})


new Vue({ router }).$mount('#photos-upload');
