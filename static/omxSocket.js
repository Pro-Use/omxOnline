$(document).ready(function() {
    namespace = '/omxSock';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var paused = false

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
            if (paused == false) {
            $('#play_pause').html('<i class="material-icons">&#xE039;</i>');
            } else {
            $('#play_pause').html('<i class="material-icons">&#xE036;</i>');
            }
        }
    });

    $('button').click(function() {
        console.log($(this).val())
        socket.emit('ctl_event', $(this).val());
        return false;
    });

 });