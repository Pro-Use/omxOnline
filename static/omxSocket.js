
    namespace = '/position';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
                console.log('I\'m connected!');
            });

    socket.on('position', function(msg) {
        console.log(msg.position);
        $('#progress_bar').html(msg.position);
    });
