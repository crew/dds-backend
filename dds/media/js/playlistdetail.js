// build_playlist : [JSONArray [JSONObject PlaylistItem]]
//                  -> Void
// builds a playlist from the data and updates the page with it
function build_playlist(data) {
  $("#playlist").html(''); // clear the contents
  $(data).each(function (dummy, datum) {
    $("#playlist").append(build_playlist_item(datum));
  });
  setup_droppable();
}

// build_playlist_item : [JSONObject PlaylistItem]
//                       -> [HTML li]
// creates an HTML list item representing a PlaylistItem
function build_playlist_item(pli) {
  return build_pli(pli);
}

// build_pli : [JSONObject PlaylistItem] -> [HTML li]
// creates an HTML list item representing a PlaylistItem
function build_pli(pli){
  var plitem = $('<li>');

  plitem.addClass("pli");
  plitem.attr('id', pli.slide.id);
  plitem.text(pli.slide.title);
  plitem.append($('<img>').attr('src', pli.slide.thumbnail));

  return plitem;
}

function setup_droppable() {
  $(".pli").droppable( { accept: ".pli_toolbox_item",
                    hoverClass: "hover",
                    activeClass: '.ui-state-highlight',
                    drop: function(id) {
  		    alert("Slide " + id.src + " has been dropped");
  		  }});
}

function load_playlist_from_server() {
  $.getJSON(playlistdatauri, build_playlist);
}

$(document).ready(function(){
  $("#playlist").sortable();
  $(".pli_toolbox_item").draggable({helper:'clone'});
});



$(function () {
  /**
   * This scope covers submitting values to the backend
   */

  /**
   * submit : -> False
   * handles submitting back the modified playlist
   **/
  function submit() {
    var json = $("#playlist").find('li').map(li_to_json).get();
    console.log(json);
    $.post(playlistdatauri,
     JSON.stringify(json),
     function(data) {
       load_playlist_from_server();
       alert('Changes complete!');
     });
    return false;
  }

  /**
   * li_to_json : Number [HTML LI] -> JSON
   * reads an li element representing a PlaylistItem and returns representative
   * json
   **/
  function li_to_json(dummy, li) {
    var li = $(li);
    // PlaylistItem
    return {type:"pli",
      slide:{id:parseInt(li.attr('id'))}};
  }

  // (provide ...)
  $('#playlist-save').click(submit);
  $('#playlist-reset').click(load_playlist_from_server);

  load_playlist_from_server();
})
