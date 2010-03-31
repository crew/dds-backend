function build_playlist(data) {
  window.data = data; // debug
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
      $(datum.groups).each(function(dummy, group) {
	span = $('<span>').addClass('removable-option')
	                  .attr('id', group.id)
	                  .text(group.name);
	span.append($('<span>').addClass('ro-button')
                               .text('x')
                               .click(function () {$(this).parent().remove()}));
	plitem.append(span);
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
  })	
}

$(function() {

  $.getJSON(playlistdatauri, build_playlist);

});

$(document).ready(function(){
  $("#playlist").sortable();
  $(".plig_toolbox_item").draggable();
  $(".plig").droppable( { accept: ".plig_toolbox_item",
	                  hoverClass: "hover",
	  		  drop: function(id) {
			    alert("Group " + id + " has been dropped.");
			  }} );
  
  $(".plis_toolbox_item").draggable();
  $(".plis").droppable( { accept: ".plis_toolbox_item",
	 		  hoverClass: "hover",
	                  drop: function(id) {
			    alert("Slide " + id.src + " has been dropped");
			  }})
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
	   function(data) { /* TODO: some error checking here! */ return;});
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
	      groups:li.find('span.removable-option').map(span_to_json).get()};
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
  $('#submit').click(submit);
  
})
