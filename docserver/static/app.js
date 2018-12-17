// Vue Componenets for Main App
Vue.component('category-item', {
    props: ['category'],
    template: `
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">{{ category.category }}</h3>
            </div>
            <ul class="list-group">
                <document-detail v-for="art in category.documents" v-bind:document="art"></document-detail>
            </ul>
        </div>`
})


Vue.component('document-detail', {
    props: ['document'],
    template: `
        <li class="list-group-item">
            <a v-bind:href="document.doc_path">{{ document.doc_name }}</a>
        </li>`
})


// Vue for Main App
var app = new Vue({
    el: '#app',
    data: {
        documentList: [],
        filterText: "",
        topDocumentPath: ""
    },

    methods: {

        getDocuments: function() {
            this.$http.get('/available').then(function(response){
                this.documentList = response.data;
            }, function(error){
                console.log(error.statusText);
            });
        },

        searchDocumentNames: function(dataList) {
            // Have to redefine this here, scoping this.filterText inside the map is weird.
            var funFilterText = this.filterText;
            // Want to filter the documentation names within each category, removing empty categories from view.
            var searchedDataList = dataList.map(val => Object.keys(val).reduce(function(previous, current) {
                // current here is the value of the key in a dict like {'documents':[docs], 'category': 'category_name'}
                if (current === 'documents') {
                    // If it's 'documents', we filter the documentation by doc_names matching funFilterText
                    previous[current] = val[current].filter(subVal => subVal.doc_name.toLowerCase().match(funFilterText.toLowerCase()) !== null);
                    return previous
                } else {
                    // If it's 'name', or anything else, we pass it along.
                    previous[current] = val[current];
                    return previous
                }
                // Then we filter out any categories with documents length of 0.
            }, {})).filter(val => val.documents.length !== 0);

            // Set the top search path for when a user hits enter
            if (searchedDataList.length > 0) {
                this.topDocumentPath = searchedDataList[0].documents[0].doc_path;
            } else {
                this.topDocumentPath = "";
            }

            return searchedDataList
        },

        navigateTopDoc: function() {
            // When a user presses enter, want to navigate them to the doc path at the top of the list if there is one.
            if (this.topDocumentPath !== "") {
                window.location.href = this.topDocumentPath;
            }
        }

    },

    mounted: function() {
        this.getDocuments();
    }

})
