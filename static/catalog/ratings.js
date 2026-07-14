// The star rating widget. Clicking a star picks a value and the submit
// button posts it to the rate endpoint with the csrf token. The page then
// shows the new average without a reload. All listeners are attached here
// rather than inline in the HTML

// jQuery runs this function once the page has finished loading.
$(function () {
    var section = $('#rating-section');
    if (!section.length) {
        // This page has no rating section so there is nothing to wire up
        return;
    }

    // The template stores the endpoint url in a data attribute so this
    // script needs no hardcoded paths
    var rateUrl = section.data('rate-url');
    var token = section.find('input[name=csrfmiddlewaretoken]').val();
    var stars = section.find('.star');
    var selected = 0;

    // Fill the star icons up to the value the user picked
    function paint(value) {
        stars.each(function () {
            var icon = $(this).find('i');
            var on = $(this).data('value') <= value;
            icon.toggleClass('bi-star-fill', on).toggleClass('bi-star', !on);
        });
    }

    // Remember the clicked star and repaint the row
    stars.on('click', function () {
        selected = $(this).data('value');
        paint(selected);
    });

    // Send the rating to the server and show the fresh average it returns
    section.find('#rating-submit').on('click', function () {
        if (selected < 1) {
            return;
        }
        var payload = {
            stars: selected,
            comment: section.find('#rating-comment').val(),
            csrfmiddlewaretoken: token
        };
        $.post(rateUrl, payload, function (data) {
            $('#rating-average').text(data.average);
            $('#rating-count').text(data.count);
            // The visual stars are a percentage width, same math as the
            // widthratio tag that draws them on first page load
            $('#rating-stars-fill').css('width', (data.average / 5 * 100) + '%');
            section.find('#rating-message').text('Your review was saved.');
        });
    });
});
