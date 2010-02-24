function getfilters() {
  var classes = new Array();
  classes.push('.slidebox');
  var loc = $('#locationselect').val();
  var group = $('#groupselect').val();
  var showoffline = $('#showoffline').is(':checked');
  if (loc != '') {
    classes.push('.client-location-'+loc);
  }
  if (group != '') {
    classes.push('.client-group-'+group);
  }
  if (!showoffline) {
    classes.push('.client-online');
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
  //Ugh, this should be done with jquery...
  document.getElementById('clientfilterform').reset();
  filtergrouplocation();
}

function powercontroldialog(id) {
  t = $('<div>').attr('class', 'powercontroldialogcontent');
  t.load(clientpowerurl, function(){
    t.find('#powerctlclient').val(id);
  });
  t.dialog({modal:true,autoOpen:true,title:"Client Power Control",
            width:350,resizable:false,draggable:true,
            close:function(event, ui) {
            t.remove();
            }
  });
}

function setupdialogs() {
  $('.slidebox').each(function() {
      var id = $(this).children('.infopopup').attr('id');
      $('#'+id).dialog({modal:true,autoOpen:false,
                        resizable:false,draggable:false,
                        buttons:{
                        "Power": function() {
                          $(this).dialog("close");
                          powercontroldialog($('#'+id+' > .clientid').val());
                        },
                        "Ok": function() {
                          $(this).dialog("close");
                        },
                        "Cancel": function() {
                          $(this).dialog("close");
                        },
                        }});
      $(this).click(function() {
        $('#'+id).dialog('open');});
      });
}

function updateclients() {
  $.getJSON(jsonupdateurl,
    function(data){
      $.each(data, function(i,client_activity) {
        div = $('#client-'+client_activity['client']['hash'])
        image = div.find('.slidepreview')[0];
        image.src = client_activity['client']['screenshot'];
        image.title = client_activity['client']['caption'];
        image.alt = client_activity['client']['caption'];
        div.removeClass('client-online client-offline')
        if (client_activity['active']) {
          div.addClass('client-online')
        } else {
          div.addClass('client-offline')
        }
      });
      filtergrouplocation();
      setTimeout(updateclients, 1000);
    });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filtergrouplocation);
  $('#locationselect').change(filtergrouplocation);
  $('#groupselect').change(filtergrouplocation);
  $('#resetfilter').click(resetfilterform);
  setTimeout(updateclients, 1000);
});
