$(document).ready(function() {
    namespace = '/omxSock';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var paused = false
    var duration = ''
    var filename = ''
    var new_file = ''

    var convertTime = function (frames, fps) {
    fps = (typeof fps !== 'undefined' ?  fps : 30 );
    var pad = function(input) {return (input < 10) ? "0" + input : input;},
        seconds = (typeof frames !== 'undefined' ?  frames / fps : 0 );
    return [
        pad(Math.floor(seconds / 3600)),
        pad(Math.floor(seconds % 3600 / 60)),
        pad(Math.floor(seconds % 60)),
        pad(Math.floor(frames % fps))
        ].join(':');
    }


    socket.on('connect', function() {
                console.log('I\'m connected!');
            });

    socket.on('position', function(msg) {
        // console.log(msg.position);
        $('#position').html(msg.position);
        var bar_width = ($( document ).width() / 100) * msg.percentage
        // console.log(bar_width);
        $('#progress_bar').width(bar_width);
        if (msg.duration != duration) {
            duration = msg.duration
            $('#duration').html(duration);
        }
        if (msg.filename != filename) {
            filename = msg.filename
            $('#filename').html(filename);
        }
        if (paused != msg.paused) {
            console.log('paused = ' + msg.paused)
            paused = msg.paused
            if (paused == false) {
            $('#play_pause').html('<i class="material-icons">&#xE036;</i>');
            } else {
            $('#play_pause').html('<i class="material-icons">&#xE039;</i>');
            }
        }
    });

    $('.ctl-button').click(function() {
        console.log($(this).val())
        socket.emit('ctl_event', $(this).val());
        return false;
    });

    $('.new-file').click(function() {
        console.log($(this).val())
        socket.emit('file_event', $(this).val());
        return false;
    });

    $('#progress-wrapper'). mousemove(function(e) {
        $('#marker').css('left', (e.pageX - 6) + 'px');
        $('#marker-pos').css('left', (e.pageX - 6) + 'px');
        $('#marker-pos').text(convertTime(e.pageX));
    });

    $('#progress-wrapper'). mouseleave(function() {
        $('#marker').css('left', '-3px');
        $('#marker-pos').css('left', '-3px');
        $('#marker-pos').text('');
    });

 });