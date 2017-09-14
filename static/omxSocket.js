$(document).ready(function() {
    namespace = '/omxSock';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var paused = 'False'

    socket.on('connect', function() {
                console.log('I\'m connected!');
            });

    socket.on('position', function(msg) {
        // console.log(msg.position);
        $('#position').html(msg.position);
        var bar_width = ($( document ).width() / 100) * msg.percentage
        // console.log(bar_width);
        $('#progress_bar').width(bar_width);
        if (paused != msg.paused) {
            console.log('paused = ' + msg.paused)
            paused = msg.paused
            if (paused == 'False') {
            $('#play_pause').html('&#9654;');
            } else {
            $('#play_pause').html('&#9611;&#9611;');
            }
        }
    });

    $('button').click(function() {
        console.log($(this).val())
        socket.emit('ctl_event', $(this).val());
        return false;
    });

 });