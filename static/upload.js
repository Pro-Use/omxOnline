            $(function () {
                $('#fileupload').fileupload({
                    dataType: 'json',
                    replaceFileInput:false,
                    add: function (e, data) {
                        console.log(data.files[0].size)
                        console.log({{available}})

                        data.context = $('<button/>').text('Upload')
                            .appendTo(document.body)
                            .click(function () {
                                data.context = $('<p/>').text('Uploading...').replaceAll($(this));
                                data.submit();
                            });
                    },
                    progressall: function (e, data) {
                        var progress = parseInt(data.loaded / data.total * 100, 10);
                        $('#progress .bar').css(
                            'width',
                            progress + '%'
                        );
                    },
                    done: function (e, data) {
                        data.context.text('Upload finished.');
                        $('#progress .bar').css(
                            'width',
                            '0%'
                        );
                        location.reload();
                    },
                });
            });
