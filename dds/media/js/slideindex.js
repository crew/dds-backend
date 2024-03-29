function getfilters() {
  var classes = new Array();
  classes.push('.slidebox');
  var loc = $('#locationselect').val();
  var showoffline = $('#showoffline').is(':checked');
  classlist = classes.join('');
  return classlist;
}

function filterlocation() {
  filterlist = getfilters();
  $('.slidebox').hide();
  $(filterlist).show();
}

function resetfilterform() {
  document.getElementById('slidefilterform').reset();
  filterlocation();
}

function handlesave(slidebox, source) {
  dosave(slidebox, source);
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

function dosave(slidebox,source) {
  source = $(source);
  $.post('/slides/edit/',source.children('form').serialize());
  return true;
}
function dodelete(slidebox, source) {
  source = $(source);
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
      var slidebox = $(this);
      var ch = slidebox.children('.infopopup')
      removalid = slidebox.attr('id');
      ch.dialog({modal:true,autoOpen:false,
                        resizable:false,draggable:false,
                        buttons:{"Save":function() {
                                   handlesave(slidebox, this);
                                   $('.infopopup').html('');
                                   $(this).dialog("close");
                                   },
                                 "Delete":function() {
                                   handledelete(slidebox, this);
                                   $(this).dialog("close");
                                   },
                                 "Cancel":function() {
                                   $(this).dialog("close");
                                   $('.infopopup').html('');
                                  }},
                        close: function(event,ui) { $('.infopopup').html(''); }});
      $(this).click(function() {
        ch.dialog('open');});
      });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filterlocation);
  $('#resetfilter').click(resetfilterform);
  $('.slide-details-save').live("click", function(){
	  $.post("", this.id, function(data) {
		  $('.result').html(data);
	      });});
});
