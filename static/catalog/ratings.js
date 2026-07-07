$(function () {
    var section = $('#rating-section');
    if (!section.length) {
        return;
    }

    var rateUrl = section.data('rate-url');
    var token = section.find('input[name=csrfmiddlewaretoken]').val();
    var stars = section.find('.star');
    var selected = 0;

    function paint(value) {
        stars.each(function () {
            var icon = $(this).find('i');
            var on = $(this).data('value') <= value;
            icon.toggleClass('bi-star-fill', on).toggleClass('bi-star', !on);
        });
    }

    stars.on('click', function () {
        selected = $(this).data('value');
        paint(selected);
    });

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
            section.find('#rating-message').text('Your review was saved.');
        });
    });
});
