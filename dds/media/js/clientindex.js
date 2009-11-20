function getfilters() {
  var classes = new Array();
  classes.push('.clientbox');
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
  $('.clientbox').hide();
  $(filterlist).show();
}

function resetfilterform() {
  document.getElementById('clientfilterform').reset();
  filtergrouplocation();
}

function setupdialogs() {
  $('.clientbox').each(function() {
      var id = $(this).children('.infopopup').attr('id');
      $('#'+id).dialog({modal:true,autoOpen:false});
      $(this).click(function() {
        $('#'+id).dialog('open');});
      });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filtergrouplocation);
  $('#locationselect').change(filtergrouplocation);
  $('#groupselect').change(filtergrouplocation);
  $('#resetfilter').click(resetfilterform);
});
