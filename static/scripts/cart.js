function clearCart() {
    $.get('/orders/clear-cart').then(res => {
        if (res.status === 'success') {
            showOrderItemsCount();
            loadCartPartial();
            $('#order-detail-content').html(res.body);
        }
    });
}

function changeCartItemCount(itemId, state) {
    $.get('/orders/change-item?item_id=' + itemId + '&state=' + state).then(res => {
        showOrderItemsCount();
        loadCartPartial();
        $('#order-detail-content').html(res.body);
    });
}

function removeCartItem(itemId) {
    $.get('/orders/remove-item?item_id=' + itemId).then(res => {
        showOrderItemsCount();
        loadCartPartial();
        $('#order-detail-content').html(res.body);
    });
}
