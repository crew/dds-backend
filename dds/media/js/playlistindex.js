$(function() {
  /* These functions relate to the playlist selector dropdown. */
  function build_playlist_dropdown(data) {
    $(data).each(function (dummy, datum) {
      var op = $('<option>');
      op.attr('value', datum.uri);
      op.html(datum.name);
      $('#playlist-selector-dropdown').append(op);
    });
  }

  function gotoplaylist(selector) {
    var newuri = $(this).val();
    if (document.location.href.indexOf(newuri) == -1) {
      document.location.href = $(this).val();
    }
    else {
      $(this).val('#');
    }
  }

  $('#playlist-selector-dropdown').change(gotoplaylist);
  $.getJSON(playlistlisturi, build_playlist_dropdown);
});
