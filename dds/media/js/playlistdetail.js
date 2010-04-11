function create_group_span(id, name) {
  span = $('<span>').addClass('removable-option').addClass('plig-group')
                    .attr('id', id)
                    .text(name);
  span.append($('<span>').addClass('ro-button')
                        .text('x')
                        .click(function () {$(this).parent().remove()}));
  return span;
}

function build_playlist(data) {
  $("#playlist").html('');
  $(data).each(function (dummy, datum) {
    var plitem = $('<li>');


    if (datum.type === 'PlaylistItemSlide') {
      // PlaylistItemSlide
      plitem.addClass("plis");
      plitem.attr('id', datum.slide.id);
      plitem.text(datum.slide.title);
      plitem.append($('<img>').attr('src', datum.slide.thumbnail));
    } else {
      // PlaylistItemGroup
      plitem.addClass("plig");
      var plitemgroups = $('<span>').addClass('plig-group-container');
      plitem.append(plitemgroups);
      $(datum.groups).each(function(dummy, group) {
        plitemgroups.append(create_group_span(group.id, group.name));
      })
      cb_id = datum.id + '-weighted';
      plitem.append($('<label>')
  	    .attr('for', cb_id)
  	    .text('Weighted?'));
      plitem.append($('<input>')
  	    .addClass('plig-weighted')
  	    .attr('id', cb_id)
  	    .attr('type', 'checkbox')
  	    .attr('checked', datum.weighted));
    }
    $("#playlist").append(plitem);
  });
  setup_droppable();
}

function setup_droppable() {
  $(".plig").droppable( { accept: ".plig_toolbox_item",
                    hoverClass: "hover",
                    activeClass: '.ui-state-highlight',
    		  drop: function(event, ui) {
    		  var group = $(event.srcElement);
    		  var plig = $(event.target);
    		  var groupcontainer = plig.find('.plig-group-container').first();
    		  var id = group.attr('id').replace('group','');
    		  var name = group.html().replace(/^\s+|\s+$/g,"");
    		  var ok = 1;
    		  groupcontainer.children().each(function(i, o) {
    		    if (ok && (id == $(o).attr('id'))) {
    		      alert('Couln\'t drop! Already exists!');
    		      ok = 0;
    		    }});
    		  if (ok) {
            var groupspan = create_group_span(id, name);
            groupcontainer.append(groupspan);
          }
  		  }} );

  $(".plis").droppable( { accept: ".plis_toolbox_item",
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
  $(".plig_toolbox_item").draggable({helper:'clone'});
  $(".plis_toolbox_item").draggable({helper:'clone'});
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
    if (li.hasClass("plis")) {
      // PlaylistItemSlide
      return {type:"plis",
        slide:{id:parseInt(li.attr('id'))}};
    } else {
      // PlaylistItemGroup
      return {type:"plig",
        weighted:li.find('.plig-weighted').first().attr('checked'),
        groups:li.find('.plig-group').map(span_to_json).get()};
    }
  }

  /**
   * span_to_json : Number [HTML SPAN] -> Float
   * reads a span element representing a group in a PlaylistItemGroup and
   * returns representative json
   **/
  function span_to_json(dummy, span) {
    return parseInt($(span).attr('id'));
  }

  // (provide ...)
  $('#playlist-save').click(submit);
  $('#playlist-reset').click(load_playlist_from_server);

  load_playlist_from_server();
})
