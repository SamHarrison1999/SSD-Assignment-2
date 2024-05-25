$('.increase-quantity').click(function(){

    let id = $(this).attr('pid').toString()
    let quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/increase-quantity',
        data: {
            cart_id: id
        },

        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('total').innerText = data.amount
        }
    })
})


$('.decrease-quantity').click(function(){
    let id = $(this).attr('pid').toString()
    let quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/decrease-quantity',
        data: {
            cart_id: id
        },

        success: function(data){
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('total').innerText = data.amount
        }
    })
})


$('.remove-cart').click(function(){

    let id = $(this).attr('pid').toString()

    let to_remove = this.parentNode.parentNode.parentNode.parentNode

    $.ajax({
        type: 'GET',
        url: '/remove-from-cart',
        data: {
            cart_id: id
        },

        success: function(data){
            document.getElementById('total').innerText = data.amount
            to_remove.remove()
        }
    })
})