function getfilters() {
  var classes = new Array();
  classes.push('.slidebox');
  var loc = $('#locationselect').val();
  var group = $('#groupselect').val();
  var showoffline = $('#showoffline').is(':checked');
  if (group != '') {
    classes.push('.slide-group-'+group);
  }
  classlist = classes.join('');
  return classlist;
}

function filtergrouplocation() {
  filterlist = getfilters();
  $('.slidebox').hide();
  $(filterlist).show();
}

function resetfilterform() {
  document.getElementById('slidefilterform').reset();
  filtergrouplocation();
}

function handledelete(slidebox, source) {
  $(source).dialog("close");
  confirmbox = $('<div>');
  confirmbox.html('Are you sure you wish to delete this slide?');
  confirmbox.dialog({modal:true,autoOpen:true,
                        resizable:false,draggable:false,
                        buttons:{"Yes, Delete!":function() {
                                   confirmbox.remove();
                                   dodelete(slidebox, source);
                                   },
                                 "Cancel":function() {
                                   $(source).dialog("open");
                                   $(this).dialog("close");
                                   confirmbox.remove();
                                  }}});
}

function dodelete(slidebox, source) {
  source = $(source);
  console.log('u');
  removalid = slidebox.attr('id');
  removalid = removalid.replace('slide-','');
  $.ajax({type:'POST', data:{remove:removalid},
          success:function(data) {
            source.dialog("close");
            slidebox.fadeOut('slow', function() {
              slidebox.children('.infopopup').dialog('destroy');
              slidebox.remove();
            });
          },
          error:function(xhr,textStatus,errorThrown) {
            if (xhr.status == 404) {
              alert('The slide you are trying to delete has vanished!');
            }
            else if (xhr.status == 500) {
              alert('There was an internal server error while deleting!');
            }
            else if (xhr.status == 400) {
              alert('The deletion request was malformed. Is the page stale?');
            }
            else if (xhr.status == 403) {
              alert('Sorry, you do not have the required permissions.');
            }
          }
  });
}

function setupdialogs() {
  $('.slidebox').each(function() {
      slidebox = $(this);
      var id = slidebox.children('.infopopup').attr('id');
      $('#'+id).dialog({modal:true,autoOpen:false,
                        resizable:false,draggable:false,
                        buttons:{"Save":function() {alert('Not implemented');},
                                 "Delete":function() {
                                   handledelete(slidebox, this);
                                   },
                                 "Cancel":function() {
                                   $(this).dialog("close");
                                  }}});
      $(this).click(function() {
        $('#'+id).dialog('open');});
      });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filtergrouplocation);
  $('#groupselect').change(filtergrouplocation);
  $('#resetfilter').click(resetfilterform);
  $('.slide-details-save').live("click", function(){
	  $.post("", this.id, function(data) {
		  $('.result').html(data);
	      });});
});
