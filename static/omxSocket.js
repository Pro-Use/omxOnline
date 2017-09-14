
    namespace = '/omxSock';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
                console.log('I\'m connected!');
            });

    socket.on('position', function(msg) {
        // console.log(msg.position);
        $('#position').html(msg.position);
        var bar_width = ($( document ).width() / 100) * msg.percentage
        // console.log(bar_width);
        $('#progress_bar').width(bar_width);

    });

    $('#play').click(function() {
        var ctl_msg = {ctl: play}
        socket.emit('ctl_event', ctl_msg);
        console.log(ctl_msg)
        return false;
    });