function getfilters() {
  var classes = new Array();
  classes.push('.slidebox');
  var loc = $('#locationselect').val();
  var showoffline = $('#showoffline').is(':checked');
  if (loc != '') {
    classes.push('.client-location-'+loc);
  }
  if (!showoffline) {
    classes.push('.client-online');
  }
  classlist = classes.join('');
  return classlist;
}

function filterlocation() {
  filterlist = getfilters();
  $('.slidebox').hide();
  $(filterlist).show();
}

function resetfilterform() {
  //Ugh, this should be done with jquery...
  document.getElementById('clientfilterform').reset();
  filterlocation();
}

function dosave(slidebox,source) {
  source = $(source);
  //var clientID = slidebox.children('.clientid').val();
  form = source.children('.editform');
  form = form.children();
  $.post('/clients/edit/',form.serialize());
  return true;
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
      var slidebox = $(this);
      var ch = slidebox.children('.infopopup')
      var hashid = slidebox.attr('id');
      var realid = $('#'+hashid).children('div').attr('title');
      ch.dialog({modal:true,autoOpen:false,
                        resizable:false,draggable:false,
                        buttons:{"Ok": function() {
                                    dosave(slidebox,this);
                                    $(this).dialog("close")
                                    location.reload();
                                  },
                                  "Cancel":function() {
                                    $(this).dialog("close");
                                  },
                                  "Power":function() {
                                    powercontroldialog(realid);
                                    //$(this).dialog("close");
                                  },
                                },
                        close: function(event,ui) { /*location.reload();*/ }});
      $(this).click(function() {
        ch.dialog('open');});
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
      filterlocation();
      setTimeout(updateclients, 1000);
    });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filterlocation);
  $('#locationselect').change(filterlocation);
  $('#resetfilter').click(resetfilterform);
  setTimeout(updateclients, 1000);
});
