if (window.jQuery) {
  (function($){
    'use strict';

    $(document).ready(function(){
        var $found_links = $("a[href='" + window.location.pathname + "']");
        if ($found_links.length > 0) {
            $found_links.parent().addClass('active');
        }
    });

    function single_submit_form_handler(e) {
      if (this.already_submitted) {
        return false;
      };
      this.already_submitted = 'true';

      // don't care about submits as input, not as buttons.
      // We use them quite rare and it's just UI stuff.
      $(this).find("button[type='submit']").each(function (index, item) {
        var $it = $(item);
        $it.html($it.text() + '&nbsp;&nbsp;(loading...)');
      });
    }

    $("form:not(.no-ss-form)").submit(single_submit_form_handler);
  }(jQuery));
}