// Cart and wishlist actions, add to cart, change a quantity, remove an
// item, and toggle the wishlist, all run over AJAX instead of a normal form
// submit, so none of them reload the page. Every form below still posts to
// the same Django view used before, this file only stops the browser's own
// submit and does the same POST through jQuery instead, then updates just
// the part of the page that changed

$(function () {
    var cartBadge = $('#cart-badge');

    function updateCartBadge(count) {
        cartBadge.text(count);
        if (count > 0) {
            cartBadge.show();
        } else {
            cartBadge.hide();
        }
    }

    // Reads the message the view sends back with a 400, which is how the
    // stock limit is explained to the shopper.
    function errorFrom(xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
            return xhr.responseJSON.error;
        }
        return 'Something went wrong, please try again.';
    }

    // Add to cart, the button on a product page
    $('.js-cart-add').on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var message = form.find('.js-cart-message');
        $.post(form.attr('action'), form.serialize(), function (data) {
            updateCartBadge(data.cart_count);
            message.removeClass('text-danger').addClass('text-success').text('Added to cart.');
        }).fail(function (xhr) {
            // The view refuses to put more in the cart than the shop has.
            message.removeClass('text-success').addClass('text-danger').text(errorFrom(xhr));
        });
    });

    // Change a quantity on the cart page. Reloading when the cart empties
    // out entirely is the simplest way to show the normal empty cart
    // message without duplicating that markup here in JavaScript
    $('.js-cart-update').on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var row = form.closest('tr');
        $.post(form.attr('action'), form.serialize(), function (data) {
            if (data.cart_count === 0) {
                location.reload();
                return;
            }
            if (data.removed) {
                row.remove();
            } else {
                row.find('.js-line-total').text('$' + data.line_total);
            }
            $('#cart-total').text('$' + data.cart_total);
            updateCartBadge(data.cart_count);
            row.find('.js-row-message').text('');
        }).fail(function (xhr) {
            row.find('.js-row-message').text(errorFrom(xhr));
        });
    });

    // Remove a row on the cart page, same empty cart handling as above
    $('.js-cart-remove').on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var row = form.closest('tr');
        $.post(form.attr('action'), form.serialize(), function (data) {
            if (data.cart_count === 0) {
                location.reload();
                return;
            }
            row.remove();
            $('#cart-total').text('$' + data.cart_total);
            updateCartBadge(data.cart_count);
        });
    });

    // Wishlist toggle. The product page swaps the button in place, the
    // wishlist page removes the whole card instead, since taking something
    // off the wishlist there means it should disappear from the list
    $('.js-wishlist-toggle').on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var mode = form.data('mode');
        $.post(form.attr('action'), form.serialize(), function (data) {
            if (mode === 'remove') {
                var card = form.closest('.js-wishlist-card');
                var wasLastCard = $('.js-wishlist-card').length === 1;
                card.remove();
                if (wasLastCard) {
                    location.reload();
                }
            } else {
                var button = form.find('button');
                if (data.in_wishlist) {
                    button.html('<i class="bi bi-heart-fill"></i> In wishlist');
                } else {
                    button.html('<i class="bi bi-heart"></i> Add to wishlist');
                }
            }
        });
    });
});
