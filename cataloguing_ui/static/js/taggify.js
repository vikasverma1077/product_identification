(function ($) {
  $.fn.taggify = function () {
    jq_name_obj = this;
    var color_dict = {}
    
    String.prototype.format = String.prototype.f = function () {
      var s = this, i = arguments.length;

      while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
      }
      return s;
    };
    
    function showTag(x, y) {
      $('.tag_list').css("left",x-200);
      $('.tag_list').css("top",y-20);
      $('.tag_list').focus();
    }

    function bindMenuSnapping() {
      $(document).click(function() {
        $('.tag_list').css("left","-9999px");
        $('.address_element').removeClass( "ui-selected" );
      });

      $(".address").click(function(e) {
        e.stopPropagation();
        return false;
      });
    }  

    function resetTags() {
      $('input:checkbox').removeAttr('checked');
      jq_name_obj.children().removeClass('ui-selected tagged').removeAttr('style').removeAttr('tag')
    }

    function refreshTags() {
      $.each($('.address_element'), function(index, val) {
        var addr_elem = $(this)
        var tooltip_obj = $(this).next()
        if (addr_elem.attr('tag') != 'null') {
          addr_elem.addClass('tagged')
          addr_elem.css({'background-color':getRandomColor(addr_elem.attr('tag'))})
          tooltip_obj.text(addr_elem.attr('tag'))
          tooltip_obj.css({
            'position':'absolute',
            'display': 'block',
            'left' : addr_elem.offset().left + addr_elem.outerWidth( false )/2 - tooltip_obj.outerWidth( false )/2 - 215,
            'top' : addr_elem.offset().top - 10
          });
        }
        else
          addr_elem.removeAttr('tag')
      });
    }

    function setUpAddress() {
      var span_text = "<span class = 'address_element' tabindex='{0}' tag='{1}'><abc>{2}</abc></span>";
      total_string = "";
      if (tagged_data == "")
          for (i = 0; i < prod_seg.length; i++) {
            total_string += span_text.f(i+1, null, prod_seg[i])
          }
      else
          for (i = 0; i < tagged_data.length; i++) {
            total_string += span_text.f(i+1, tagged_data[i][1], tagged_data[i][0])
          }

      var tags = $('#tag_template').html();
      jq_name_obj.html(total_string);
      $(tags).insertAfter(jq_name_obj);
      $("<div class='tooltip'>Tooltip Box</div>").insertAfter('.address_element')
    }

    function getRandomColor (tag_type) {
//      var hex = Math.floor(0.3*Math.random() * 0xFFFFFF);
//      var color = "#" + ("000000" + hex.toString(16)).substr(-6);
        if (color_dict[tag_type])
          return color_dict[tag_type]
        else {
          var letters = '0123456789ABCDEF'.split('');
          var color = '#';
          for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
          }
          color_dict[tag_type] = color
          return color;
        }
    }

    function tagItem(obj) {
      var tag_type = $(obj).attr('tagtype');
      $('.ui-selected').attr('tag',tag_type);
      $( "span[tag]").addClass('tagged');
      $.each($('.ui-selected'), function() {
        var addr_elem = $(this);
        var tooltip_obj = $(this).next();
        tooltip_obj.text(addr_elem.attr('tag'));
        tooltip_obj.css({
          'position':'absolute',
          'display': 'block',
          'left' : addr_elem.offset().left + addr_elem.outerWidth( false )/2 - tooltip_obj.outerWidth( false )/2 - 215,
          'top' : addr_elem.offset().top - 10
        });
      });
      // ---------------Coloring logic-------------------
      var all_elements = $( "span[tag]");
      $.each(all_elements, function(elem_obj) {
        if ($(this).attr('tag') == tag_type)
          {
            $(this).css({
              'background-color': getRandomColor(tag_type)
            });
          }
      })
    }

    function sendTagsAJAX(tags, dang, xray, dirty, skipped) {
      var url;
      if (q != 'tag') {
        url = '/cat-ui/set-verified-tags';
        data_obj['admin_tags'] = tags;
      }
      else {
        url = '/cat-ui/set-tags';
        data_obj['tags'] = tags;
      }

      var date = new Date();
      data_obj.epoch = date.getTime();
      data_obj['id'] = (is_undo) ? pid : id;
      data_obj['is_dang'] = dang;
      data_obj['is_xray'] = xray;
      data_obj['is_dirty'] = dirty;
      data_obj['is_skipped'] = skipped;
      data_obj['undo'] = is_undo;
      return $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST', //make query POST
        contentType: 'application/json',
        data: JSON.stringify(data_obj)
      });
    }

    function sendTags(tags, is_dang, is_xray, is_dirty, is_skipped) {

      sendTagsAJAX(tags, is_dang, is_xray, is_dirty, is_skipped).done(function(data) {
        console.log('next product-name data:  ', data);
        if(data.error) {
            $.notify(data.error, { position:"bottom-right" });
            if (data.tag_count)
              $('#tag-count').html(data.tag_count);
            if (data.verify_count)
              $('#verify-count').html(data.verify_count);
            $("#tag-products").css("display", "none");
        }
        else {
            resetTags();
            if (data['tags'])
              tagged_data = data['tags'];
            else
              tagged_data = "";
            update_html(data);
            $('.address').taggify();
        }
      })
    }

    function setUp() {
      setUpAddress();
      if (q != 'tag' || is_undo) {
        refreshTags();
        is_undo = false;
      }
      bindMenuSnapping();
      $( "#selectable" ).selectable({ autoRefresh: true,filter:'span',selected: function( event, ui ) {
          showTag(event.pageX,event.pageY)
        }
      });

      $('.tag_list a').on("click", function(e) {
        e.preventDefault();
        tagItem(this)
      });

      $('#clear-button').bind("click", function() {
        resetTags()
      });

      $('#submit-button').off().on('click', function() {
        if ($("span[tag][tag!=null]").length == $("span .address_element").length || $('input[type=checkbox]').is(':checked')) {
              var is_dang = $('#dangerous-goods').is(':checked');
              var is_xray = $('#x-ray').is(':checked');
              var is_dirty = $('#dirty-name').is(':checked');
              var is_skipped = false
              var tags = [];
              $.each($( "span .address_element"),function() {
                  if($(this).attr('tag') === undefined) {
                      tags = '';
                      return false;
                  }
                  tags.push([$(this).text(),$(this).attr('tag')])
              });
              pid = id;
              $('#submit-button').notify('Tags saved, fetching new product name...', "success");
              sendTags(tags, is_dang, is_xray, is_dirty, is_skipped);
        } else {
            $.notify('Please tag everything or Skip this name.', { position:"bottom-right" });
        }
      });

      $('#skip-button').off().on('click', function() {
          var is_skipped = true
          pid = id;
          $('#skip-button').notify('Skipping product name', "info");
          sendTags(null, null, null, null, is_skipped);
      });

      $('#undo-button').off().on('click', function() {
          if (pid) {
            is_undo = true;
            $('#undo-button').notify('Getting previous product...', "info");
            sendTags(null, null, null, null, null);
            pid = null
          }
          else
            $('#undo-button').notify('Pehle kuch tag toh karle!', "error");
      });
      
    }
    setUp()
  };
  return this
}( jQuery ));