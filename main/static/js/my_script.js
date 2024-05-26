$('.increase-quantity').click(function(){
    /**
     * Increases the quantity of an item in your cart when the plus button click
     */

    // Get the cart id and quantity
    let id = $(this).attr('pid').toString()
    let quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/increase-quantity',
        data: {
            cart_id: id
        },

        success: function(data){
            /**
             * Update the quantity of the item and price of order in your cart
             */
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('total').innerText = data.amount
        }
    })
})


$('.decrease-quantity').click(function(){
    /**
     * Decrease the quantity of an item in your cart when the minus button clicked
     */

    // Get the cart id and quantity
    let id = $(this).attr('pid').toString()
    let quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/decrease-quantity',
        data: {
            cart_id: id
        },

        success: function(data){
            /**
             * Update the quantity of the item and price of order in your cart
             */
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('total').innerText = data.amount
        }
    })
})


$('.remove-cart').click(function(){
    /**
     * Removing an item from your cart when the remove button is clicked
     */

    // Get the cart id and product to remove from cart
    let id = $(this).attr('pid').toString()

    let to_remove = this.parentNode.parentNode.parentNode.parentNode

    $.ajax({
        type: 'GET',
        url: '/remove-from-cart',
        data: {
            cart_id: id
        },

        success: function(data){
            /**
             * Update the price of order in your cart
             */
            document.getElementById('total').innerText = data.amount
            to_remove.remove()
        }
    })
})