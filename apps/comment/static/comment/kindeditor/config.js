KindEditor.ready(function (K) {
    window.editor = K.create("#comment-widget", {
        "afterCreate": function () {
            this.sync();
        },
        "afterChange": function () {
            this.sync();
        },
        "afterBlur": function () {
            this.sync();
        },
        "items": [
            'emoticons', 'paste', 'plainpaste', 'wordpaste', '|', 'justifyleft', 'justifycenter', 'justifyright',
            'justifyfull', 'insertorderedlist', 'insertunorderedlist', 'formatblock', 'fontname', 'fontsize', '|', 'forecolor', 'bold',
            'italic', 'underline', 'lineheight', '|', 'fullscreen'
        ],
        "uploadJson":"/kindeditor/upload/",
    });
});