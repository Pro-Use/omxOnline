$(document).ready(function() {
    namespace = '/progress';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('position', function(msg) {
        $('#progress_bar').html(msg.position);
    });
});