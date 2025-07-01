function clearCart() {
    $.get('/orders/clear-cart').then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body)
        }
    });
}

function changeCartItemCount(itemId, state) {
    $.get('/orders/change-item?item_id=' + itemId + '&state=' + state).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body)
        } else if (res.order_deleted) {
            $('#order-detail-content').html(res.body)
        }
    });
}

function removeCartItem(itemId) {
    $.get('/orders/remove-item?item_id=' + itemId).then(res => {
        if (res.status === 'success' || res.order_deleted) {
            $('#order-detail-content').html(res.body)
        }
    });
}
